"""Sprint X — Exam Intelligence Catalog

Revision ID: s25_exam_intelligence_catalog
Revises: s24_shared_daily_booklets
Create Date: 2026-07-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s25_exam_intelligence_catalog"
down_revision = "s24_shared_daily_booklets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ei_exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source", sa.String(40), nullable=False, server_default="official"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_ei_exams_code", "ei_exams", ["code"], unique=True)

    op.create_table(
        "ei_packs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(60), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("parent_pack_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("branch_key", sa.String(40), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["exam_id"], ["ei_exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_pack_id"], ["ei_packs.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("exam_id", "code", name="uq_ei_packs_exam_code"),
    )
    op.create_index("ix_ei_packs_exam_id", "ei_packs", ["exam_id"])
    op.create_index("ix_ei_packs_code", "ei_packs", ["code"])

    op.create_table(
        "ei_subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pack_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exam_code", sa.String(40), nullable=False),
        sa.Column("pack_code", sa.String(60), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("legacy_subject_code", sa.String(80), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["pack_id"], ["ei_packs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("pack_id", "code", name="uq_ei_subjects_pack_code"),
    )
    op.create_index("ix_ei_subjects_pack_id", "ei_subjects", ["pack_id"])
    op.create_index("ix_ei_subjects_exam_code", "ei_subjects", ["exam_code"])
    op.create_index("ix_ei_subjects_pack_code", "ei_subjects", ["pack_code"])
    op.create_index("ix_ei_subjects_code", "ei_subjects", ["code"])

    op.create_table(
        "ei_topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exam_code", sa.String(40), nullable=False),
        sa.Column("pack_code", sa.String(60), nullable=False),
        sa.Column("subject_code", sa.String(80), nullable=False),
        sa.Column("code", sa.String(160), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("importance_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("average_question_count", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("question_range_min", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("question_range_max", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("difficulty_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column(
            "estimated_study_minutes", sa.Integer(), nullable=False, server_default="30"
        ),
        sa.Column("revision_cost", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("assessment_weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column(
            "knowledge_tags",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "aliases",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("source", sa.String(40), nullable=False, server_default="estimated"),
        sa.Column("legacy_topic_code", sa.String(120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["subject_id"], ["ei_subjects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("subject_id", "code", name="uq_ei_topics_subject_code"),
    )
    op.create_index("ix_ei_topics_subject_id", "ei_topics", ["subject_id"])
    op.create_index("ix_ei_topics_exam_code", "ei_topics", ["exam_code"])
    op.create_index("ix_ei_topics_pack_code", "ei_topics", ["pack_code"])
    op.create_index("ix_ei_topics_subject_code", "ei_topics", ["subject_code"])
    op.create_index("ix_ei_topics_code", "ei_topics", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_ei_topics_code", table_name="ei_topics")
    op.drop_index("ix_ei_topics_subject_code", table_name="ei_topics")
    op.drop_index("ix_ei_topics_pack_code", table_name="ei_topics")
    op.drop_index("ix_ei_topics_exam_code", table_name="ei_topics")
    op.drop_index("ix_ei_topics_subject_id", table_name="ei_topics")
    op.drop_table("ei_topics")

    op.drop_index("ix_ei_subjects_code", table_name="ei_subjects")
    op.drop_index("ix_ei_subjects_pack_code", table_name="ei_subjects")
    op.drop_index("ix_ei_subjects_exam_code", table_name="ei_subjects")
    op.drop_index("ix_ei_subjects_pack_id", table_name="ei_subjects")
    op.drop_table("ei_subjects")

    op.drop_index("ix_ei_packs_code", table_name="ei_packs")
    op.drop_index("ix_ei_packs_exam_id", table_name="ei_packs")
    op.drop_table("ei_packs")

    op.drop_index("ix_ei_exams_code", table_name="ei_exams")
    op.drop_table("ei_exams")
