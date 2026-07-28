"""
StudyOS — Exam Intelligence Catalog (Sprint X)

Read-only resmi sınav ağacı: Exam → Pack → Subject → Topic.
Evidence / Confidence / Assessment tablolarıyla karışmaz.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

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


class EiExam(Base):
    """Üst seviye sınav (YKS, KPSS, LGS, …)."""

    __tablename__ = "ei_exams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="official")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    packs: Mapped[list[EiPack]] = relationship(
        "EiPack",
        back_populates="exam",
        cascade="all, delete-orphan",
        order_by="EiPack.display_order",
    )


class EiPack(Base):
    """Sınav paketi / alan (TYT, AYT Sayısal, KPSS Lisans, …)."""

    __tablename__ = "ei_packs"
    __table_args__ = (
        UniqueConstraint("exam_id", "code", name="uq_ei_packs_exam_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ei_exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    parent_pack_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ei_packs.id", ondelete="SET NULL"),
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Profile branch eşlemesi (sayisal / ea / sozel / lisans / …)
    branch_key: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    exam: Mapped[EiExam] = relationship("EiExam", back_populates="packs")
    subjects: Mapped[list[EiSubject]] = relationship(
        "EiSubject",
        back_populates="pack",
        cascade="all, delete-orphan",
        order_by="EiSubject.display_order",
    )


class EiSubject(Base):
    """Ders — çalışma birimi değil; Topic'lerin üstü."""

    __tablename__ = "ei_subjects"
    __table_args__ = (
        UniqueConstraint("pack_id", "code", name="uq_ei_subjects_pack_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ei_packs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam_code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    pack_code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Eski subject_catalog.code ile köprü (Decision Engine dokunulmaz)
    legacy_subject_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    pack: Mapped[EiPack] = relationship("EiPack", back_populates="subjects")
    topics: Mapped[list[EiTopic]] = relationship(
        "EiTopic",
        back_populates="subject",
        cascade="all, delete-orphan",
        order_by="EiTopic.display_order",
    )


class EiTopic(Base):
    """Tek çalışma birimi + Decision Engine metadata."""

    __tablename__ = "ei_topics"
    __table_args__ = (
        UniqueConstraint("subject_id", "code", name="uq_ei_topics_subject_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ei_subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam_code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    pack_code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    subject_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    average_question_count: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    question_range_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    question_range_max: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    difficulty_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    estimated_study_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    revision_cost: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    assessment_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    knowledge_tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    aliases: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    # official | estimated
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="estimated")
    # Eski topic_catalog.code köprüsü
    legacy_topic_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    subject: Mapped[EiSubject] = relationship("EiSubject", back_populates="topics")
