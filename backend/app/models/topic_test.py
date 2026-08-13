"""Topic Test Catalog — published weekly topic tests (immutable after publish).

Separate from per-user topic_quiz_generations. User start/submit creates attempts
without calling Gemini.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TopicTestStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    FAILED = "failed"


class TopicTestDifficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TopicTestAttemptStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"


class TopicTest(Base):
    """One published (or draft) weekly test for a topic+difficulty."""

    __tablename__ = "topic_tests"
    __table_args__ = (
        UniqueConstraint(
            "exam",
            "subject_code",
            "topic_code",
            "week_id",
            "difficulty",
            name="uq_topic_tests_week_difficulty",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    subject_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    topic_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    week_id: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TopicTestStatus.DRAFT, index=True
    )
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    published_at: Mapped[datetime | None] = mapped_column(
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

    items: Mapped[list[TopicTestItem]] = relationship(
        "TopicTestItem",
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="TopicTestItem.ord_index",
    )
    attempts: Mapped[list[TopicTestAttempt]] = relationship(
        "TopicTestAttempt",
        back_populates="test",
        cascade="all, delete-orphan",
    )


class TopicTestItem(Base):
    """Immutable snapshot of one question in a published test."""

    __tablename__ = "topic_test_items"
    __table_args__ = (
        UniqueConstraint("test_id", "ord_index", name="uq_topic_test_items_ord"),
        # A pool card may appear in at most one catalog test (any week/difficulty).
        UniqueConstraint("pool_card_id", name="uq_topic_test_items_pool_card_global"),
        UniqueConstraint("content_hash", name="uq_topic_test_items_content_hash_global"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ord_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pool_card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("question_pool_cards.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[dict] = mapped_column(JSONB, nullable=False)
    correct_key: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    qie_card: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    test: Mapped[TopicTest] = relationship("TopicTest", back_populates="items")


class TopicTestAttempt(Base):
    """User solving a published catalog test (no Gemini)."""

    __tablename__ = "topic_test_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TopicTestAttemptStatus.IN_PROGRESS,
        index=True,
    )
    correct_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wrong_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blank_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accuracy_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    test: Mapped[TopicTest] = relationship("TopicTest", back_populates="attempts")
    answers: Mapped[list[TopicTestAttemptAnswer]] = relationship(
        "TopicTestAttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class TopicTestAttemptAnswer(Base):
    __tablename__ = "topic_test_attempt_answers"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "item_id", name="uq_topic_test_attempt_answers_item"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_test_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_test_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_key: Mapped[str | None] = mapped_column(String(1), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    attempt: Mapped[TopicTestAttempt] = relationship(
        "TopicTestAttempt", back_populates="answers"
    )
