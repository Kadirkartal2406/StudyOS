"""
StudyOS — Learning Profile (Sprint-3.0)
Student hub + multi-exam targets + subject catalog (S-02/S-03/S-34).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class JourneyStage(StrEnum):
    """M1 — RuleEngine günceller; LLM yalnızca yorumlar."""

    NEW_USER = "new_user"
    ONBOARDING = "onboarding"
    LEARNING = "learning"
    CONSISTENT = "consistent"
    ADVANCED = "advanced"


class BaselineLevel(StrEnum):
    UNKNOWN = "unknown"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Student(Base):
    """Learning Profile hub — 1:1 User (A1)."""

    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    journey_stage: Mapped[str] = mapped_column(
        String(30), nullable=False, default=JourneyStage.NEW_USER, index=True
    )
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    onboarding_skipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    daily_study_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    available_days: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    available_hours: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    baseline_level: Mapped[str] = mapped_column(
        String(30), nullable=False, default=BaselineLevel.UNKNOWN
    )
    baseline_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Sprint-3.1.A — Active Exam (UI çalışma bağlamı; Primary'den ayrı)
    active_exam_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )

    # ── LOS Module 3: Observation Mode ──────────────────────────────
    # 'observing' → 'calibrating' → 'full'
    observation_state: Mapped[str] = mapped_column(
        String(20), nullable=False, default="observing", index=True
    )
    observation_gates: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    observation_entered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    observation_exited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class ExamTarget(Base):
    """Multi-exam hedefler — 1:N (B1)."""

    __tablename__ = "exam_targets"
    __table_args__ = (UniqueConstraint("user_id", "exam_type", name="uq_exam_targets_user_type"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exam_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    target_net: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_university: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class SubjectCatalog(Base):
    """Sistem müfredat kataloğu (C1) — seed."""

    __tablename__ = "subject_catalog"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    exam_types: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    section: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )


class TopicCatalog(Base):
    """Konu kataloğu (Sprint-3.2.A) — Subject altında Topic; identity = code."""

    __tablename__ = "topic_catalog"
    __table_args__ = (
        UniqueConstraint("subject_code", "code", name="uq_topic_catalog_subject_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    subject_code: Mapped[str] = mapped_column(
        String(80),
        ForeignKey("subject_catalog.code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )


class UserSubject(Base):
    """Kullanıcı ders ataması — dual-write name + code (C1)."""

    __tablename__ = "user_subjects"
    __table_args__ = (UniqueConstraint("user_id", "subject_code", name="uq_user_subjects_user_code"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="onboarding")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
