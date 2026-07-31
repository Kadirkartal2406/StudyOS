"""
StudyOS — AI Coach Service (LOS Hizalama)

LOS § 5 — RuleEngine karar verir; LLM açıklar.

DEĞİŞTİRİLDİ (Alignment Sprint):
  Hardcoded recommended_topics / recommended_question_count / insights kaldırıldı.
  Tüm öneriler PolicyDecisionEngine + TopicConfidence + ActivityService'ten gelir.
  AI Coach artık EXPLAIN_ONLY katmanındadır; karar vermez.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_confidence import ConfidenceLevel, TopicConfidence
from app.models.user import User
from app.services.learning_profile_service import LearningProfileService
from app.services.policy_decision_engine import Policy, PolicyDecisionEngine


class AICoachDailyRead(BaseModel):
    greeting: str
    target_exam: str
    goal_progress_pct: float
    badge: str
    insights: list[str]
    recommended_question_count: int
    recommended_topics: list[str]
    # LOS Alignment — karar kaynağı bilgisi (Explain katmanı için)
    policy: str = "HOLD_OBS"
    policy_topic_code: str | None = None
    policy_reason: str | None = None
    confidence_level: str | None = None


class AICoachService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_svc = LearningProfileService(db)

    async def get_daily_coaching(self, user_id: uuid.UUID) -> AICoachDailyRead:
        user = await self.db.get(User, user_id)
        name = (user.first_name if user else "") or "Öğrenci"

        exam, _, _ = await self.profile_svc.resolve_active_scope(user_id)
        exam = (exam or "kpss").upper()

        # ── 1. Policy kararını al (RuleEngine) ───────────────────────────────
        policy_engine = PolicyDecisionEngine(self.db)
        try:
            decision = await policy_engine.decide(user_id)
        except Exception:
            from app.services.policy_decision_engine import DecisionResult, Policy
            decision = DecisionResult(
                policy=Policy.HOLD_OBS,
                reason="Henüz yeterli gözlem yok.",
            )

        # ── 2. Confidence verisi — en zayıf topic'ler ────────────────────────
        low_confidence_topics = await self._get_low_confidence_topics(user_id, limit=3)
        topic_names = [_format_topic_name(t.topic_code) for t in low_confidence_topics]

        # ── 3. Son 7 günlük soru aktivitesinden gerçek soru sayısı öner ──────
        recommended_q = await self._suggest_question_count(user_id)

        # ── 4. Hedef ilerleme (Assessment tablosu kaldırıldı; basit confidence avg) ──
        progress_pct, badge = await self._compute_progress(user_id, low_confidence_topics)

        # ── 5. Insight'ları Evidence + Policy'den üret (hardcoded yok) ────────
        insights = _build_insights(
            policy=decision.policy,
            policy_reason=decision.reason,
            topic_code=decision.topic_code,
            low_confidence_topics=low_confidence_topics,
            progress_pct=progress_pct,
        )

        return AICoachDailyRead(
            greeting=f"Merhaba {name}!",
            target_exam=exam,
            goal_progress_pct=progress_pct,
            badge=badge,
            insights=insights,
            recommended_question_count=recommended_q,
            recommended_topics=topic_names,
            policy=str(decision.policy),
            policy_topic_code=decision.topic_code,
            policy_reason=decision.reason,
            confidence_level=decision.confidence_level,
        )

    # ── Yardımcı: düşük confidence topic'ler ─────────────────────────────────

    async def _get_low_confidence_topics(
        self, user_id: uuid.UUID, limit: int = 3
    ) -> list[TopicConfidence]:
        """
        TopicConfidence tablosundan kullanıcının en düşük inanç seviyeli
        topic'lerini döner. Önce LOW, sonra MEDIUM ve UNKNOWN.
        LOS §4.5: low inanç + düşük belirsizlik = tamir adayı.
        """
        stmt = (
            select(TopicConfidence)
            .where(TopicConfidence.user_id == user_id)
            .order_by(
                TopicConfidence.belief.asc(),
                TopicConfidence.uncertainty.desc(),
            )
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _suggest_question_count(self, user_id: uuid.UUID) -> int:
        """
        Son 7 günlük ortalama günlük soru çözme × 1.1 artış hedefi.
        Veri yoksa konservatif varsayılan: 20.
        """
        try:
            from app.models.question_record import QuestionRecord

            seven_days_ago = datetime.now(UTC) - timedelta(days=7)
            stmt = select(QuestionRecord).where(
                QuestionRecord.user_id == user_id,
                QuestionRecord.created_at >= seven_days_ago,
            )
            result = await self.db.execute(stmt)
            records = result.scalars().all()
            if not records:
                return 20
            avg_daily = len(records) / 7.0
            suggested = max(10, int(avg_daily * 1.1))
            return min(suggested, 60)  # üst cap
        except Exception:
            return 20

    async def _compute_progress(
        self, user_id: uuid.UUID, confidence_rows: list[TopicConfidence]
    ) -> tuple[float, str]:
        """
        Kullanıcının ortalama Confidence belief'ini ilerleme yüzdesi olarak yorumla.
        Veri yoksa 0.
        """
        if not confidence_rows:
            # Hiç confidence kaydı yoksa profil hedefini kontrol et
            try:
                targets = await self.profile_svc.repo.list_exam_targets(user_id)
                if not targets:
                    return 0.0, "🌱 Başlangıç"
            except Exception:
                pass
            return 0.0, "🌱 Başlangıç"

        avg_belief = sum(r.belief for r in confidence_rows) / len(confidence_rows)
        progress_pct = round(avg_belief * 100.0, 1)

        if progress_pct >= 80:
            badge = "🥇 Yüksek Güven"
        elif progress_pct >= 60:
            badge = "🥈 Orta Güven"
        elif progress_pct >= 35:
            badge = "🥉 Gelişiyor"
        else:
            badge = "🌱 Başlangıç"

        return progress_pct, badge


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def _format_topic_name(topic_code: str) -> str:
    """topic_code → okunabilir ad (örn. 'mat__turevler' → 'Türevler')."""
    parts = topic_code.split("__")
    name = parts[-1] if parts else topic_code
    return name.replace("_", " ").title()


def _build_insights(
    *,
    policy: Policy,
    policy_reason: str,
    topic_code: str | None,
    low_confidence_topics: list[TopicConfidence],
    progress_pct: float,
) -> list[str]:
    """
    LOS §7 (RuleEngine karar verir; LLM açıklar) prensibine uygun:
    Insights, hardcoded değil — Policy + Confidence sonuçlarından üretilir.
    """
    insights: list[str] = []

    # Policy mesajı — RuleEngine kararının Explain katmanı
    if policy == Policy.HOLD_OBS:
        insights.append("Sistem seni daha iyi tanımak için gözlemlemeye devam ediyor. Çalışmaya devam et!")
    elif policy == Policy.SUGGEST:
        topic_display = _format_topic_name(topic_code) if topic_code else "bir konu"
        insights.append(f"Sistem bir öneri hazırladı: {topic_display} konusuna odaklanmayı değerlendir.")
    elif policy in (Policy.MUTATE_TODAY, Policy.MUTATE_PLAN):
        insights.append(f"Sistem bugünkü planını güncelledi. {policy_reason}")
    elif policy == Policy.EXPLAIN_ONLY:
        insights.append(policy_reason)

    # Confidence tabanlı insight
    if low_confidence_topics:
        weakest = low_confidence_topics[0]
        if weakest.confidence_level == ConfidenceLevel.LOW:
            insights.append(
                f"'{_format_topic_name(weakest.topic_code)}' konusunda inanç düşük "
                f"(belief={weakest.belief:.0%}). Bu konuya öncelik ver."
            )
        elif weakest.confidence_level == ConfidenceLevel.UNKNOWN:
            insights.append(
                f"'{_format_topic_name(weakest.topic_code)}' konusunda henüz yeterli "
                "çalışma verisi yok. Birkaç soru çöz."
            )
        elif weakest.confidence_level == ConfidenceLevel.CONFLICTED:
            insights.append(
                f"'{_format_topic_name(weakest.topic_code)}' konusunda çelişkili sonuçlar var. "
                "Farklı türde soru dene."
            )

    # Genel ilerleme
    if progress_pct >= 70:
        insights.append("Genel güven seviyeniz iyi görünüyor. Tekrar sıklığını koru.")
    elif progress_pct > 0:
        insights.append(f"Genel güven ortalamanız %{progress_pct:.0f}. Düzenli çalışma artıracak.")

    return insights[:4]  # dashboard için maksimum 4 insight
