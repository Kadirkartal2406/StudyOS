"""
StudyOS — Topic Confidence Engine (LOS Module 2)
LOS § 4 — Confidence Engine

Confidence = inanç + belirsizlik çifti.
"Öğrendin / öğrenmedin" bayrağı değildir.

Faktörler:
  - sample_size: az örnek → yüksek belirsizlik
  - consistency: aynı yönde tekrar → inanç güçlenir
  - recency: yeni kanıt eskiyi aşındırır
  - forgetting: uzun sessizlik → decay
  - evidence_quality: zayıf kanıt az ağırlık

Karar birimi: Decision Engine Confidence'ı okur; Confidence karar vermez.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ConfidenceLevel(StrEnum):
    """LOS § 4.5 — Decide'e etkisi için kategorik özet."""

    UNKNOWN = "unknown"         # cold-start; yetersiz evidence
    LOW = "low"                 # düşük inanç + düşük belirsizlik → tamir adayı
    MEDIUM = "medium"           # orta belirsizlik; daha fazla örnek gerekiyor
    HIGH = "high"               # yüksek inanç + düşük belirsizlik → bakım
    CONFLICTED = "conflicted"   # çelişkili kanıt → belirsizlik yüksek


class TopicConfidence(Base):
    """
    LOS § 4 — Topic başına Confidence durumu.

    Her kullanıcı × topic çifti için tek kayıt.
    Evidence aggregate'i sonrasında güncellenir.
    """

    __tablename__ = "topic_confidence"
    __table_args__ = (
        Index("ix_topic_confidence_user_topic", "user_id", "topic_code", unique=True),
        Index("ix_topic_confidence_level", "user_id", "confidence_level"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Topic kimliği ──────────────────────────────────────────────
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # ── İnanç + belirsizlik ────────────────────────────────────────
    # belief: 0.0 (hiç inanç yok) → 1.0 (tam inanç)
    # uncertainty: 0.0 (çok emin) → 1.0 (tamamen belirsiz)
    belief: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    uncertainty: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # ── Kategorik özet ─────────────────────────────────────────────
    confidence_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ConfidenceLevel.UNKNOWN, index=True
    )

    # ── Evidence aggregate girdileri ───────────────────────────────
    performance_sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weighted_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_effort_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Trend ─────────────────────────────────────────────────────
    # +1.0 = yükselen trend, 0 = durağan, -1.0 = düşen trend
    trend_direction: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Kaç evidence penceresinde tutarlı?
    consistency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Forgetting ────────────────────────────────────────────────
    days_since_last_evidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Forgetting decay uygulandı mı?
    forgetting_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Tarihçe özeti ─────────────────────────────────────────────
    # Son birkaç hesaplama için özet (thrashing koruması için)
    history_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # ── Zaman ──────────────────────────────────────────────────────
    last_evidence_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<TopicConfidence {self.topic_code} "
            f"belief={self.belief:.2f} unc={self.uncertainty:.2f} "
            f"level={self.confidence_level}>"
        )
