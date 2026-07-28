"""
StudyOS — Revision & Spaced Repetition modelleri
Sprint-2.8 (Meeting-026) — S-11 + S-12 MVP.
LLM kuyruk/interval üretmez; Rule Engine + saklanan reason.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RevisionSourceType(StrEnum):
    MANUAL = "manual"
    QUESTION_TRACKING = "question_tracking"
    EXAM = "exam"
    PLANNER = "planner"
    AI_SUGGESTION = "ai_suggestion"


class RevisionItemStatus(StrEnum):
    ACTIVE = "active"
    MASTERED = "mastered"
    ARCHIVED = "archived"


class RevisionGrade(StrEnum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


class RevisionItem(Base):
    __tablename__ = "revision_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[RevisionSourceType] = mapped_column(
        String(40), nullable=False, default=RevisionSourceType.MANUAL, index=True
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    # 1–5; Rule Engine review ile günceller — LLM dokunmaz
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    reason: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    status: Mapped[RevisionItemStatus] = mapped_column(
        String(20), nullable=False, default=RevisionItemStatus.ACTIVE, index=True
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    schedule: Mapped["RevisionSchedule | None"] = relationship(
        "RevisionSchedule",
        back_populates="item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["RevisionReview"]] = relationship(
        "RevisionReview",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="RevisionReview.reviewed_at.desc()",
    )


class RevisionSchedule(Base):
    __tablename__ = "revision_schedules"
    __table_args__ = (UniqueConstraint("revision_item_id", name="uq_revision_schedules_item"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("revision_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ease_factor: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    repetition_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lapse_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    item: Mapped[RevisionItem] = relationship("RevisionItem", back_populates="schedule")


class RevisionReview(Base):
    __tablename__ = "revision_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("revision_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    grade: Mapped[RevisionGrade] = mapped_column(String(20), nullable=False)
    previous_interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    new_interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    new_difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_ease: Mapped[float] = mapped_column(Float, nullable=False)
    new_ease: Mapped[float] = mapped_column(Float, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    item: Mapped[RevisionItem] = relationship("RevisionItem", back_populates="reviews")
