"""Question pool ORM — M32 reusable generated questions."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class QuestionPoolCard(Base):
    __tablename__ = "question_pool_cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    exam: Mapped[str] = mapped_column(String(32), index=True)
    subject_code: Mapped[str] = mapped_column(String(80), index=True)
    topic_code: Mapped[str] = mapped_column(String(120), index=True)
    difficulty_band: Mapped[str] = mapped_column(String(16), default="medium")
    skill: Mapped[str] = mapped_column(String(64), default="")
    stem: Mapped[str] = mapped_column(Text)
    choices: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    correct_key: Mapped[str] = mapped_column(String(8))
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    qie_card: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
