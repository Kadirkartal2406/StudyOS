"""
StudyOS — StudySession Modeli
Pomodoro / kronometre + server-side mola telemetrisi (Sprint 22).
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class StudySessionStatus(StrEnum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class StudySessionMode(StrEnum):
    POMODORO = "pomodoro"
    CHRONOMETER = "chronometer"


class StudySessionPhase(StrEnum):
    FOCUS = "focus"
    BREAK = "break"


class StudySession(Base):
    """Kullanıcının bir çalışma oturumu kaydı."""

    __tablename__ = "study_sessions"

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

    subject_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    topic_code: Mapped[str | None] = mapped_column(String(200), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Chronometer: nullable planned duration
    planned_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    mode: Mapped[str] = mapped_column(String(20), nullable=False, default=StudySessionMode.POMODORO)
    phase: Mapped[str] = mapped_column(String(20), nullable=False, default=StudySessionPhase.FOCUS)
    actual_break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    break_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    break_segments: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    completed_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_topics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[StudySessionStatus] = mapped_column(
        String(20), nullable=False, default=StudySessionStatus.RUNNING
    )

    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<StudySession id={self.id} user_id={self.user_id} status={self.status}>"
