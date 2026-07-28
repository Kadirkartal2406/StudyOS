"""
StudyOS — Policy Decision Engine (LOS Module 4)
LOS § 5 — RuleEngine → Policy.

ANAHTAR PRENSIP (LOS § 1.3):
  LLM bu soruların hiçbirine KARAR VERMEZ.
  RuleEngine karar verir; LLM yalnızca mevcut kararın NEDENİNİ açıklar.

Policy sözlüğü (LOS § 2):
  HOLD_OBS       — Dokunma; gözlemle (evidence yetersiz, gürültü, cooldown)
  SUGGEST        — Öneri; kullanıcı kabul/ertele/red edebilir
  MUTATE_TODAY   — Bugünün Next Action / sırasını güncelle (düşük-orta eşik)
  MUTATE_PLAN    — Living Plan güncelle (yüksek eşik)
  EXPLAIN_ONLY   — Yeni karar yok; mevcut durumun dil açıklaması

Thrashing koruması:
  Aynı karar 72 saat içinde tekrar verilmez.
  Red sonrası cooldown: 3 gün.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_confidence import ConfidenceLevel, TopicConfidence
from app.services.observation_mode import (
    FULL,
    OBSERVING,
    ObservationMode,
)

# ── Policy enum ───────────────────────────────────────────────────────────────


class Policy(StrEnum):
    HOLD_OBS = "HOLD_OBS"
    SUGGEST = "SUGGEST"
    MUTATE_TODAY = "MUTATE_TODAY"
    MUTATE_PLAN = "MUTATE_PLAN"
    EXPLAIN_ONLY = "EXPLAIN_ONLY"


# ── Eşikler ───────────────────────────────────────────────────────────────────

# MUTATE_TODAY için minimum performance sample
_MIN_SAMPLE_MUTATE_TODAY = 3
# MUTATE_PLAN için daha yüksek eşik
_MIN_SAMPLE_MUTATE_PLAN = 8
# Thrashing cooldown (saat)
_THRASHING_COOLDOWN_HOURS = 72
# Red sonrası cooldown (gün)
_REJECTION_COOLDOWN_DAYS = 3


class DecisionResult:
    """Tek bir Decision Engine çıktısı."""

    def __init__(
        self,
        policy: Policy,
        *,
        reason: str,
        topic_code: str | None = None,
        subject_code: str | None = None,
        confidence_level: str | None = None,
        observation_state: str | None = None,
        urgency: float = 0.5,   # 0.0–1.0
        metadata: dict | None = None,
    ):
        self.policy = policy
        self.reason = reason
        self.topic_code = topic_code
        self.subject_code = subject_code
        self.confidence_level = confidence_level
        self.observation_state = observation_state
        self.urgency = urgency
        self.metadata = metadata or {}
        self.decided_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        return {
            "policy": self.policy,
            "reason": self.reason,
            "topic_code": self.topic_code,
            "subject_code": self.subject_code,
            "confidence_level": self.confidence_level,
            "observation_state": self.observation_state,
            "urgency": self.urgency,
            "decided_at": self.decided_at.isoformat(),
            "metadata": self.metadata,
        }


class PolicyDecisionEngine:
    """
    LOS § 5 — Policy selection RuleEngine.

    Kullanım:
        engine = PolicyDecisionEngine(db)
        result = await engine.decide(user_id)
        result = await engine.decide_for_topic(user_id, subject_code, topic_code)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Ana karar: kullanıcı seviyesi ─────────────────────────────────────────

    async def decide(self, user_id: uuid.UUID) -> DecisionResult:
        """
        Kullanıcı için günlük policy seç.
        Today Engine bu çıktıya göre Next Action üretir.
        """
        obs = ObservationMode(self.db)
        observation_state = await obs.get_state(user_id)
        obs_context = obs.state_for_decide(observation_state)

        # Observation Mode tam etkin → minimal müdahale
        if obs_context["conservative_only"]:
            return DecisionResult(
                Policy.HOLD_OBS,
                reason="Seni tanıyoruz. Observation tamamlanana kadar minimal müdahale.",
                observation_state=observation_state,
                urgency=0.1,
            )

        # Düşük confidence topic'ler var mı?
        low_conf_topics = await self._get_low_confidence_topics(user_id)

        if not low_conf_topics:
            # Evidence yetersiz → Hold
            return DecisionResult(
                Policy.HOLD_OBS,
                reason="Yeterli kanıt birikene kadar bekliyoruz.",
                observation_state=observation_state,
                urgency=0.2,
            )

        # En acil düşük-confidence topic
        top = low_conf_topics[0]

        # Thrashing koruması
        if await self._is_thrashing(user_id, top.topic_code):
            return DecisionResult(
                Policy.EXPLAIN_ONLY,
                reason="Yakın zamanda bu konu için karar verildi.",
                topic_code=top.topic_code,
                subject_code=top.subject_code,
                confidence_level=top.confidence_level,
                observation_state=observation_state,
                urgency=0.3,
            )

        # Policy seç
        return self._select_policy(top, obs_context)

    async def decide_for_topic(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
    ) -> DecisionResult:
        """
        Belirli bir Topic için policy seç.
        Topic Work Surface'e girdi verir.
        """
        obs = ObservationMode(self.db)
        observation_state = await obs.get_state(user_id)
        obs_context = obs.state_for_decide(observation_state)

        # Bu Topic'in Confidence'ını getir
        conf = await self._get_topic_confidence(user_id, topic_code)

        if conf is None or conf.confidence_level == ConfidenceLevel.UNKNOWN:
            # Henüz yeterli data yok → observe + default action
            return DecisionResult(
                Policy.HOLD_OBS,
                reason="Bu konu için henüz yeterli kanıt yok. Çalışmaya başla.",
                topic_code=topic_code,
                subject_code=subject_code,
                confidence_level=ConfidenceLevel.UNKNOWN,
                observation_state=observation_state,
                urgency=0.3,
            )

        if conf.confidence_level == ConfidenceLevel.HIGH:
            return DecisionResult(
                Policy.EXPLAIN_ONLY,
                reason="Bu konuda güçlü. Bakım amaçlı tekrar yeterli.",
                topic_code=topic_code,
                subject_code=subject_code,
                confidence_level=conf.confidence_level,
                observation_state=observation_state,
                urgency=0.2,
                metadata={"belief": conf.belief, "uncertainty": conf.uncertainty},
            )

        return self._select_policy(conf, obs_context)

    # ── Policy seçim kuralları ────────────────────────────────────────────────

    def _select_policy(
        self,
        conf: TopicConfidence,
        obs_context: dict,
    ) -> DecisionResult:
        """
        LOS § 5.4 / 5.5 / 5.6 — Confidence + Observation'a göre policy seç.
        """
        level = conf.confidence_level
        sample = conf.performance_sample_count
        belief = conf.belief
        uncertainty = conf.uncertainty
        trend = conf.trend_direction
        obs_state = obs_context["state"]

        # Kesinlik yüksek, inanç düşük → Tamir adayı
        if level == ConfidenceLevel.LOW and uncertainty < 0.5:
            if sample >= _MIN_SAMPLE_MUTATE_PLAN and obs_context["allow_mutate_plan"] and trend < -0.2:
                # Haftalık tekrarlayan trend + yeterli sample + full obs → PLAN güncelle
                return DecisionResult(
                    Policy.MUTATE_PLAN,
                    reason=(
                        f"Bu konuda tutarlı düşüş trendi ({trend:.2f}). "
                        "Çalışma planına öncelik veriliyor."
                    ),
                    topic_code=conf.topic_code,
                    subject_code=conf.subject_code,
                    confidence_level=level,
                    observation_state=obs_state,
                    urgency=0.85,
                    metadata={"belief": belief, "sample": sample, "trend": trend},
                )
            if sample >= _MIN_SAMPLE_MUTATE_TODAY and obs_context["allow_mutate_today"]:
                return DecisionResult(
                    Policy.MUTATE_TODAY,
                    reason="Bu konu öncelikli. Today'e eklendi.",
                    topic_code=conf.topic_code,
                    subject_code=conf.subject_code,
                    confidence_level=level,
                    observation_state=obs_state,
                    urgency=0.7,
                    metadata={"belief": belief, "sample": sample},
                )
            # Yeterli sample yok → Suggest
            return DecisionResult(
                Policy.SUGGEST,
                reason="Bu konuda düşük güven tespit edildi. Odaklanmayı önerir misin?",
                topic_code=conf.topic_code,
                subject_code=conf.subject_code,
                confidence_level=level,
                observation_state=obs_state,
                urgency=0.55,
            )

        # Belirsizlik yüksek (MEDIUM veya CONFLICTED) → Daha fazla örnek
        if level in (ConfidenceLevel.MEDIUM, ConfidenceLevel.CONFLICTED):
            if obs_context["allow_mutate_today"] and sample >= _MIN_SAMPLE_MUTATE_TODAY:
                return DecisionResult(
                    Policy.SUGGEST,
                    reason="Bu konuda belirsizlik var. Biraz daha pratik yapmanı öneriyoruz.",
                    topic_code=conf.topic_code,
                    subject_code=conf.subject_code,
                    confidence_level=level,
                    observation_state=obs_state,
                    urgency=0.45,
                )

        return DecisionResult(
            Policy.HOLD_OBS,
            reason="Yeterli veri birikene kadar gözlemliyoruz.",
            topic_code=conf.topic_code,
            subject_code=conf.subject_code,
            confidence_level=level,
            observation_state=obs_state,
            urgency=0.2,
        )

    # ── Yardımcılar ──────────────────────────────────────────────────────────

    async def _get_low_confidence_topics(
        self, user_id: uuid.UUID
    ) -> list[TopicConfidence]:
        stmt = (
            select(TopicConfidence)
            .where(
                TopicConfidence.user_id == user_id,
                TopicConfidence.confidence_level.in_(
                    [ConfidenceLevel.LOW, ConfidenceLevel.CONFLICTED]
                ),
                TopicConfidence.performance_sample_count >= _MIN_SAMPLE_MUTATE_TODAY,
            )
            .order_by(
                TopicConfidence.belief.asc(),  # en düşük inanç önce
            )
            .limit(5)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_topic_confidence(
        self, user_id: uuid.UUID, topic_code: str
    ) -> TopicConfidence | None:
        stmt = select(TopicConfidence).where(
            TopicConfidence.user_id == user_id,
            TopicConfidence.topic_code == topic_code,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _is_thrashing(
        self, user_id: uuid.UUID, topic_code: str
    ) -> bool:
        """
        Bu topic için son {_THRASHING_COOLDOWN_HOURS} saat içinde karar verildi mi?
        (Şimdilik TopicConfidence.last_calculated_at kontrolü — production'da snapshot tablosu kullanılır)
        """
        conf = await self._get_topic_confidence(user_id, topic_code)
        if conf is None:
            return False
        threshold = datetime.now(UTC) - timedelta(hours=_THRASHING_COOLDOWN_HOURS)
        return conf.last_calculated_at > threshold if conf.last_calculated_at else False


# ── Policy → Action mapping (Today Engine için) ──────────────────────────────

def policy_to_action_type(policy: Policy) -> str:
    """Policy'yi Today Engine action_type'ına çevir."""
    return {
        Policy.HOLD_OBS: "focus",
        Policy.SUGGEST: "suggest",
        Policy.MUTATE_TODAY: "study_plan",
        Policy.MUTATE_PLAN: "study_plan",
        Policy.EXPLAIN_ONLY: "focus",
    }.get(policy, "focus")


def policy_to_confidence_tone(policy: Policy) -> str:
    """Policy'yi confidence_tone'a çevir."""
    return {
        Policy.HOLD_OBS: "low",
        Policy.SUGGEST: "medium",
        Policy.MUTATE_TODAY: "high",
        Policy.MUTATE_PLAN: "high",
        Policy.EXPLAIN_ONLY: "high",
    }.get(policy, "low")
