"""Sprint 25 — QIE: question cards + human evaluations.

Revision ID: s28_qie_question_intelligence
Revises: s27_assessment_wrong_explain
Create Date: 2026-07-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s28_qie_question_intelligence"
down_revision = "s27_assessment_wrong_explain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "topic_quiz_items",
        sa.Column(
            "qie_card",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "shared_daily_booklet_questions",
        sa.Column(
            "qie_card",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "assessment_questions",
        sa.Column(
            "qie_card",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "assessment_sessions",
        sa.Column(
            "qie_meta",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    op.create_table(
        "qie_human_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "rater_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("question_ref_type", sa.String(40), nullable=False),
        sa.Column("question_ref_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stem_preview", sa.String(280), nullable=True),
        sa.Column("exam_feel", sa.Integer(), nullable=False),
        sa.Column("language", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("option_quality", sa.Integer(), nullable=False),
        sa.Column("objective_fit", sa.Integer(), nullable=False),
        sa.Column("overall", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "qie_card_snapshot",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_qie_human_eval_ref",
        "qie_human_evaluations",
        ["question_ref_type", "question_ref_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_qie_human_eval_ref", table_name="qie_human_evaluations")
    op.drop_table("qie_human_evaluations")
    op.drop_column("assessment_sessions", "qie_meta")
    op.drop_column("assessment_questions", "qie_card")
    op.drop_column("shared_daily_booklet_questions", "qie_card")
    op.drop_column("topic_quiz_items", "qie_card")
