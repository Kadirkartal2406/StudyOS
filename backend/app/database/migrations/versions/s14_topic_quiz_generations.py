"""Sprint 14 — topic_quiz_generations + topic_quiz_items

Revision ID: s14_topic_quiz_generations
Revises: ai_phase1_002
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s14_topic_quiz_generations"
down_revision = "ai_phase1_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topic_quiz_generations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("subject_name", sa.String(200), nullable=True),
        sa.Column("topic_name", sa.String(300), nullable=True),
        sa.Column("requested_count", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("exam_type", sa.String(40), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("provider", sa.String(40), nullable=True),
        sa.Column("model", sa.String(80), nullable=True),
        sa.Column("prompt_fingerprint", sa.String(64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=True),
        sa.Column("wrong_count", sa.Integer(), nullable=True),
        sa.Column("blank_count", sa.Integer(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index(
        "ix_topic_quiz_generations_user_id", "topic_quiz_generations", ["user_id"]
    )
    op.create_index(
        "ix_topic_quiz_generations_subject_code",
        "topic_quiz_generations",
        ["subject_code"],
    )
    op.create_index(
        "ix_topic_quiz_generations_topic_code",
        "topic_quiz_generations",
        ["topic_code"],
    )
    op.create_index(
        "ix_topic_quiz_generations_status", "topic_quiz_generations", ["status"]
    )

    op.create_table(
        "topic_quiz_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "generation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("topic_quiz_generations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ord_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(), nullable=False),
        sa.Column("correct_key", sa.String(1), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("selected_key", sa.String(1), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
    )
    op.create_index(
        "ix_topic_quiz_items_generation_id", "topic_quiz_items", ["generation_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_topic_quiz_items_generation_id", table_name="topic_quiz_items")
    op.drop_table("topic_quiz_items")
    op.drop_index("ix_topic_quiz_generations_status", table_name="topic_quiz_generations")
    op.drop_index(
        "ix_topic_quiz_generations_topic_code", table_name="topic_quiz_generations"
    )
    op.drop_index(
        "ix_topic_quiz_generations_subject_code", table_name="topic_quiz_generations"
    )
    op.drop_index("ix_topic_quiz_generations_user_id", table_name="topic_quiz_generations")
    op.drop_table("topic_quiz_generations")
