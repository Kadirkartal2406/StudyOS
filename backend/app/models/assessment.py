"""
Sprint 18 â Assessment Engine models (LOS Â§11 Sense layer).
Decision / Living Plan Ã¼retmez; Evidence Ã¼retir.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
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


class AssessmentKind(StrEnum):
    INITIAL_CALIBRATION = "initial_calibration"
    DAILY_CHALLENGE = "daily_challenge"
    BRANCH_QUESTION = "branch_question"


class AssessmentSessionStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"
    SUBMITTED = "submitted"


class AssessmentSession(Base):
    """Tek assessment oturumu â Topic Quiz generation'a kÃ¶prÃ¼."""

    __tablename__ = "assessment_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subject_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    topic_code: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    subject_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    topic_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AssessmentSessionStatus.PENDING, index=True
    )
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    challenge_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    # Sprint 23 â full daily booklet
    is_booklet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    section_plan: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generation_progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Sprint 14 bridge (single-subject sessions; booklet may leave null)
    quiz_generation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_quiz_generations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # Sprint 25 â adaptive calibration / QIE session metadata (internal)
    qie_meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    correct_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wrong_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blank_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    commentary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    questions: Mapped[list[AssessmentQuestion]] = relationship(
        "AssessmentQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="AssessmentQuestion.ord_index",
    )


class AssessmentQuestion(Base):
    """Assessment sorusu â quiz item kopyasÄ± / mirror (submit snapshot)."""

    __tablename__ = "assessment_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    quiz_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    ord_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[dict] = mapped_column(JSONB, nullable=False)
    correct_key: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Sprint 23 M23.7 â lazy wrong-answer explain cache (JSON text)
    wrong_explain: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_key: Mapped[str | None] = mapped_column(String(1), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    topic_code: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Sprint 25 â internal QIE card
    qie_card: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Sprint 26 / EAE interaction
    eae_interaction: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    session: Mapped[AssessmentSession] = relationship(
        "AssessmentSession", back_populates="questions"
    )


class SharedDailyBooklet(Base):
    """SÄ±nav + gÃ¼n (+ opsiyonel branch) iÃ§in ortak kitapÃ§Ä±k â kullanÄ±cÄ± baÅÄ±na Ã¼retilmez."""

    __tablename__ = "shared_daily_booklets"
    __table_args__ = (
        UniqueConstraint(
            "exam_type",
            "branch_key",
            "challenge_date",
            name="uq_shared_daily_booklet_exam_branch_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    branch_key: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    challenge_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    section_plan: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generation_progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_finalized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    questions: Mapped[list[SharedDailyBookletQuestion]] = relationship(
        "SharedDailyBookletQuestion",
        back_populates="booklet",
        cascade="all, delete-orphan",
        order_by="SharedDailyBookletQuestion.ord_index",
    )


class SharedDailyBookletQuestion(Base):
    """Ortak gÃ¼nlÃ¼k kitapÃ§Ä±k sorusu."""

    __tablename__ = "shared_daily_booklet_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    booklet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_daily_booklets.id", ondelete="CASCADE"),
        index=True,
    )
    ord_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[dict] = mapped_column(JSONB, nullable=False)
    correct_key: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    topic_code: Mapped[str | None] = mapped_column(String(200), nullable=True)
    qie_card: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    eae_interaction: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    booklet: Mapped[SharedDailyBooklet] = relationship(
        "SharedDailyBooklet", back_populates="questions"
    )


class DailyChallenge(Base):
    """KullanÄ±cÄ± + sÄ±nav + gÃ¼n iÃ§in oturum kaydÄ± (ortak kitapÃ§Ä±ktan klon)."""

    __tablename__ = "daily_challenges"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "exam_type",
            "challenge_date",
            name="uq_daily_challenge_user_exam_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    challenge_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # Legacy per-subject field; booklet rows use subject_code='booklet'
    subject_code: Mapped[str] = mapped_column(
        String(100), nullable=False, default="booklet", index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="available", index=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessment_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="GÃ¼nÃ¼n Denemesi")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class DailyChallengeScore(Base):
    """GÃ¼nÃ¼n denemesi skorlarÄ± â sosyal sÄ±ralama (Sprint 22)."""

    __tablename__ = "daily_challenge_scores"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "exam_type",
            "challenge_date",
            "subject_code",
            name="uq_daily_challenge_score_user_day_subject",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    challenge_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    nickname: Mapped[str] = mapped_column(String(120), nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blank_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    studyos_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    studyos_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    osym_estimations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class EstimatedScoreSnapshot(Base):
    """Ä°statistiksel tahmini puan / sÄ±ralama â gerÃ§ek ÃSYM deÄil."""

    __tablename__ = "estimated_score_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    estimated_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_success_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_rank_pct: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    peer_sample_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    strongest_subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    weakest_subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    commentary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class DailyChallengeStatistics(Base):
    """Günün denemesi için saat 22:30'da finalize edilen resmi istatistikler."""

    __tablename__ = "daily_challenge_statistics"
    __table_args__ = (
        UniqueConstraint(
            "exam_type",
            "challenge_date",
            name="uq_daily_challenge_statistics_exam_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    challenge_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    participant_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    subject_averages: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    subject_std_devs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    score_mean: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    score_std_dev: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class OsymCoefficients(Base):
    """Geçmiş yıllara ait ÖSYM puan formülü katsayıları."""

    __tablename__ = "osym_coefficients"
    __table_args__ = (
        UniqueConstraint(
            "exam_type",
            "year",
            name="uq_osym_coefficients_exam_year",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    base_point: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    subject_weights: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    subject_means: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    subject_std_devs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
