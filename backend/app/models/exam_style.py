"""
Sprint 23 — Exam Style Learning Dataset (telif-safe).

Resmi sınav SORU METİNLERİ asla saklanmaz.
Yalnızca istatistiksel stil özellikleri + üretim profilleri.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ExamStyleProfile(Base):
    """Sınav bazlı üretim stili (prompt enjeksiyonu)."""

    __tablename__ = "exam_style_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    # paragraph | short_stem | mixed
    question_format: Mapped[str] = mapped_column(String(40), nullable=False, default="mixed")
    paragraph_words_min: Mapped[int] = mapped_column(Integer, nullable=False, default=40)
    paragraph_words_max: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    stem_words_min: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    stem_words_max: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    option_words_min: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    option_words_max: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    choice_count: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    # weak | balanced | strong
    distractor_strength: Mapped[str] = mapped_column(String(20), nullable=False, default="strong")
    # remember | understand | apply | analyze | evaluate
    bloom_default: Mapped[str] = mapped_column(String(40), nullable=False, default="analyze")
    language_level: Mapped[str] = mapped_column(String(40), nullable=False, default="formal_tr")
    reading_time_sec_avg: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    difficulty_band_default: Mapped[str] = mapped_column(String(20), nullable=False, default="high")
    # free-form rules for prompt
    style_rules: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    avoid_patterns: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    distractor_types: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="estimated")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class ExamStyleStat(Base):
    """Konu/beceri bazlı istatistik — soru metni YOK."""

    __tablename__ = "exam_style_stats"
    __table_args__ = (
        UniqueConstraint(
            "exam_code",
            "subject_code",
            "skill_type",
            name="uq_exam_style_stats_exam_subject_skill",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subject_code: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    skill_type: Mapped[str] = mapped_column(String(60), nullable=False, default="general")
    paragraph_length_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sentence_count_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    distractor_pattern: Mapped[str] = mapped_column(String(80), nullable=False, default="plausible")
    reasoning_type: Mapped[str] = mapped_column(String(80), nullable=False, default="inference")
    vocabulary_level: Mapped[str] = mapped_column(String(40), nullable=False, default="formal")
    option_distribution: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    reading_time_sec_avg: Mapped[float] = mapped_column(Float, nullable=False, default=60.0)
    difficulty_band: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # estimated | official_stats — never raw_question
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="estimated")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
