"""Sprint 22 — Study UX Overhaul

Revision ID: s22_study_ux_overhaul
Revises: s21_rc_beta_ops
Create Date: 2026-07-25
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s22_study_ux_overhaul"
down_revision = "s21_rc_beta_ops"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Study sessions: mode / phase / break telemetry ─────────────
    op.add_column(
        "study_sessions",
        sa.Column("mode", sa.String(length=20), nullable=False, server_default="pomodoro"),
    )
    op.add_column(
        "study_sessions",
        sa.Column("phase", sa.String(length=20), nullable=False, server_default="focus"),
    )
    op.add_column(
        "study_sessions",
        sa.Column("actual_break_minutes", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "study_sessions",
        sa.Column("break_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "study_sessions",
        sa.Column(
            "break_segments",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.alter_column(
        "study_sessions",
        "planned_duration_minutes",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # ── Daily challenge: per-subject ───────────────────────────────
    op.add_column(
        "daily_challenges",
        sa.Column("subject_code", sa.String(length=100), nullable=True),
    )
    op.execute(
        "UPDATE daily_challenges SET subject_code = 'unknown' WHERE subject_code IS NULL"
    )
    op.alter_column(
        "daily_challenges",
        "subject_code",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.drop_constraint("uq_daily_challenge_user_exam_date", "daily_challenges", type_="unique")
    op.create_unique_constraint(
        "uq_daily_challenge_user_exam_date_subject",
        "daily_challenges",
        ["user_id", "exam_type", "challenge_date", "subject_code"],
    )
    op.create_index(
        "ix_daily_challenges_subject_code",
        "daily_challenges",
        ["subject_code"],
    )

    # ── Leaderboard scores ─────────────────────────────────────────
    op.create_table(
        "daily_challenge_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exam_type", sa.String(40), nullable=False),
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("nickname", sa.String(120), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blank_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accuracy", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "exam_type",
            "challenge_date",
            "subject_code",
            name="uq_daily_challenge_score_user_day_subject",
        ),
    )
    op.create_index(
        "ix_daily_challenge_scores_day_subject",
        "daily_challenge_scores",
        ["challenge_date", "subject_code", "exam_type"],
    )
    op.create_index(
        "ix_daily_challenge_scores_user",
        "daily_challenge_scores",
        ["user_id"],
    )

    # ── Chat plan proposals marker on drafts ───────────────────────
    op.add_column(
        "planner_drafts",
        sa.Column("source", sa.String(length=40), nullable=False, server_default="adaptive"),
    )
    op.add_column(
        "planner_drafts",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("planner_drafts", "conversation_id")
    op.drop_column("planner_drafts", "source")
    op.drop_index("ix_daily_challenge_scores_user", table_name="daily_challenge_scores")
    op.drop_index("ix_daily_challenge_scores_day_subject", table_name="daily_challenge_scores")
    op.drop_table("daily_challenge_scores")
    op.drop_index("ix_daily_challenges_subject_code", table_name="daily_challenges")
    op.drop_constraint(
        "uq_daily_challenge_user_exam_date_subject", "daily_challenges", type_="unique"
    )
    op.create_unique_constraint(
        "uq_daily_challenge_user_exam_date",
        "daily_challenges",
        ["user_id", "exam_type", "challenge_date"],
    )
    op.drop_column("daily_challenges", "subject_code")
    op.drop_column("study_sessions", "break_segments")
    op.drop_column("study_sessions", "break_started_at")
    op.drop_column("study_sessions", "actual_break_minutes")
    op.drop_column("study_sessions", "phase")
    op.drop_column("study_sessions", "mode")
    op.alter_column(
        "study_sessions",
        "planned_duration_minutes",
        existing_type=sa.Integer(),
        nullable=False,
    )
