"""
StudyOS — Achievement modelleri
Sprint-2.9 (Meeting-027) — S-33 Achievement Engine.
LLM unlock üretmez; Rule Engine + saklanan reason.
Unlock ledger immutable (S1).
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AchievementTier(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LEGENDARY = "legendary"


class AchievementCategory(StrEnum):
    POMODORO = "pomodoro"
    STUDY_TIME = "study_time"
    QUESTIONS = "questions"
    EXAM = "exam"
    REVISION = "revision"
    GOAL = "goal"
    PLANNER = "planner"
    STREAK = "streak"


class Achievement(Base):
    """Katalog — seed ile dolar; criteria JSONB data-driven (U1)."""

    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    category: Mapped[AchievementCategory] = mapped_column(String(40), nullable=False, index=True)
    tier: Mapped[AchievementTier] = mapped_column(String(20), nullable=False, default=AchievementTier.EASY)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=10)  # display only (P1)
    icon_key: Mapped[str] = mapped_column(String(80), nullable=False, default="trophy")
    # criteria: {metric, op, value, events?}
    criteria: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class UserAchievement(Base):
    """Unlock ledger — silinmez (S1). UNIQUE(user_id, achievement_id) idempotent (D1)."""

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievements_user_achievement"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    source_event: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    achievement: Mapped[Achievement] = relationship("Achievement")


class AchievementProgress(Base):
    """Kısmi ilerleme (E1)."""

    __tablename__ = "achievement_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_achievement_progress_user_achievement"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    target_value: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    achievement: Mapped[Achievement] = relationship("Achievement")
