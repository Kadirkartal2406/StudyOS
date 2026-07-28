"""Sprint 24 — Shared daily booklets (one per exam/date)

Revision ID: s24_shared_daily_booklets
Revises: s23_daily_booklet
Create Date: 2026-07-25
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s24_shared_daily_booklets"
down_revision = "s23_daily_booklet"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shared_daily_booklets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_type", sa.String(40), nullable=False),
        sa.Column("branch_key", sa.String(40), nullable=False, server_default=""),
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("requested_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "section_plan",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("generation_progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "exam_type",
            "branch_key",
            "challenge_date",
            name="uq_shared_daily_booklet_exam_branch_date",
        ),
    )
    op.create_index(
        "ix_shared_daily_booklets_exam_type",
        "shared_daily_booklets",
        ["exam_type"],
    )
    op.create_index(
        "ix_shared_daily_booklets_challenge_date",
        "shared_daily_booklets",
        ["challenge_date"],
    )

    op.create_table(
        "shared_daily_booklet_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "booklet_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("shared_daily_booklets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ord_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(), nullable=False),
        sa.Column("correct_key", sa.String(1), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("subject_code", sa.String(100), nullable=True),
        sa.Column("topic_code", sa.String(200), nullable=True),
    )
    op.create_index(
        "ix_shared_daily_booklet_questions_booklet_id",
        "shared_daily_booklet_questions",
        ["booklet_id"],
    )


def downgrade() -> None:
    op.drop_table("shared_daily_booklet_questions")
    op.drop_table("shared_daily_booklets")
