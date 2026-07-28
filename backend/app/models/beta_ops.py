"""
Sprint 21 RC — Merkezi analytics (dış servis zorunlu değil).
Olaylar DB'ye yazılır; ileride export/Sentry/Firebase bağlanabilir.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AnalyticsEventName(StrEnum):
    APP_OPEN = "app_open"
    TODAY_VIEWED = "today_viewed"
    TOPIC_OPENED = "topic_opened"
    QUIZ_GENERATED = "quiz_generated"
    QUIZ_FINISHED = "quiz_finished"
    ASSESSMENT_STARTED = "assessment_started"
    ASSESSMENT_FINISHED = "assessment_finished"
    EXPLAIN_USED = "explain_used"
    COACH_VIEWED = "coach_viewed"
    NOTEBOOK_VIEWED = "notebook_viewed"
    RESOURCE_ADDED = "resource_added"
    FEEDBACK_SENT = "feedback_sent"
    ERROR_REPORTED = "error_reported"


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    platform: Mapped[str | None] = mapped_column(String(40), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    properties: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )


class BetaFeedback(Base):
    """RC.9 — Beta geri bildirimi."""

    __tablename__ = "beta_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    # bug | suggestion | other
    message: Mapped[str] = mapped_column(Text, nullable=False)
    screen_hint: Mapped[str | None] = mapped_column(String(200), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(40), nullable=True)
    log_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
