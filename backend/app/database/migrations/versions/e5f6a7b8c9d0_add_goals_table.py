"""add goals table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-16 21:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("goal_type", sa.String(length=30), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("subject", sa.String(length=100), nullable=True),
        sa.Column("topic", sa.String(length=200), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "milestones_reached",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_goals_user_id"), "goals", ["user_id"])
    op.create_index(op.f("ix_goals_goal_type"), "goals", ["goal_type"])
    op.create_index(op.f("ix_goals_period"), "goals", ["period"])
    op.create_index(op.f("ix_goals_status"), "goals", ["status"])
    op.create_index(op.f("ix_goals_subject"), "goals", ["subject"])
    op.create_index(op.f("ix_goals_topic"), "goals", ["topic"])
    op.create_index(op.f("ix_goals_start_date"), "goals", ["start_date"])
    op.create_index(op.f("ix_goals_end_date"), "goals", ["end_date"])


def downgrade() -> None:
    op.drop_index(op.f("ix_goals_end_date"), table_name="goals")
    op.drop_index(op.f("ix_goals_start_date"), table_name="goals")
    op.drop_index(op.f("ix_goals_topic"), table_name="goals")
    op.drop_index(op.f("ix_goals_subject"), table_name="goals")
    op.drop_index(op.f("ix_goals_status"), table_name="goals")
    op.drop_index(op.f("ix_goals_period"), table_name="goals")
    op.drop_index(op.f("ix_goals_goal_type"), table_name="goals")
    op.drop_index(op.f("ix_goals_user_id"), table_name="goals")
    op.drop_table("goals")
