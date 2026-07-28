"""add activities table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-16 19:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("study_session_id", sa.UUID(), nullable=True),
        sa.Column("study_plan_id", sa.UUID(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default="now()", nullable=False),
        sa.ForeignKeyConstraint(["study_plan_id"], ["study_plans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["study_session_id"], ["study_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activities_user_id"), "activities", ["user_id"], unique=False)
    op.create_index(op.f("ix_activities_event_type"), "activities", ["event_type"], unique=False)
    op.create_index(
        op.f("ix_activities_study_session_id"), "activities", ["study_session_id"], unique=False
    )
    op.create_index(
        op.f("ix_activities_study_plan_id"), "activities", ["study_plan_id"], unique=False
    )
    op.create_index(op.f("ix_activities_occurred_at"), "activities", ["occurred_at"], unique=False)
    op.create_index(
        "ix_activities_user_occurred",
        "activities",
        ["user_id", "occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_activities_user_occurred", table_name="activities")
    op.drop_index(op.f("ix_activities_occurred_at"), table_name="activities")
    op.drop_index(op.f("ix_activities_study_plan_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_study_session_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_event_type"), table_name="activities")
    op.drop_index(op.f("ix_activities_user_id"), table_name="activities")
    op.drop_table("activities")
