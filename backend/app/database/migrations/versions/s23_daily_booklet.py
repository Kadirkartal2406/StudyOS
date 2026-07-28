"""Sprint 23 — Daily booklet (full exam)

Revision ID: s23_daily_booklet
Revises: s22_study_ux_overhaul
Create Date: 2026-07-25
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s23_daily_booklet"
down_revision = "s22_study_ux_overhaul"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "assessment_sessions",
        sa.Column("is_booklet", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "assessment_sessions",
        sa.Column(
            "section_plan",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "assessment_sessions",
        sa.Column(
            "generation_progress",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # Collapse daily_challenges to one row per user/exam/date
    op.execute(
        """
        DELETE FROM daily_challenges a
        USING daily_challenges b
        WHERE a.ctid < b.ctid
          AND a.user_id = b.user_id
          AND a.exam_type = b.exam_type
          AND a.challenge_date = b.challenge_date
        """
    )
    op.drop_constraint(
        "uq_daily_challenge_user_exam_date_subject",
        "daily_challenges",
        type_="unique",
    )
    op.execute(
        "UPDATE daily_challenges SET subject_code = 'booklet'"
    )
    op.create_unique_constraint(
        "uq_daily_challenge_user_exam_date",
        "daily_challenges",
        ["user_id", "exam_type", "challenge_date"],
    )

    # Booklet scores use subject_code='booklet'
    op.execute(
        """
        DELETE FROM daily_challenge_scores a
        USING daily_challenge_scores b
        WHERE a.ctid < b.ctid
          AND a.user_id = b.user_id
          AND a.exam_type = b.exam_type
          AND a.challenge_date = b.challenge_date
          AND a.subject_code = b.subject_code
        """
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_daily_challenge_user_exam_date",
        "daily_challenges",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_daily_challenge_user_exam_date_subject",
        "daily_challenges",
        ["user_id", "exam_type", "challenge_date", "subject_code"],
    )
    op.drop_column("assessment_sessions", "generation_progress")
    op.drop_column("assessment_sessions", "section_plan")
    op.drop_column("assessment_sessions", "is_booklet")
