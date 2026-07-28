"""
StudyOS — Goal Modeli
Sprint-2.1 (Meeting-019) — Goal Engine.
AI Goal Generator / Habit / Challenge için metadata hazır.
"""

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class GoalType(StrEnum):
    STUDY_TIME = "study_time"
    POMODORO = "pomodoro"
    QUESTION = "question"
    SUBJECT = "subject"
    TOPIC = "topic"
    CUSTOM = "custom"


class GoalPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class GoalPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Goal(Base):
    """Kullanıcı hedefi — süre / pomodoro / soru / ders / konu / özel."""

    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal_type: Mapped[GoalType] = mapped_column(String(30), nullable=False, index=True)
    # Sprint-3.0.2 — ürün tipi (nullable; motor goal_type korunur)
    product_goal_type: Mapped[str | None] = mapped_column(
        String(40), nullable=True, index=True
    )
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    priority: Mapped[GoalPriority] = mapped_column(
        String(20), nullable=False, default=GoalPriority.MEDIUM
    )
    period: Mapped[GoalPeriod] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[GoalStatus] = mapped_column(
        String(20), nullable=False, default=GoalStatus.ACTIVE, index=True
    )
    # Subject / Topic goal eşlemesi (string — Subject tablosu yok)
    subject: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    # Sprint-3.0 post-revision — hangi sınav hedefi için (additive, nullable)
    exam_type: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Gelecek: AI generator, habit, challenge, gamification
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    milestones_reached: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
