"""
StudyOS — Confidence Engine (LOS Module 2)
LOS § 4 — Topic başına inanç + belirsizlik hesaplama.

Confidence Engine karar vermez. Decision Engine için girdi üretir.
Evidence aggregate → belief + uncertainty → confidence_level.

Prensipler (LOS § 4.4):
  - Yavaş yüksel, kontrollü düş
  - Belirsizlik kapısı: yüksek belirsizlik → Decide agresif olmaz
  - Floor/ceiling yok: her zaman yeni evidence'a açık
  - Cross-topic izolasyon: A topic'i B'yi doğrudan etkilemez
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_confidence import ConfidenceLevel, TopicConfidence
from app.repositories.topic_evidence_repository import TopicEvidenceRepository
from app.services.evidence_service import EvidenceService

if TYPE_CHECKING:
    pass

# ── Sabitler ──────────────────────────────────────────────────────────────────

# Minimum performance sample → belirsizlik düşmeye başlar
_MIN_SAMPLE_FOR_LOW_UNCERTAINTY = 3
_MIN_SAMPLE_FOR_SETTLED = 8

# Forgetting decay: kaç gün sonra başlar
_FORGETTING_START_DAYS = 14
# Her ek gün için belief decay katsayısı
_FORGETTING_RATE = 0.008   # 14 gün sonra ~%11 decay / 30 gün → ~%24

# Trend pencereleri: son N kayıt
_TREND_WINDOW = 5

# Consistency için yön eşiği
_CONSISTENCY_THRESHOLD = 0.6

# Belief güncelleme öğrenme hızı (slow update prensibi)
_BELIEF_LEARNING_RATE = 0.25
_UNCERTAINTY_LEARNING_RATE = 0.3


class ConfidenceEngine:
    """
    LOS § 4 — Topic Confidence hesaplama + güncelleme.

    Kullanım:
        engine = ConfidenceEngine(db)
        conf = await engine.recalculate(user_id, subject_code, topic_code)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_repo = TopicEvidenceRepository(db)
        self.evidence_svc = EvidenceService(db)

    # ── Ana hesaplama ─────────────────────────────────────────────────────────

    async def recalculate(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
    ) -> TopicConfidence:
        """
        Topic için Confidence'ı evidence aggregate'inden hesapla ve kaydet.
        Mevcut kayıt varsa slow-update; yoksa oluştur.
        """
        # 1. Evidence aggregate'i al
        since_mid = datetime.now(UTC) - timedelta(days=21)  # orta vade
        aggregate = await self.evidence_svc.topic_aggregate(
            user_id, topic_code, since=since_mid
        )

        # 2. Tüm performance evidence (trend için)
        perf_rows = await self.evidence_repo.list_for_topic(
            user_id, topic_code,
            limit=50,
        )

        # 3. Mevcut confidence kaydını getir veya oluştur
        conf = await self._get_or_create(user_id, subject_code, topic_code)

        # 4. Hesapla
        new_belief, new_uncertainty, level = self._compute(
            aggregate=aggregate,
            perf_rows=perf_rows,
            current_belief=conf.belief,
            current_uncertainty=conf.uncertainty,
        )

        # 5. Forgetting decay
        last_ev_str = aggregate.get("last_evidence_at")
        last_ev_at = datetime.fromisoformat(last_ev_str) if last_ev_str else None
        forgetting_applied = False
        if last_ev_at:
            days_silent = (datetime.now(UTC) - last_ev_at).days
            if days_silent >= _FORGETTING_START_DAYS:
                decay = _FORGETTING_RATE * (days_silent - _FORGETTING_START_DAYS + 1)
                new_belief = max(0.1, new_belief - decay)
                new_uncertainty = min(1.0, new_uncertainty + decay * 0.5)
                forgetting_applied = True
                # Level'ı yeniden belirle
                level = self._classify(new_belief, new_uncertainty)
        else:
            days_silent = None

        # 6. History snapshot güncelle (son 3 hesaplama)
        hist = conf.history_snapshot or {}
        snapshots: list = hist.get("snapshots", [])
        snapshots.append({
            "ts": datetime.now(UTC).isoformat(),
            "belief": round(new_belief, 3),
            "uncertainty": round(new_uncertainty, 3),
            "level": level,
        })
        snapshots = snapshots[-3:]  # son 3 kayıt

        # 7. Trend hesapla
        trend, consistency = self._compute_trend(perf_rows)

        # 8. Kaydet
        conf.belief = round(new_belief, 4)
        conf.uncertainty = round(new_uncertainty, 4)
        conf.confidence_level = level
        conf.performance_sample_count = aggregate.get("performance_sample_count", 0)
        conf.weighted_accuracy = aggregate.get("weighted_accuracy")
        conf.total_effort_minutes = aggregate.get("effort_minutes", 0.0)
        conf.trend_direction = round(trend, 3)
        conf.consistency_score = round(consistency, 3)
        conf.days_since_last_evidence = days_silent
        conf.forgetting_applied = forgetting_applied
        conf.last_evidence_at = last_ev_at
        conf.last_calculated_at = datetime.now(UTC)
        conf.updated_at = datetime.now(UTC)
        conf.history_snapshot = {"snapshots": snapshots}

        await self.db.flush()
        return conf

    # ── Hesaplama çekirdeği ───────────────────────────────────────────────────

    def _compute(
        self,
        *,
        aggregate: dict,
        perf_rows: list,
        current_belief: float,
        current_uncertainty: float,
    ) -> tuple[float, float, str]:
        """
        Yeni belief + uncertainty hesapla.
        LOS prensibi: yavaş yüksel, kontrollü düş.
        """
        sample_count = aggregate.get("performance_sample_count", 0)
        weighted_acc = aggregate.get("weighted_accuracy")

        # Cold-start: yeterli kanıt yok
        if sample_count < 2 or weighted_acc is None:
            return current_belief, min(current_uncertainty, 1.0), ConfidenceLevel.UNKNOWN

        # Target belief: quality-weighted accuracy
        target_belief = weighted_acc

        # Target uncertainty: sample_count'a göre azalır
        if sample_count < _MIN_SAMPLE_FOR_LOW_UNCERTAINTY:
            target_uncertainty = 0.85
        elif sample_count < _MIN_SAMPLE_FOR_SETTLED:
            target_uncertainty = 0.5 - (sample_count - _MIN_SAMPLE_FOR_LOW_UNCERTAINTY) * 0.05
        else:
            target_uncertainty = max(0.15, 0.5 - sample_count * 0.03)

        # Slow update: yavaşça yaklaş
        # LOS: "yavaş yüksel" — öğrenme yönünde daha yavaş
        if target_belief > current_belief:
            rate = _BELIEF_LEARNING_RATE * 0.7  # yükseliş daha yavaş
        else:
            rate = _BELIEF_LEARNING_RATE * 1.2  # düşüş biraz daha hızlı (asimetri)

        new_belief = current_belief + rate * (target_belief - current_belief)
        new_belief = max(0.05, min(0.98, new_belief))

        new_uncertainty = current_uncertainty + _UNCERTAINTY_LEARNING_RATE * (
            target_uncertainty - current_uncertainty
        )
        new_uncertainty = max(0.05, min(1.0, new_uncertainty))

        level = self._classify(new_belief, new_uncertainty)
        return new_belief, new_uncertainty, level

    def _classify(self, belief: float, uncertainty: float) -> str:
        """LOS § 4.5 — Kategorik sınıflandırma."""
        if uncertainty > 0.75:
            return ConfidenceLevel.UNKNOWN
        if uncertainty > 0.5:
            if belief > 0.65:
                return ConfidenceLevel.MEDIUM
            return ConfidenceLevel.LOW
        # uncertainty <= 0.5: settled kanıt
        if belief > 0.72:
            return ConfidenceLevel.HIGH
        if belief < 0.45:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.MEDIUM

    def _compute_trend(
        self, perf_rows: list
    ) -> tuple[float, float]:
        """
        Son N performance evidence'ından trend ve consistency hesapla.
        Trend: +1 yükseliş, 0 durağan, -1 düşüş.
        Consistency: aynı yönde tekrar oranı.
        """
        if len(perf_rows) < 2:
            return 0.0, 0.0

        # En son _TREND_WINDOW değeri (occurred_at sırasına göre)
        sorted_rows = sorted(perf_rows, key=lambda r: r.occurred_at)[-_TREND_WINDOW:]
        values = [r.value for r in sorted_rows]

        if len(values) < 2:
            return 0.0, 0.0

        # Basit lineer trend: sonlar − önler
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)
        trend = (second_half_avg - first_half_avg) * 2  # -1 ile 1 arası normalize

        # Consistency: kaç değişim aynı yönde?
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        if all(d >= 0 for d in diffs):
            consistency = 1.0
        elif all(d <= 0 for d in diffs):
            consistency = 0.0  # tutarlı düşüş
        else:
            positives = sum(1 for d in diffs if d > 0)
            consistency = positives / len(diffs)

        return max(-1.0, min(1.0, trend)), consistency

    # ── CRUD ─────────────────────────────────────────────────────────────────

    async def _get_or_create(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
    ) -> TopicConfidence:
        stmt = select(TopicConfidence).where(
            TopicConfidence.user_id == user_id,
            TopicConfidence.topic_code == topic_code,
        )
        result = await self.db.execute(stmt)
        conf = result.scalar_one_or_none()
        if conf is None:
            conf = TopicConfidence(
                user_id=user_id,
                subject_code=subject_code,
                topic_code=topic_code,
            )
            self.db.add(conf)
            await self.db.flush()
        return conf

    async def get_for_topic(
        self,
        user_id: uuid.UUID,
        topic_code: str,
    ) -> TopicConfidence | None:
        stmt = select(TopicConfidence).where(
            TopicConfidence.user_id == user_id,
            TopicConfidence.topic_code == topic_code,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_low_confidence_topics(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
    ) -> list[TopicConfidence]:
        """Decision Engine: 'tamir adayı' topic listesi."""
        stmt = (
            select(TopicConfidence)
            .where(
                TopicConfidence.user_id == user_id,
                TopicConfidence.confidence_level.in_(
                    [ConfidenceLevel.LOW, ConfidenceLevel.CONFLICTED]
                ),
            )
            .order_by(TopicConfidence.belief.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
