"""
StudyOS — Topic Evidence Engine (Module 1)
LOS § 3 — Evidence Engine

Evidence Engine, "doğru-yanlış sayacı" değildir.
Topic üzerindeki öğrenme durumunu etkileyen bağlanmış gözlemlerin
üretim ve sınıflandırma katmanıdır.

Her evidence kaydı:
  - Bir Topic'e bağlıdır (subject_code + topic_code)
  - Bir kategoriye aittir (performance / effort / temporal / …)
  - Bir kalite ağırlığı taşır (quality_weight: 0–1)
  - Ham metadata içerir (Confidence Engine aggregation için)
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EvidenceCategory(StrEnum):
    """LOS § 3.1 — Evidence kategorileri."""

    # A. Soru sonuçları, revision grade, deneme net
    PERFORMANCE = "performance"
    # B. Çalışma süresi, soru hacmi, kaynak açma/tamamlama
    EFFORT = "effort"
    # C. Çalışma saati, gün, oturum boşluğu, unutma vekili
    TEMPORAL = "temporal"
    # D. Mola davranışı, pomodoro abort, yarım oturum
    BEHAVIORAL_MICRO = "behavioral_micro"
    # E. Aktif gün oranı, süre varyansı, neglect
    CONSISTENCY = "consistency"
    # F. Kaynak tipi tercihi, pomodoro süresi
    PREFERENCE = "preference"
    # G. Confidence history, öneri kabul/red
    META = "meta"


class EvidenceHorizon(StrEnum):
    """LOS § 3.2 — Zaman vadesi."""

    INSTANT = "instant"   # tek olay / tek oturum
    SHORT = "short"       # 1–3 gün
    MID = "mid"           # 1–3 hafta
    LONG = "long"         # ay+


class EvidenceSourceType(StrEnum):
    """Kanıtın kaynağı."""

    STUDY_SESSION = "study_session"
    QUESTION_RECORD = "question_record"
    REVISION_REVIEW = "revision_review"
    REVISION_ITEM = "revision_item"
    EXAM = "exam"
    PLANNER = "planner"
    MANUAL = "manual"
    AI_QUESTION = "ai_question"  # AI tarafından üretilen soru yanıtlandı
    ASSESSMENT = "assessment"  # Sprint 18 — kalibrasyon / daily / branch


class TopicEvidence(Base):
    """
    LOS § 3 — Topic Evidence kaydı.

    Sense → Bind → Evidence zincirinin çıktısı.
    Her kayıt bir Topic'e bağlıdır; bağlanamayan olaylar
    subject_code='unbound' ile düşük kaliteyle saklanır.
    """

    __tablename__ = "topic_evidence"
    __table_args__ = (
        Index("ix_topic_evidence_user_topic", "user_id", "topic_code"),
        Index("ix_topic_evidence_user_subject", "user_id", "subject_code"),
        Index("ix_topic_evidence_occurred", "user_id", "occurred_at"),
        Index("ix_topic_evidence_category", "user_id", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Bind: Canonical Topic kimliği ──────────────────────────────
    subject_code: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    topic_code: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )

    # ── Sınıflandırma ──────────────────────────────────────────────
    category: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EvidenceHorizon.INSTANT
    )

    # ── Sinyal değeri ──────────────────────────────────────────────
    # Normalize 0.0–1.0: accuracy, completion ratio, grade signal vb.
    # Effort için raw dk de olabilir (metadata'da full değer var).
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Kalite ağırlığı ────────────────────────────────────────────
    # 0.0 = güvenilmez gürültü  /  1.0 = yüksek kalite kanıt
    # Confidence Engine aggregate'de quality-weighted kullanır.
    quality_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)

    # ── Kaynak ─────────────────────────────────────────────────────
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # ── Ham metadata ───────────────────────────────────────────────
    # Confidence Engine tüm ham değerleri buradan okur.
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    # ── Zaman ──────────────────────────────────────────────────────
    # occurred_at: olayın gerçek zamanı (session başlangıcı, QR tarihi vb.)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<TopicEvidence {self.category} {self.topic_code} "
            f"v={self.value:.2f} q={self.quality_weight:.2f}>"
        )
