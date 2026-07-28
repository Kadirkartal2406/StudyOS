"""Sprint 19 — Knowledge Layer tables

Revision ID: s19_knowledge_layer
Revises: s18_assessment_engine
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s19_knowledge_layer"
down_revision = "s18_assessment_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_notebooks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("topic_name", sa.String(300), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("citation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "subject_code",
            "topic_code",
            name="uq_knowledge_notebook_user_topic",
        ),
    )
    op.create_index("ix_knowledge_notebooks_user_id", "knowledge_notebooks", ["user_id"])
    op.create_index(
        "ix_knowledge_notebooks_topic_code", "knowledge_notebooks", ["topic_code"]
    )

    op.create_table(
        "knowledge_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "notebook_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_notebooks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "study_resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("study_resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("resource_type", sa.String(40), nullable=False),
        sa.Column("health", sa.String(30), nullable=False, server_default="processing"),
        sa.Column("provider_name", sa.String(40), nullable=False, server_default="local"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("citation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "quiz_generated_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("used_by_ai", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_explain_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_quiz_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("study_resource_id", name="uq_knowledge_source_resource"),
    )
    op.create_index("ix_knowledge_sources_user_id", "knowledge_sources", ["user_id"])
    op.create_index(
        "ix_knowledge_sources_notebook_id", "knowledge_sources", ["notebook_id"]
    )
    op.create_index("ix_knowledge_sources_health", "knowledge_sources", ["health"])

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notebook_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_notebooks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("ord_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_hint", sa.String(80), nullable=True),
        sa.Column("token_estimate", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding", postgresql.JSONB(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_knowledge_chunks_notebook_id", "knowledge_chunks", ["notebook_id"]
    )
    op.create_index("ix_knowledge_chunks_topic_code", "knowledge_chunks", ["topic_code"])

    op.create_table(
        "knowledge_citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notebook_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_notebooks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "chunk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_chunks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_sources.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("used_by", sa.String(40), nullable=False),
        sa.Column("source_title", sa.String(300), nullable=True),
        sa.Column("quote", sa.Text(), nullable=True),
        sa.Column("page_hint", sa.String(80), nullable=True),
        sa.Column("relevance", sa.Float(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_knowledge_citations_notebook_id", "knowledge_citations", ["notebook_id"]
    )
    op.create_index(
        "ix_knowledge_citations_topic_code", "knowledge_citations", ["topic_code"]
    )


def downgrade() -> None:
    op.drop_table("knowledge_citations")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_sources")
    op.drop_table("knowledge_notebooks")
