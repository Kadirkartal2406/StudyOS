"""
StudyOS — Observation Mode (LOS Module 3)
LOS § 6 — Gate-based state machine.

Kapılar dolmadan MUTATE_PLAN yok.
Observation'da Today boş kalmaz; Next Action "güvenli varsayımdır".

State: observing → calibrating → full

Kapılar (LOS § 6.4):
  1. min_active_study_days  — Gerçek oturumlar oluştu
  2. min_topic_evidence     — Birden fazla Topic'te sample
  3. min_temporal_sample    — Saat/alışkanlık için tekrar
  4. stability              — Tempo aşırı kaotik değil
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_profile import Student
from app.models.topic_evidence import EvidenceCategory, TopicEvidence

# ── Kapı eşikleri (LOS § 6.4) ────────────────────────────────────────────────

GATE_MIN_ACTIVE_DAYS = 5           # 5 farklı günde oturum
GATE_MIN_TOPIC_EVIDENCE_COUNT = 3  # en az 3 farklı Topic'te kanıt
GATE_MIN_TEMPORAL_SESSIONS = 4     # farklı saat dilimlerinde en az 4 oturum
GATE_STABILITY_MAX_CV = 0.8        # varyasyon katsayısı < 0.8 (kaotik değil)

# Observation state'leri
OBSERVING = "observing"
CALIBRATING = "calibrating"
FULL = "full"


class ObservationMode:
    """
    LOS § 6 — Observation gate checker + state updater.

    Kullanım:
        obs = ObservationMode(db)
        state = await obs.get_state(user_id)
        gates = await obs.check_gates(user_id)
        if gates['all_passed']:
            await obs.advance(user_id, student)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student(self, user_id: uuid.UUID) -> Student | None:
        stmt = select(Student).where(Student.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_state(self, user_id: uuid.UUID) -> str:
        student = await self.get_student(user_id)
        if student is None:
            return OBSERVING
        return student.observation_state or OBSERVING

    # ── Kapı değerlendirmesi ──────────────────────────────────────────────────

    async def check_gates(self, user_id: uuid.UUID) -> dict:
        """
        Tüm kapıları değerlendir. Sonuç:
          {
            'min_active_days': bool,
            'min_topic_evidence': bool,
            'min_temporal_sample': bool,
            'stability': bool,
            'all_passed': bool,
            'details': {...}
          }
        """
        since = datetime.now(UTC) - timedelta(days=30)

        # Gate 1: Aktif çalışma günleri
        active_days = await self._count_active_days(user_id, since)

        # Gate 2: Topic evidence çeşitliliği
        topic_count = await self._count_distinct_evidence_topics(user_id)

        # Gate 3: Temporal sample (farklı saat dilimleri)
        temporal_diversity = await self._count_temporal_diversity(user_id, since)

        # Gate 4: Stability (günlük effort varyasyonu)
        stability_ok = await self._check_stability(user_id, since)

        g1 = active_days >= GATE_MIN_ACTIVE_DAYS
        g2 = topic_count >= GATE_MIN_TOPIC_EVIDENCE_COUNT
        g3 = temporal_diversity >= GATE_MIN_TEMPORAL_SESSIONS
        g4 = stability_ok

        return {
            "min_active_days": g1,
            "min_topic_evidence": g2,
            "min_temporal_sample": g3,
            "stability": g4,
            "all_passed": g1 and g2 and g3 and g4,
            "details": {
                "active_days": active_days,
                "distinct_topics_with_evidence": topic_count,
                "temporal_sessions": temporal_diversity,
                "stability_ok": stability_ok,
            },
        }

    async def _count_active_days(
        self, user_id: uuid.UUID, since: datetime
    ) -> int:
        """Effort evidence'ından kaç farklı gün oturum yapıldı."""
        stmt = (
            select(
                func.count(
                    func.distinct(
                        func.date_trunc("day", TopicEvidence.occurred_at)
                    )
                )
            )
            .select_from(TopicEvidence)
            .where(
                TopicEvidence.user_id == user_id,
                TopicEvidence.category == EvidenceCategory.EFFORT,
                TopicEvidence.occurred_at >= since,
            )
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def _count_distinct_evidence_topics(self, user_id: uuid.UUID) -> int:
        """Kaç farklı Topic'te (unbound dışında) kanıt var."""
        stmt = (
            select(func.count(func.distinct(TopicEvidence.topic_code)))
            .select_from(TopicEvidence)
            .where(
                TopicEvidence.user_id == user_id,
                TopicEvidence.topic_code != "unbound",
            )
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def _count_temporal_diversity(
        self, user_id: uuid.UUID, since: datetime
    ) -> int:
        """Kaç farklı saat diliminde TEMPORAL evidence var."""
        stmt = select(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.category == EvidenceCategory.TEMPORAL,
            TopicEvidence.occurred_at >= since,
            TopicEvidence.topic_code != "unbound",
        )
        result = await self.db.execute(stmt)
        rows = list(result.scalars().all())
        if not rows:
            return 0
        hours = {r.metadata_.get("hour_of_day", -1) for r in rows}
        hours.discard(-1)
        # 4 saatlik dilimlere grupla → çeşitlilik
        buckets = {h // 4 for h in hours}
        return len(buckets)

    async def _check_stability(
        self, user_id: uuid.UUID, since: datetime
    ) -> bool:
        """
        Günlük effort toplamı varyasyon katsayısı < eşik → stable.
        Çok az veri varsa 'stable' kabul et (aşırı kısıtlama olmasın).
        """
        stmt = select(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.category == EvidenceCategory.EFFORT,
            TopicEvidence.occurred_at >= since,
        )
        result = await self.db.execute(stmt)
        rows = list(result.scalars().all())

        if len(rows) < 3:
            return True  # yeterli veri yok, bloke etme

        # Günlük toplam effort
        daily: dict[str, float] = {}
        for r in rows:
            day = r.occurred_at.strftime("%Y-%m-%d")
            minutes = float(r.metadata_.get("actual_minutes", 0))
            daily[day] = daily.get(day, 0) + minutes

        values = list(daily.values())
        if len(values) < 2:
            return True

        mean = sum(values) / len(values)
        if mean == 0:
            return False
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        cv = variance ** 0.5 / mean  # coefficient of variation
        return cv < GATE_STABILITY_MAX_CV

    # ── State transitions ─────────────────────────────────────────────────────

    async def advance(self, user_id: uuid.UUID) -> str:
        """
        Kapıları kontrol et; geçiş varsa Student'ı güncelle.
        Yeni state'i döndür.
        """
        student = await self.get_student(user_id)
        if student is None:
            return OBSERVING

        current = student.observation_state or OBSERVING
        if current == FULL:
            return FULL

        gates = await self.check_gates(user_id)
        now = datetime.now(UTC)

        if current == OBSERVING and gates["min_active_days"] and gates["min_topic_evidence"]:
            # Observing → Calibrating: temel kapılar doldu
            student.observation_state = CALIBRATING
            student.observation_entered_at = student.observation_entered_at or now
            student.observation_gates = gates["details"]
            await self.db.flush()
            return CALIBRATING

        if current == CALIBRATING and gates["all_passed"]:
            # Calibrating → Full: tüm kapılar doldu
            student.observation_state = FULL
            student.observation_exited_at = now
            student.observation_gates = gates["details"]
            await self.db.flush()
            return FULL

        # Kapılar güncelle
        student.observation_gates = gates["details"]
        await self.db.flush()
        return current

    def state_for_decide(self, observation_state: str) -> dict:
        """
        Decision Engine için Observation durumu özeti.
        """
        return {
            "state": observation_state,
            "is_observing": observation_state == OBSERVING,
            "is_calibrating": observation_state == CALIBRATING,
            "is_full": observation_state == FULL,
            # Living Plan mutasyonuna izin var mı?
            "allow_mutate_plan": observation_state == FULL,
            # Agresif Today mutasyonuna izin var mı?
            "allow_mutate_today": observation_state in (CALIBRATING, FULL),
            # Sadece güvenli öneriler?
            "conservative_only": observation_state == OBSERVING,
        }
