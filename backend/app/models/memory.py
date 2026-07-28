"""
StudyOS — Memory Modeli
Sprint-2.3 (Meeting-021) — Long-term memory foundation.
Embedding/pgvector yok; metadata.embedding_ready rezerv.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MemoryCategory(StrEnum):
    STUDY_HABIT = "study_habit"
    GOAL = "goal"
    PREFERENCE = "preference"
    WEAK_SUBJECT = "weak_subject"
    STRONG_SUBJECT = "strong_subject"
    SCHEDULE = "schedule"
    CONVERSATION = "conversation"
    MOTIVATION = "motivation"
    EXAM = "exam"
    CUSTOM = "custom"


class MemorySource(StrEnum):
    AI_CHAT = "ai_chat"
    GOAL_ENGINE = "goal_engine"
    STUDY_PLAN = "study_plan"
    QUESTION_TRACKING = "question_tracking"
    STATISTICS = "statistics"
    STUDY_RESOURCE = "study_resource"
    EXAM_TRACKING = "exam_tracking"
    MANUAL = "manual"


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[MemoryCategory] = mapped_column(String(40), nullable=False, index=True)
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[MemorySource] = mapped_column(String(40), nullable=False, index=True)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
