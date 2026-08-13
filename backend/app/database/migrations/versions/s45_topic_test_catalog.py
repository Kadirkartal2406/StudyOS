"""s45_topic_test_catalog

Revision ID: s45_topic_test_catalog
Revises: s44_eae_node_metadata
Create Date: 2026-08-13 19:20:00.000000

Published weekly topic tests (easy/medium/hard × 10 questions) + user attempts.
Does not modify topic_quiz_generations or question_pool_cards schema beyond FKs.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "s45_topic_test_catalog"
down_revision: Union[str, None] = "s44_eae_node_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "topic_tests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("exam", sa.String(40), nullable=False),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("subject_name", sa.String(200), nullable=True),
        sa.Column("topic_name", sa.String(300), nullable=True),
        sa.Column("week_id", sa.String(16), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("question_count", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
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
            "exam",
            "subject_code",
            "topic_code",
            "week_id",
            "difficulty",
            name="uq_topic_tests_week_difficulty",
        ),
    )
    op.create_index("ix_topic_tests_exam", "topic_tests", ["exam"])
    op.create_index("ix_topic_tests_subject_code", "topic_tests", ["subject_code"])
    op.create_index("ix_topic_tests_topic_code", "topic_tests", ["topic_code"])
    op.create_index("ix_topic_tests_week_id", "topic_tests", ["week_id"])
    op.create_index("ix_topic_tests_difficulty", "topic_tests", ["difficulty"])
    op.create_index("ix_topic_tests_status", "topic_tests", ["status"])

    op.create_table(
        "topic_test_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "test_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("topic_tests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ord_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "pool_card_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("question_pool_cards.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(), nullable=False),
        sa.Column("correct_key", sa.String(1), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "qie_card",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.UniqueConstraint("test_id", "ord_index", name="uq_topic_test_items_ord"),
        sa.UniqueConstraint(
            "pool_card_id", name="uq_topic_test_items_pool_card_global"
        ),
        sa.UniqueConstraint(
            "content_hash", name="uq_topic_test_items_content_hash_global"
        ),
    )
    op.create_index("ix_topic_test_items_test_id", "topic_test_items", ["test_id"])
    op.create_index(
        "ix_topic_test_items_pool_card_id", "topic_test_items", ["pool_card_id"]
    )
    op.create_index(
        "ix_topic_test_items_content_hash", "topic_test_items", ["content_hash"]
    )

    op.create_table(
        "topic_test_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("topic_tests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="in_progress"
        ),
        sa.Column("correct_count", sa.Integer(), nullable=True),
        sa.Column("wrong_count", sa.Integer(), nullable=True),
        sa.Column("blank_count", sa.Integer(), nullable=True),
        sa.Column("accuracy_pct", sa.Float(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_topic_test_attempts_user_id", "topic_test_attempts", ["user_id"])
    op.create_index("ix_topic_test_attempts_test_id", "topic_test_attempts", ["test_id"])
    op.create_index("ix_topic_test_attempts_status", "topic_test_attempts", ["status"])

    op.create_table(
        "topic_test_attempt_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("topic_test_attempts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("topic_test_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("selected_key", sa.String(1), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.UniqueConstraint(
            "attempt_id", "item_id", name="uq_topic_test_attempt_answers_item"
        ),
    )
    op.create_index(
        "ix_topic_test_attempt_answers_attempt_id",
        "topic_test_attempt_answers",
        ["attempt_id"],
    )
    op.create_index(
        "ix_topic_test_attempt_answers_item_id",
        "topic_test_attempt_answers",
        ["item_id"],
    )


def downgrade() -> None:
    op.drop_table("topic_test_attempt_answers")
    op.drop_table("topic_test_attempts")
    op.drop_table("topic_test_items")
    op.drop_table("topic_tests")
