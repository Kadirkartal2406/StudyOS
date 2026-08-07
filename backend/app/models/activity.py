"""
StudyOS — Activity Modeli
Kullanıcı olay akışı (timeline). Bkz. docs/architecture/database-design.md §1.13

Genel tasarım (Sprint-1.7): Notification, Widget, AI Timeline ve Teacher Analytics
modüllerinin de kullanabileceği event log. metadata JSONB ile genişletilebilir.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ActivityEventType(StrEnum):
    """Bilinen event tipleri. Yeni modüller string olarak ek event ekleyebilir."""

    SESSION_STARTED = "session_started"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_COMPLETED = "session_completed"
    BREAK_STARTED = "break_started"
    BREAK_ENDED = "break_ended"
    STUDY_FINISHED = "study_finished"
    PLAN_COMPLETED = "plan_completed"
    EXAM_COMPLETED = "exam_completed"
    PLANNER_GENERATED = "planner_generated"
    PLANNER_ACCEPTED = "planner_accepted"
    REVISION_CREATED = "revision_created"
    REVISION_REVIEWED = "revision_reviewed"
    REVISION_COMPLETED = "revision_completed"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    WORKSPACE_CREATED = "workspace_created"
    WORKSPACE_UPDATED = "workspace_updated"


class Activity(Base):
    """Kullanıcıya ait tek bir aktivite / olay kaydı."""

    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    study_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    study_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # İleride bildirim/AI/öğretmen paneli için esnek yük.
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    def __repr__(self) -> str:
        return f"<Activity id={self.id} type={self.event_type} user_id={self.user_id}>"
