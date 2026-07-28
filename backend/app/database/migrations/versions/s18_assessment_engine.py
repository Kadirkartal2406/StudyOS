"""Sprint 18 — Assessment Engine tables

Revision ID: s18_assessment_engine
Revises: s14_topic_quiz_generations
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s18_assessment_engine"
down_revision = "s14_topic_quiz_generations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assessment_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exam_type", sa.String(40), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("subject_code", sa.String(100), nullable=True),
        sa.Column("topic_code", sa.String(200), nullable=True),
        sa.Column("subject_name", sa.String(200), nullable=True),
        sa.Column("topic_name", sa.String(300), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("requested_count", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("challenge_date", sa.Date(), nullable=True),
        sa.Column(
            "quiz_generation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("topic_quiz_generations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("correct_count", sa.Integer(), nullable=True),
        sa.Column("wrong_count", sa.Integer(), nullable=True),
        sa.Column("blank_count", sa.Integer(), nullable=True),
        sa.Column("accuracy", sa.Float(), nullable=True),
        sa.Column("commentary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_assessment_sessions_user_id", "assessment_sessions", ["user_id"])
    op.create_index("ix_assessment_sessions_exam_type", "assessment_sessions", ["exam_type"])
    op.create_index("ix_assessment_sessions_kind", "assessment_sessions", ["kind"])
    op.create_index("ix_assessment_sessions_status", "assessment_sessions", ["status"])
    op.create_index(
        "ix_assessment_sessions_challenge_date", "assessment_sessions", ["challenge_date"]
    )
    op.create_index(
        "ix_assessment_sessions_quiz_generation_id",
        "assessment_sessions",
        ["quiz_generation_id"],
    )

    op.create_table(
        "assessment_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quiz_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ord_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correct_key", sa.String(1), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("selected_key", sa.String(1), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("subject_code", sa.String(100), nullable=True),
        sa.Column("topic_code", sa.String(200), nullable=True),
    )
    op.create_index(
        "ix_assessment_questions_session_id", "assessment_questions", ["session_id"]
    )

    op.create_table(
        "daily_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exam_type", sa.String(40), nullable=False),
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessment_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "title", sa.String(200), nullable=False, server_default="Günün Denemesi"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "exam_type",
            "challenge_date",
            name="uq_daily_challenge_user_exam_date",
        ),
    )
    op.create_index("ix_daily_challenges_user_id", "daily_challenges", ["user_id"])
    op.create_index("ix_daily_challenges_exam_type", "daily_challenges", ["exam_type"])
    op.create_index(
        "ix_daily_challenges_challenge_date", "daily_challenges", ["challenge_date"]
    )

    op.create_table(
        "estimated_score_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exam_type", sa.String(40), nullable=False),
        sa.Column("estimated_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "estimated_success_pct", sa.Float(), nullable=False, server_default="0"
        ),
        sa.Column(
            "estimated_rank_pct", sa.Float(), nullable=False, server_default="50"
        ),
        sa.Column("peer_sample_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("strongest_subject", sa.String(200), nullable=True),
        sa.Column("weakest_subject", sa.String(200), nullable=True),
        sa.Column("commentary", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_estimated_score_snapshots_user_id",
        "estimated_score_snapshots",
        ["user_id"],
    )
    op.create_index(
        "ix_estimated_score_snapshots_exam_type",
        "estimated_score_snapshots",
        ["exam_type"],
    )


def downgrade() -> None:
    op.drop_table("estimated_score_snapshots")
    op.drop_table("daily_challenges")
    op.drop_table("assessment_questions")
    op.drop_table("assessment_sessions")
