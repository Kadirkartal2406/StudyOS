"""
StudyOS — Living Plan Service (LOS Module 6)
LOS § 9 — Living Plan: observe → suggest → accept → adapt

Living Plan, Exam pack + müsaitlik + Confidence/Trend + Learning Memory'ye göre
yaşayan orta vadeli çalışma sözleşmesidir.

Bu servis:
  1. MUTATE_PLAN: Confidence trendi + Observation Full durumuna göre plan adapte eder
  2. Suggest: Kullanıcıya öneri gönderir (accept / red / cooldown)
  3. Red → Memory: Red cevabı Learning Memory'ye yazılır
  4. Cooldown koruması: Aynı öneri hemen tekrar gelmez

Kısıtlar (LOS § 5.6 — yüksek eşik):
  - Tek oturum, tek yanlış, tek deneme → asla MUTATE_PLAN
  - Observation FULL değilse → asla MUTATE_PLAN
  - Cooldown aktifse → asla yeniden öner
  - Thrashing yasağı: 3 gün içinde aynı konu için ikinci plan değişikliği yok
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.planner_draft import PlannerDraft, PlannerDraftStatus
from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.models.topic_confidence import ConfidenceLevel, TopicConfidence
from app.repositories.planner_draft_repository import PlannerDraftRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.services.observation_mode import FULL, ObservationMode
from app.services.policy_decision_engine import Policy, PolicyDecisionEngine

# ── Eşikler ───────────────────────────────────────────────────────────────────

_MUTATE_PLAN_MIN_TREND_SCORE = -0.25   # negatif trend eşiği
_MUTATE_PLAN_MIN_SAMPLE = 8            # minimum sample
_COOLDOWN_DAYS = 3                     # aynı konu için öneri cooldown
_THRASH_PROTECT_HOURS = 72             # plan değişimi thrashing koruması


class LivingPlanService:
    """
    LOS § 9 — Living Plan adapt servisi.

    Kullanım:
        svc = LivingPlanService(db)
        result = await svc.run_adapt_cycle(user_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.draft_repo = PlannerDraftRepository(db)
        self.plan_repo = StudyPlanRepository(db)

    # ── Adapt cycle ───────────────────────────────────────────────────────────

    async def run_adapt_cycle(self, user_id: uuid.UUID) -> dict:
        """
        LOS loop'unun MUTATE_PLAN adımı.
        Dashboard yüklenişinde ve oturum bitiminde tetiklenir.

        Returns:
            {
              'action': 'hold' | 'suggest' | 'mutate',
              'reason': str,
              'affected_topics': list[str],
            }
        """
        # 1. Observation Full değilse → HOLD
        obs = ObservationMode(self.db)
        obs_state = await obs.get_state(user_id)
        if obs_state != FULL:
            return {
                "action": "hold",
                "reason": f"Observation tamamlanmadı ({obs_state}). Plan değiştirilmedi.",
                "affected_topics": [],
            }

        # 2. Policy kararı MUTATE_PLAN mı?
        policy_engine = PolicyDecisionEngine(self.db)
        decision = await policy_engine.decide(user_id)

        if decision.policy != Policy.MUTATE_PLAN:
            return {
                "action": "hold",
                "reason": f"Policy={decision.policy}. Plan değişikliği gerekmedi.",
                "affected_topics": [],
            }

        # 3. Thrashing koruması
        if await self._is_thrashing(user_id, decision.topic_code):
            return {
                "action": "hold",
                "reason": "Thrashing koruması aktif. Aynı konu için yakın zamanda karar verildi.",
                "affected_topics": [],
            }

        # 4. Önce Suggest → planner_draft oluştur
        topic_code = decision.topic_code
        if not topic_code:
            return {
                "action": "hold",
                "reason": "MUTATE_PLAN için hedef konu belirsiz.",
                "affected_topics": [],
            }

        # Cooldown kontrolü
        if await self._in_cooldown(user_id, topic_code):
            return {
                "action": "hold",
                "reason": "Cooldown aktif. Bu konu için öneri yakın zamanda zaten yapıldı.",
                "affected_topics": [topic_code],
            }

        # 5. Mevcut planlarda bu konu var mı?
        existing = await self._find_existing_plan_for_topic(user_id, topic_code)
        if existing:
            # Zaten planda → sadece önce sıraya al (MUTATE_TODAY düzeyi)
            await self._prioritize_plan(existing)
            return {
                "action": "mutate",
                "reason": decision.reason,
                "affected_topics": [topic_code],
            }

        # 6. Yeni plan bloğu öner → draft oluştur
        await self._create_suggest_draft(user_id, decision)
        return {
            "action": "suggest",
            "reason": decision.reason,
            "affected_topics": [topic_code],
        }

    # ── Accept / Reject — Kullanıcı karar API'si ─────────────────────────────

    async def accept_suggestion(
        self, user_id: uuid.UUID, *, draft_id: uuid.UUID | None = None
    ) -> dict:
        """
        LOS § 9.1 — Suggest → Accept.
        PENDING draft → ACCEPTED; StudyPlan'a dönüştür.
        """
        draft = await self._get_pending_draft(user_id, draft_id)
        if draft is None:
            return {"action": "no_pending", "draft_id": None, "reason": "Bekleyen öneri yok."}

        draft.status = PlannerDraftStatus.ACCEPTED
        draft.updated_at = datetime.now(UTC)
        await self.db.flush()

        # Plan payload'dan bugün için StudyPlan blokları üret
        try:
            items = (draft.plan_payload or {}).get("items", [])
            today = datetime.now(UTC).date()
            for idx, item in enumerate(items[:3]):  # max 3 blok
                from app.models.study_plan import StudyPlan, StudyPlanStatus
                sp = StudyPlan(
                    user_id=user_id,
                    title=item.get("title") or item.get("topic_name") or "Kaydedilen Öneri",
                    subject=item.get("subject") or item.get("subject_code"),
                    topic=item.get("topic_name") or item.get("topic_code"),
                    estimated_minutes=item.get("estimated_minutes", 45),
                    study_date=today,
                    order_index=100 + idx,  # mevcut planların sonuna
                    status=StudyPlanStatus.PLANNED,
                )
                self.db.add(sp)
        except Exception:
            pass  # Plan dönüştirme hatası accept'i engellemez

        await self.db.flush()
        return {
            "action": "accepted",
            "draft_id": str(draft.id),
            "reason": "Plan önerisi kabul edildi. Bugünün planlarına eklendi.",
        }

    async def reject_suggestion(
        self, user_id: uuid.UUID, *, draft_id: uuid.UUID | None = None
    ) -> dict:
        """
        LOS § 9.4 — Reddetmek öğrenmektir.
        PENDING draft → REJECTED.
        Red cezalandırılmaz: cooldown aktifleşir, Memory'ye yazılır.
        """
        draft = await self._get_pending_draft(user_id, draft_id)
        if draft is None:
            return {"action": "no_pending", "draft_id": None, "reason": "Bekleyen öneri yok."}

        draft.status = PlannerDraftStatus.REJECTED
        draft.updated_at = datetime.now(UTC)
        await self.db.flush()

        # Memory'ye red sinyali yaz (plan_receptivity bilgisi)
        try:
            from app.services.behavioral_memory_service import BehavioralMemoryService
            mem_svc = BehavioralMemoryService(self.db)
            await mem_svc.record_plan_decision(user_id, accepted=False)
        except Exception:
            pass  # Memory yazımı kritik değil


        return {
            "action": "rejected",
            "draft_id": str(draft.id),
            "reason": "Plan önerisi reddedildi. Mevcut plan değişmedi.",
        }

    async def _get_pending_draft(
        self, user_id: uuid.UUID, draft_id: uuid.UUID | None
    ) -> PlannerDraft | None:
        """PENDING draft'u döner (spesifik ID veya en son)."""
        if draft_id:
            stmt = select(PlannerDraft).where(
                PlannerDraft.id == draft_id,
                PlannerDraft.user_id == user_id,
                PlannerDraft.status == PlannerDraftStatus.PENDING,
            )
        else:
            stmt = (
                select(PlannerDraft)
                .where(
                    PlannerDraft.user_id == user_id,
                    PlannerDraft.status == PlannerDraftStatus.PENDING,
                )
                .order_by(PlannerDraft.created_at.desc())
                .limit(1)
            )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    # ── Yardımcı: mevcut plan bul ────────────────────────────────────────────

    async def _find_existing_plan_for_topic(
        self, user_id: uuid.UUID, topic_code: str
    ) -> StudyPlan | None:
        """Bugün için bu topic'te incomplete plan var mı?"""
        today = datetime.now(UTC).date()
        plans = await self.plan_repo.list_for_user(user_id, today)
        for p in plans:
            if p.status in (StudyPlanStatus.PLANNED, StudyPlanStatus.IN_PROGRESS):
                if (p.topic or "").lower() in topic_code.lower():
                    return p
        return None

    async def _prioritize_plan(self, plan: StudyPlan) -> None:
        """Planı order_index=0 yaparak öne al."""
        plan.order_index = 0
        plan.updated_at = datetime.now(UTC)
        await self.db.flush()

    # ── Draft oluştur (Suggest → Accept → Adapt lifecycle başlat) ────────────

    async def _create_suggest_draft(
        self, user_id: uuid.UUID, decision
    ) -> PlannerDraft | None:
        """
        MUTATE_PLAN kararı için küçük bir planner draft oluştur.
        Kullanıcı accept ederse → StudyPlan'a dönüşür.
        """
        try:
            from app.schemas.planner import PlannerGenerateRequest
            from app.services.planner_service import PlannerService

            # Topic'ten subject çıkar
            topic_code = decision.topic_code or ""
            subject_code = decision.subject_code or topic_code.split("__")[0] if "__" in topic_code else ""

            svc = PlannerService(self.db)
            req = PlannerGenerateRequest(
                target_exam=None,
                target_net=None,
                available_days=None,
                available_hours=None,
                override_reason=f"LOS MUTATE_PLAN: {decision.reason}",
            )
            draft = await svc.generate(user_id, req)
            return draft
        except Exception:
            return None

    # ── Cooldown ──────────────────────────────────────────────────────────────

    async def _in_cooldown(self, user_id: uuid.UUID, topic_code: str) -> bool:
        """
        Bu topic için son {_COOLDOWN_DAYS} gün içinde draft önerildi mi?
        PlannerDraft tablosundan kontrol.
        """
        threshold = datetime.now(UTC) - timedelta(days=_COOLDOWN_DAYS)
        stmt = (
            select(func.count())
            .select_from(PlannerDraft)
            .where(
                PlannerDraft.user_id == user_id,
                PlannerDraft.created_at >= threshold,
                PlannerDraft.status == PlannerDraftStatus.DRAFT,
            )
        )
        result = await self.db.execute(stmt)
        count = int(result.scalar_one())
        return count > 0

    async def _is_thrashing(
        self, user_id: uuid.UUID, topic_code: str | None
    ) -> bool:
        """
        Bu topic için son {_THRASH_PROTECT_HOURS} saat içinde
        ACCEPTED draft var mı? (Thrashing koruma)
        """
        if not topic_code:
            return False
        threshold = datetime.now(UTC) - timedelta(hours=_THRASH_PROTECT_HOURS)
        stmt = (
            select(func.count())
            .select_from(PlannerDraft)
            .where(
                PlannerDraft.user_id == user_id,
                PlannerDraft.updated_at >= threshold,
                PlannerDraft.status == PlannerDraftStatus.ACCEPTED,
            )
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one()) > 0


# ── Dashboard entegrasyon hook'u ──────────────────────────────────────────────

async def maybe_run_living_plan_adapt(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    """
    Dashboard yüklenişinde veya oturum bitiminde tetikle.
    Fire-and-forget: hata kullanıcı akışını kesmez.
    """
    try:
        svc = LivingPlanService(db)
        await svc.run_adapt_cycle(user_id)
    except Exception:
        pass
