"""
Sprint 19 — Knowledge Layer models (LOS §12).
Decision / Confidence / Policy üretmez; yalnızca bilgi sağlar.
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


class KnowledgeHealth(StrEnum):
    PROCESSING = "processing"
    INDEXED = "indexed"
    READY = "ready"
    NEEDS_UPDATE = "needs_update"
    ERROR = "error"


class CitationUsedBy(StrEnum):
    EXPLAIN = "explain"
    QUIZ = "quiz"
    ASSESSMENT = "assessment"
    OTHER = "other"


class KnowledgeNotebook(Base):
    """Topic başına tek Notebook (Knowledge Space index)."""

    __tablename__ = "knowledge_notebooks"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "subject_code",
            "topic_code",
            name="uq_knowledge_notebook_user_topic",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    topic_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    citation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    sources: Mapped[list[KnowledgeSource]] = relationship(
        "KnowledgeSource", back_populates="notebook", cascade="all, delete-orphan"
    )
    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        "KnowledgeChunk", back_populates="notebook", cascade="all, delete-orphan"
    )
    citations: Mapped[list[KnowledgeCitation]] = relationship(
        "KnowledgeCitation", back_populates="notebook", cascade="all, delete-orphan"
    )


class KnowledgeSource(Base):
    """StudyResource ↔ Knowledge Layer köprüsü."""

    __tablename__ = "knowledge_sources"
    __table_args__ = (
        UniqueConstraint(
            "study_resource_id",
            name="uq_knowledge_source_resource",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_notebooks.id", ondelete="CASCADE"),
        index=True,
    )
    study_resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_resources.id", ondelete="CASCADE"),
        index=True,
    )
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)
    health: Mapped[str] = mapped_column(
        String(30), nullable=False, default=KnowledgeHealth.PROCESSING, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(40), nullable=False, default="local")
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    citation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quiz_generated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    used_by_ai: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    last_explain_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_quiz_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    notebook: Mapped[KnowledgeNotebook] = relationship(
        "KnowledgeNotebook", back_populates="sources"
    )
    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        "KnowledgeChunk", back_populates="source", cascade="all, delete-orphan"
    )


class KnowledgeChunk(Base):
    """Topic-scoped metin parçası."""

    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_notebooks.id", ondelete="CASCADE"),
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_sources.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    ord_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_hint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    token_estimate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Basit vektör (local); provider-specific metadata JSONB
    embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    notebook: Mapped[KnowledgeNotebook] = relationship(
        "KnowledgeNotebook", back_populates="chunks"
    )
    source: Mapped[KnowledgeSource] = relationship(
        "KnowledgeSource", back_populates="chunks"
    )


class KnowledgeCitation(Base):
    """AI çıktısının kaynak referansı."""

    __tablename__ = "knowledge_citations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_notebooks.id", ondelete="CASCADE"),
        index=True,
    )
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_chunks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    used_by: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_hint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    notebook: Mapped[KnowledgeNotebook] = relationship(
        "KnowledgeNotebook", back_populates="citations"
    )
