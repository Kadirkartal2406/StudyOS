"""
StudyOS — QuestionRecord Modeli
Soru takip kaydı (S-09). Bkz. docs/architecture/database-design.md §1.11b
Sprint-1.9 (Meeting-017) — A1: subject/topic string (Subject tablosu yok).
Hard delete; soft delete yok.
"""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ExamType(StrEnum):
    """Sınav türü — canonical variants (see app.core.exam_identity)."""

    KPSS_LISANS = "kpss_lisans"
    KPSS_ONLISANS = "kpss_onlisans"
    KPSS_ORTAOGRETIM = "kpss_ortaogretim"
    TYT = "tyt"
    AYT_SAYISAL = "ayt_sayisal"
    AYT_EA = "ayt_ea"
    AYT_SOZEL = "ayt_sozel"
    YDT_INGILIZCE = "ydt_ingilizce"
    YKS = "yks"  # umbrella: TYT + AYT/YDT branch
    AGS = "ags"
    LGS = "lgs"
    ALES = "ales"
    DGS = "dgs"
    YDS_INGILIZCE = "yds_ingilizce"
    YOKDIL_INGILIZCE = "yokdil_ingilizce"
    CUSTOM = "custom"


class QuestionDifficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionSource(StrEnum):
    BOOK = "book"
    VIDEO = "video"
    PAST_EXAM = "past_exam"
    ONLINE = "online"
    CLASS = "class"
    OTHER = "other"


class QuestionRecord(Base):
    """Kullanıcının çözdüğü soru seti kaydı (batch entry)."""

    __tablename__ = "question_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    study_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # A1 — Subject/Topic tablosu yok; düz metin (StudyPlan emsali).
    subject: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)

    # Sprint-6 — Catalog-linked codes (nullable; backfilled incrementally).
    subject_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    topic_code: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)

    question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blank_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    difficulty: Mapped[QuestionDifficulty | None] = mapped_column(String(20), nullable=True)
    source: Mapped[QuestionSource | None] = mapped_column(String(30), nullable=True)
    exam_type: Mapped[ExamType | None] = mapped_column(String(20), nullable=True, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Hesaplanan net (create/update'te yazılır; AI için hazır).
    net_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<QuestionRecord id={self.id} user_id={self.user_id} "
            f"subject={self.subject!r} count={self.question_count}>"
        )
