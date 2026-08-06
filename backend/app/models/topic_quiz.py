"""
Sprint 14 — Topic Quiz Generation models.
LOS §10: Content generation bound to Topic; Evidence producer.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class QuizGenerationStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"
    SUBMITTED = "submitted"


class QuizDifficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TopicQuizGeneration(Base):
    """Bir Topic için üretilmiş quiz oturumu (Intent → LLM → Quality Gate)."""

    __tablename__ = "topic_quiz_generations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    subject_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    topic_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, default=QuizDifficulty.MEDIUM
    )
    exam_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=QuizGenerationStatus.PENDING, index=True
    )
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prompt_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Soft quality stats
    raw_item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Submit sonuçları
    correct_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wrong_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blank_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    items: Mapped[list[TopicQuizItem]] = relationship(
        "TopicQuizItem",
        back_populates="generation",
        cascade="all, delete-orphan",
        order_by="TopicQuizItem.ord_index",
    )


class TopicQuizItem(Base):
    """Kalite kapısından geçmiş tek çoktan seçmeli soru."""

    __tablename__ = "topic_quiz_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_quiz_generations.id", ondelete="CASCADE"),
        index=True,
    )
    ord_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    # {"A": "...", "B": "...", "C": "...", "D": "..."}
    choices: Mapped[dict] = mapped_column(JSONB, nullable=False)
    correct_key: Mapped[str] = mapped_column(String(1), nullable=False)  # A|B|C|D
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Sprint 25 — internal QIE QuestionCard (never exposed on public quiz APIs)
    qie_card: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Sprint 26 / EAE interaction
    eae_interaction: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Kullanıcı cevabı (submit sonrası)
    selected_key: Mapped[str | None] = mapped_column(String(1), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    generation: Mapped[TopicQuizGeneration] = relationship(
        "TopicQuizGeneration", back_populates="items"
    )
