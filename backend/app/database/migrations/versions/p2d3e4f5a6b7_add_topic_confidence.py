"""add topic_confidence table (LOS Module 2)

Revision ID: p2d3e4f5a6b7
Revises: o1c2d3e4f5a6
Create Date: 2026-07-20 12:45:00.000000

LOS Module 2 — Confidence Engine.
topic_confidence: per-user per-topic belief + uncertainty state.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "p2d3e4f5a6b7"
down_revision: str | None = "o1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "topic_confidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("belief", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("uncertainty", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("confidence_level", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("performance_sample_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weighted_accuracy", sa.Float(), nullable=True),
        sa.Column("total_effort_minutes", sa.Float(), nullable=False, server_default="0"),
        sa.Column("trend_direction", sa.Float(), nullable=False, server_default="0"),
        sa.Column("consistency_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("days_since_last_evidence", sa.Integer(), nullable=True),
        sa.Column("forgetting_applied", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("history_snapshot", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("last_evidence_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_calculated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_topic_confidence_user_topic",
        "topic_confidence",
        ["user_id", "topic_code"],
        unique=True,
    )
    op.create_index(
        "ix_topic_confidence_level",
        "topic_confidence",
        ["user_id", "confidence_level"],
    )
    op.create_index("ix_topic_confidence_subject", "topic_confidence", ["subject_code"])


def downgrade() -> None:
    op.drop_index("ix_topic_confidence_subject", table_name="topic_confidence")
    op.drop_index("ix_topic_confidence_level", table_name="topic_confidence")
    op.drop_index("ix_topic_confidence_user_topic", table_name="topic_confidence")
    op.drop_table("topic_confidence")
