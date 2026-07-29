"""M33 — Smart Question Pool Inventory & history.

Bu sprint mevcut AI/QIE motorlarını değiştirmez; sadece havuz yönetimi ve
admin görünürlüğü için ek persist katmanı sağlar.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class QuestionPoolGenerationHistory(Base):
    __tablename__ = "question_pool_generation_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    exam: Mapped[str] = mapped_column(String(32), index=True)
    subject_code: Mapped[str] = mapped_column(String(80), index=True)
    topic_code: Mapped[str] = mapped_column(String(120), index=True)
    difficulty_band: Mapped[str] = mapped_column(String(16), index=True, default="medium")

    generated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    quality_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    gemini_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Optional: for later debugging
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)


class QuestionPoolGenerationLock(Base):
    __tablename__ = "question_pool_generation_locks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lock_key: Mapped[str] = mapped_column(String(240), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    __table_args__ = (
        UniqueConstraint("lock_key", name="uq_question_pool_generation_locks_lock_key"),
    )

    @staticmethod
    def default_expires(minutes: int = 15) -> datetime:
        tz = timezone(timedelta(0))
        return datetime.now(tz=tz).astimezone(timezone.utc) + timedelta(minutes=minutes)

