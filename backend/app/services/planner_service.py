"""
StudyOS — Planner Service
Sprint-2.7 — generate / accept (G3) / explain (P1)
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.activity import ActivityEventType
from app.models.planner_draft import PlannerDraft, PlannerDraftStatus
from app.models.question_record import ExamType
from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.repositories.planner_draft_repository import PlannerDraftRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.schemas.planner import (
    DashboardPlannerSummary,
    PlannerAcceptConflict,
    PlannerAcceptRequest,
    PlannerAcceptResponse,
    PlannerConflictDay,
    PlannerDraftRead,
    PlannerExplainResponse,
    PlannerGenerateRequest,
    PlannerItemRead,
)
from app.schemas.study_plan import StudyPlanRead
from app.services.activity_service import ActivityService
from app.services.ai.adaptive_planner_engine import AdaptivePlannerEngine
from app.services.notification_settings_service import NotificationSettingsService


class PlannerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PlannerDraftRepository(db)
        self.plans = StudyPlanRepository(db)
        self.engine = AdaptivePlannerEngine(db)
        self.activity = ActivityService(db)
        self.notif = NotificationSettingsService(db)

    async def _resolve_generate_request(
        self, user_id: uuid.UUID, data: PlannerGenerateRequest
    ) -> PlannerGenerateRequest:
        """F1 — eksik alanları Learning Profile'dan doldur."""
        from app.services.learning_profile_service import LearningProfileService

        defaults = await LearningProfileService(self.db).planner_defaults(user_id)
        target_exam = data.target_exam
        target_net = data.target_net
        available_days = data.available_days
        available_hours = data.available_hours

        if defaults:
            if target_exam is None:
                target_exam = ExamType(defaults["target_exam"])
            if target_net is None:
                target_net = float(defaults["target_net"])
            if available_days is None:
                available_days = list(defaults["available_days"])
            if available_hours is None:
                available_hours = float(defaults["available_hours"])

        if target_exam is None or target_net is None or not available_days or available_hours is None:
            raise ValidationError(
                "Plan için target_exam, target_net, available_days ve available_hours gerekli "
                "(veya Learning Profile tamamlanmalı)"
            )
        return PlannerGenerateRequest(
            target_exam=target_exam,
            target_net=target_net,
            available_days=available_days,
            available_hours=available_hours,
        )

    def _to_read(self, draft: PlannerDraft) -> PlannerDraftRead:
        payload = dict(draft.plan_payload or {})
        raw_items = payload.get("items") or []
        items: list[PlannerItemRead] = []
        for it in raw_items:
            items.append(
                PlannerItemRead(
                    study_date=date.fromisoformat(it["study_date"]),
                    title=it["title"],
                    subject=it["subject"],
                    topic=it.get("topic"),
                    target_question_count=int(it["target_question_count"]),
                    estimated_minutes=int(it["estimated_minutes"]),
                    start_time=it.get("start_time"),
                    end_time=it.get("end_time"),
                    resource_ids=list(it.get("resource_ids") or []),
                    resource_titles=list(it.get("resource_titles") or []),
                    reason=str(it.get("reason") or ""),
                )
            )
        return PlannerDraftRead(
            id=draft.id,
            user_id=draft.user_id,
            status=draft.status,
            target_exam=ExamType(draft.target_exam),
            target_net=float(draft.target_net),
            available_days=list(draft.available_days or []),
            available_hours=float(draft.available_hours),
            items=items,
            summary=dict(payload.get("summary") or {}),
            rationale=dict(payload.get("rationale") or {}),
            created_at=draft.created_at,
            accepted_at=draft.accepted_at,
        )

    async def generate(
        self, user_id: uuid.UUID, data: PlannerGenerateRequest
    ) -> PlannerDraftRead:
        data = await self._resolve_generate_request(user_id, data)
        payload = await self.engine.generate(user_id, data)
        draft = PlannerDraft(
            user_id=user_id,
            status=PlannerDraftStatus.DRAFT,
            target_exam=str(data.target_exam),
            target_net=float(data.target_net),
            available_days=list(data.available_days),
            available_hours=float(data.available_hours),
            plan_payload=payload,
        )
        draft = await self.repo.add(draft)
        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.PLANNER_GENERATED,
            title="Adaptive plan oluşturuldu",
            description=payload.get("rationale", {}).get("overview"),
            metadata={
                "planner_draft_id": str(draft.id),
                "target_exam": str(data.target_exam),
                "target_net": float(data.target_net),
                "item_count": len(payload.get("items") or []),
            },
        )
        from app.schemas.achievement import AchievementCheckRequest
        from app.services.achievement_service import AchievementService

        await AchievementService(self.db).check(
            user_id, AchievementCheckRequest(event="planner_generated")
        )
        return self._to_read(draft)

    async def get_draft(self, draft_id: uuid.UUID, user_id: uuid.UUID) -> PlannerDraftRead:
        draft = await self.repo.get_for_user(draft_id, user_id)
        if draft is None:
            raise NotFoundError("Planner taslağı", str(draft_id))
        return self._to_read(draft)

    async def _conflicts_for_draft(
        self, user_id: uuid.UUID, draft: PlannerDraft
    ) -> list[PlannerConflictDay]:
        payload = dict(draft.plan_payload or {})
        dates = {it["study_date"] for it in (payload.get("items") or [])}
        conflicts: list[PlannerConflictDay] = []
        for ds in sorted(dates):
            d = date.fromisoformat(ds)
            existing = await self.plans.list_for_user(user_id, d)
            if existing:
                conflicts.append(
                    PlannerConflictDay(
                        study_date=d,
                        existing_plan_count=len(existing),
                        existing_titles=[p.title for p in existing[:5]],
                    )
                )
        return conflicts

    async def accept(
        self,
        draft_id: uuid.UUID,
        user_id: uuid.UUID,
        data: PlannerAcceptRequest,
    ) -> PlannerAcceptResponse:
        draft = await self.repo.get_for_user(draft_id, user_id)
        if draft is None:
            raise NotFoundError("Planner taslağı", str(draft_id))
        if draft.status == PlannerDraftStatus.ACCEPTED:
            raise ValidationError("Bu taslak zaten kabul edilmiş")
        if draft.status == PlannerDraftStatus.DISCARDED:
            raise ValidationError("Bu taslak iptal edilmiş")

        conflicts = await self._conflicts_for_draft(user_id, draft)
        if conflicts and not data.force:
            raise ConflictError(
                "Seçilen günlerde mevcut planlar var",
                details={
                    "draft_id": str(draft_id),
                    "conflicts": [c.model_dump(mode="json") for c in conflicts],
                    "hint": "force=true ile yanına ekleyebilirsin",
                },
            )

        created: list[StudyPlan] = []
        payload = dict(draft.plan_payload or {})
        for it in payload.get("items") or []:
            study_date = date.fromisoformat(it["study_date"])
            order = await self.plans.next_order_index(user_id, study_date)
            start_t = None
            end_t = None
            try:
                from datetime import time as dtime

                if it.get("start_time"):
                    sh, sm = str(it["start_time"]).split(":")[:2]
                    start_t = dtime(int(sh), int(sm))
                if it.get("end_time"):
                    eh, em = str(it["end_time"]).split(":")[:2]
                    end_t = dtime(int(eh), int(em))
            except Exception:
                start_t = None
                end_t = None
            plan = StudyPlan(
                user_id=user_id,
                title=it["title"],
                subject=it["subject"],
                topic=it.get("topic"),
                target_question_count=int(it["target_question_count"]),
                estimated_minutes=int(it["estimated_minutes"]),
                planned_start_time=start_t,
                planned_end_time=end_t,
                study_date=study_date,
                order_index=order,
                status=StudyPlanStatus.PLANNED,
                source="planner",
                planner_draft_id=draft.id,
            )
            created.append(await self.plans.add(plan))

        draft.status = PlannerDraftStatus.ACCEPTED
        draft.accepted_at = datetime.now(UTC)
        draft.updated_at = datetime.now(UTC)
        await self.db.flush()

        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.PLANNER_ACCEPTED,
            title="Adaptive plan kabul edildi",
            description=f"{len(created)} çalışma planı oluşturuldu",
            metadata={
                "planner_draft_id": str(draft.id),
                "created_plan_ids": [str(p.id) for p in created],
                "forced": data.force,
            },
        )
        from app.schemas.achievement import AchievementCheckRequest
        from app.services.achievement_service import AchievementService

        await AchievementService(self.db).check(
            user_id, AchievementCheckRequest(event="planner_accepted")
        )
        return PlannerAcceptResponse(
            draft=self._to_read(draft),
            created_plans=[StudyPlanRead.model_validate(p) for p in created],
        )

    async def explain(
        self, draft_id: uuid.UUID, user_id: uuid.UUID
    ) -> PlannerExplainResponse:
        draft = await self.repo.get_for_user(draft_id, user_id)
        if draft is None:
            raise NotFoundError("Planner taslağı", str(draft_id))
        read = self._to_read(draft)
        item_reasons = [
            {"subject": i.subject, "date": str(i.study_date), "reason": i.reason}
            for i in read.items
        ]
        overview = str((read.rationale or {}).get("overview") or "")
        bullets = "\n".join(f"- {i.subject} ({i.study_date}): {i.reason}" for i in read.items[:12])
        system = (
            "Sen StudyOS çalışma koçusun. Planı sen üretmedin; kural motoru üretti. "
            "Sana verilen gerekçeleri (reason) doğal Türkçe ile açıkla. "
            "Yeni plan önerme, sayıları uydurma."
        )
        user_msg = (
            f"Hedef: {read.target_exam} {read.target_net} net.\n"
            f"Özet gerekçe: {overview}\n"
            f"Madde gerekçeleri:\n{bullets}\n"
            "Öğrenciye neden bu planın önerildiğini 2–4 kısa paragrafta anlat."
        )
        pref = await self.notif.get_or_create(user_id)
        result = await generate_with_fallback(
            GenerateRequest(
                messages=[
                    ChatMessageDTO(role="system", content=system),
                    ChatMessageDTO(role="user", content=user_msg),
                ],
                context={"planner_draft_id": str(draft.id)},
            ),
            preferred=pref.ai_preferred_provider,
            model=pref.ai_preferred_model,
        )
        return PlannerExplainResponse(
            draft_id=draft.id,
            explanation=result.text,
            provider=result.provider,
            used_fallback=result.used_fallback,
            rationale=read.rationale,
            item_reasons=item_reasons,
        )

    # ── Sprint 9: Living Plan önerileri ──────────────────────────────────────

    async def list_pending(self, user_id: uuid.UUID) -> list[PlannerDraftRead]:
        """Sistemin ürettiği ve henüz yanıtlanmamış plan önerileri."""
        from sqlalchemy import select as _sel
        from app.models.planner_draft import PlannerDraft
        rows = await self.db.execute(
            _sel(PlannerDraft).where(
                PlannerDraft.user_id == user_id,
                PlannerDraft.status == PlannerDraftStatus.DRAFT,
            ).order_by(PlannerDraft.created_at.desc()).limit(5)
        )
        drafts = rows.scalars().all()
        return [self._to_read(d) for d in drafts]

    async def reject(self, draft_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Öneriyi reddet — cooldown metadata'ya yazılır."""
        from datetime import UTC, datetime, timedelta
        draft = await self.repo.get_for_user(draft_id, user_id)
        if draft is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Planner taslağı", str(draft_id))
        draft.status = PlannerDraftStatus.REJECTED
        meta = dict(draft.metadata_ or {})
        meta["rejected_at"] = datetime.now(UTC).isoformat()
        meta["cooldown_until"] = (datetime.now(UTC) + timedelta(days=3)).isoformat()
        draft.metadata_ = meta
        await self.db.flush()

    # ── Sprint-9: Living Plan Suggestion endpoints ────────────────────────────

    async def list_pending_suggestions(self, user_id: uuid.UUID) -> list[PlannerDraftRead]:
        """Return planner drafts with status='pending' for the current user."""
        drafts = await self.repo.list_pending(user_id)
        return [self._to_read(d) for d in drafts]

    async def accept_suggestion(
        self, user_id: uuid.UUID, draft_id: uuid.UUID
    ) -> PlannerAcceptResponse:
        """Accept a Living Plan suggestion (DRAFT or PENDING) → create study plans."""
        draft = await self.repo.get_for_user(draft_id, user_id)
        if draft is None:
            raise NotFoundError("Planner taslağı", str(draft_id))
        if draft.status not in (PlannerDraftStatus.PENDING, PlannerDraftStatus.DRAFT):
            raise ValidationError("Bu öneri kabul için uygun değil")

        created: list[StudyPlan] = []
        payload = dict(draft.plan_payload or {})
        for it in payload.get("items") or []:
            study_date = date.fromisoformat(it["study_date"])
            order = await self.plans.next_order_index(user_id, study_date)
            plan = StudyPlan(
                user_id=user_id,
                title=it["title"],
                subject=it["subject"],
                topic=it.get("topic"),
                target_question_count=int(it["target_question_count"]),
                estimated_minutes=int(it["estimated_minutes"]),
                study_date=study_date,
                order_index=order,
                status=StudyPlanStatus.PLANNED,
                source="living_plan",
                planner_draft_id=draft.id,
            )
            created.append(await self.plans.add(plan))

        draft.status = PlannerDraftStatus.ACCEPTED
        draft.accepted_at = datetime.now(UTC)
        draft.updated_at = datetime.now(UTC)
        await self.db.flush()

        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.PLANNER_ACCEPTED,
            title="Yaşayan plan önerisi kabul edildi",
            description=f"{len(created)} çalışma planı oluşturuldu",
            metadata={
                "planner_draft_id": str(draft.id),
                "created_plan_ids": [str(p.id) for p in created],
                "source": "living_plan",
            },
        )
        # Sprint 9 — receptivity Memory güncelle
        try:
            from app.services.behavioral_memory_service import BehavioralMemoryService
            await BehavioralMemoryService(self.db).record_plan_decision(
                user_id, accepted=True
            )
        except Exception:
            pass
        return PlannerAcceptResponse(
            draft=self._to_read(draft),
            created_plans=[StudyPlanRead.model_validate(p) for p in created],
        )

    async def reject_suggestion(
        self, user_id: uuid.UUID, draft_id: uuid.UUID
    ) -> PlannerDraftRead:
        """Reject a Living Plan suggestion → cooldown + receptivity Memory."""
        draft = await self.repo.get_for_user(draft_id, user_id)
        if draft is None:
            raise NotFoundError("Planner taslağı", str(draft_id))
        if draft.status not in (PlannerDraftStatus.PENDING, PlannerDraftStatus.DRAFT):
            raise ValidationError("Bu öneri zaten işlem gördü")

        now = datetime.now(UTC)
        meta = dict(draft.plan_payload or {})
        meta["rejected_at"] = now.isoformat()
        meta["cooldown_until"] = (now + timedelta(days=3)).isoformat()
        draft.plan_payload = meta
        draft.status = PlannerDraftStatus.REJECTED
        draft.updated_at = now
        await self.db.flush()

        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.PLANNER_GENERATED,
            title="Yaşayan plan önerisi reddedildi",
            description="Cooldownğlam Memory'ye yazıldı; cooldown aktif",
            metadata={"planner_draft_id": str(draft.id), "source": "living_plan"},
        )
        try:
            from app.services.behavioral_memory_service import BehavioralMemoryService
            await BehavioralMemoryService(self.db).record_plan_decision(
                user_id, accepted=False
            )
        except Exception:
            pass
        return self._to_read(draft)

    async def dashboard_summary(self, user_id: uuid.UUID) -> DashboardPlannerSummary:
        draft = await self.repo.latest_draft(user_id, status=PlannerDraftStatus.DRAFT)
        if draft is None:
            draft = await self.repo.latest_draft(user_id)
        if draft is None:
            return DashboardPlannerSummary()
        read = self._to_read(draft)
        overview = str((read.rationale or {}).get("overview") or None)
        return DashboardPlannerSummary(
            draft_id=draft.id,
            status=str(draft.status),
            target_exam=str(draft.target_exam),
            target_net=float(draft.target_net),
            item_count=len(read.items),
            overview_reason=overview,
            created_at=draft.created_at,
        )
