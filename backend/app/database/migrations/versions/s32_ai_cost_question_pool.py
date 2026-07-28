"""Sprint M32 — question pool + AI cost counters.

Revision ID: s32_ai_cost_question_pool
Revises: s28_qie_question_intelligence
Create Date: 2026-07-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s32_ai_cost_question_pool"
down_revision = "s28_qie_question_intelligence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_pool_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("exam", sa.String(32), nullable=False),
        sa.Column("subject_code", sa.String(80), nullable=False),
        sa.Column("topic_code", sa.String(120), nullable=False),
        sa.Column("difficulty_band", sa.String(16), nullable=False, server_default="medium"),
        sa.Column("skill", sa.String(64), nullable=False, server_default=""),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column(
            "choices",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("correct_key", sa.String(8), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "qie_card",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_question_pool_cards_fingerprint", "question_pool_cards", ["fingerprint"], unique=True)
    op.create_index("ix_question_pool_cards_content_hash", "question_pool_cards", ["content_hash"])
    op.create_index("ix_question_pool_cards_exam", "question_pool_cards", ["exam"])
    op.create_index("ix_question_pool_cards_subject_code", "question_pool_cards", ["subject_code"])
    op.create_index("ix_question_pool_cards_topic_code", "question_pool_cards", ["topic_code"])


def downgrade() -> None:
    op.drop_table("question_pool_cards")
