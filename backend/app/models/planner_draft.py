"""
StudyOS — PlannerDraft modeli
Sprint-2.7 (Meeting-025) — Adaptive Study Planner (S-07).
Rule Engine üretir; LLM yalnızca Explain.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PlannerDraftStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"   # Sprint-9: Living Plan suggestion awaiting user decision
    ACCEPTED = "accepted"
    DISCARDED = "discarded"
    REJECTED = "rejected"  # Sprint-9: user explicitly rejected suggestion


class PlannerDraft(Base):
    __tablename__ = "planner_drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[PlannerDraftStatus] = mapped_column(
        String(20), nullable=False, default=PlannerDraftStatus.DRAFT, index=True
    )
    target_exam: Mapped[str] = mapped_column(String(20), nullable=False)
    target_net: Mapped[float] = mapped_column(Float, nullable=False)
    available_days: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    available_hours: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    # plan_payload: items[] with per-item reason; summary; rationale
    plan_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Sprint 22 — adaptive | living_plan | chat
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="adaptive")
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
