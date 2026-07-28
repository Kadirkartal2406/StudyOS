"""Sprint 23 — Exam Style Learning Dataset migration.

Revision ID: s26_exam_style_intelligence
Revises: s25_exam_intelligence_catalog
Create Date: 2026-07-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s26_exam_style_intelligence"
down_revision = "s25_exam_intelligence_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "exam_style_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("question_format", sa.String(40), nullable=False, server_default="mixed"),
        sa.Column("paragraph_words_min", sa.Integer(), nullable=False, server_default="40"),
        sa.Column("paragraph_words_max", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("stem_words_min", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("stem_words_max", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("option_words_min", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("option_words_max", sa.Integer(), nullable=False, server_default="25"),
        sa.Column("choice_count", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("distractor_strength", sa.String(20), nullable=False, server_default="strong"),
        sa.Column("bloom_default", sa.String(40), nullable=False, server_default="analyze"),
        sa.Column("language_level", sa.String(40), nullable=False, server_default="formal_tr"),
        sa.Column("reading_time_sec_avg", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("difficulty_band_default", sa.String(20), nullable=False, server_default="high"),
        sa.Column("style_rules", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("avoid_patterns", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("distractor_types", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("source", sa.String(40), nullable=False, server_default="estimated"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_exam_style_profiles_exam_code", "exam_style_profiles", ["exam_code"], unique=True)

    op.create_table(
        "exam_style_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_code", sa.String(40), nullable=False),
        sa.Column("subject_code", sa.String(80), nullable=True),
        sa.Column("skill_type", sa.String(60), nullable=False, server_default="general"),
        sa.Column("paragraph_length_avg", sa.Float(), nullable=False, server_default="0"),
        sa.Column("sentence_count_avg", sa.Float(), nullable=False, server_default="0"),
        sa.Column("distractor_pattern", sa.String(80), nullable=False, server_default="plausible"),
        sa.Column("reasoning_type", sa.String(80), nullable=False, server_default="inference"),
        sa.Column("vocabulary_level", sa.String(40), nullable=False, server_default="formal"),
        sa.Column("option_distribution", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("reading_time_sec_avg", sa.Float(), nullable=False, server_default="60"),
        sa.Column("difficulty_band", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("sample_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(40), nullable=False, server_default="estimated"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint(
            "exam_code", "subject_code", "skill_type", name="uq_exam_style_stats_exam_subject_skill"
        ),
    )
    op.create_index("ix_exam_style_stats_exam_code", "exam_style_stats", ["exam_code"])
    op.create_index("ix_exam_style_stats_subject_code", "exam_style_stats", ["subject_code"])


def downgrade() -> None:
    op.drop_index("ix_exam_style_stats_subject_code", table_name="exam_style_stats")
    op.drop_index("ix_exam_style_stats_exam_code", table_name="exam_style_stats")
    op.drop_table("exam_style_stats")
    op.drop_index("ix_exam_style_profiles_exam_code", table_name="exam_style_profiles")
    op.drop_table("exam_style_profiles")
