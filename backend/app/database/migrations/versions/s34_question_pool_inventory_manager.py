"""M33 — Smart Question Pool Manager (inventory/history/locks).

Yeni tablolar:
- question_pool_generation_history
- question_pool_generation_locks
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s34_qpool_mgr"
down_revision = "s33_admin_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_pool_generation_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exam", sa.String(length=32), nullable=False),
        sa.Column("subject_code", sa.String(length=80), nullable=False),
        sa.Column("topic_code", sa.String(length=120), nullable=False),
        sa.Column(
            "difficulty_band", sa.String(length=16), nullable=False, server_default="medium"
        ),
        sa.Column("generated_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accepted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quality_average", sa.Float(), nullable=True),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("gemini_calls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost", sa.Float(), nullable=True),
        sa.Column("provider", sa.String(length=32), nullable=True),
        sa.Column("model", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_question_pool_generation_history_timestamp",
        "question_pool_generation_history",
        ["timestamp"],
    )
    op.create_index(
        "ix_question_pool_generation_history_exam_subject_topic",
        "question_pool_generation_history",
        ["exam", "subject_code", "topic_code", "difficulty_band"],
    )

    op.create_table(
        "question_pool_generation_locks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lock_key", sa.String(length=240), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_question_pool_generation_locks_expires_at",
        "question_pool_generation_locks",
        ["expires_at"],
    )
    op.create_unique_constraint(
        "uq_question_pool_generation_locks_lock_key",
        "question_pool_generation_locks",
        ["lock_key"],
    )


def downgrade() -> None:
    op.drop_table("question_pool_generation_locks")
    op.drop_table("question_pool_generation_history")

