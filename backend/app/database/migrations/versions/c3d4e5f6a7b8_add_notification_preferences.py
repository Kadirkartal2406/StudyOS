"""add notification_preferences table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-16 19:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("pomodoro_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("long_break_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("daily_reminder_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("daily_goal_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("streak_reminder_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "widget_auto_update_enabled", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column("reminder_time", sa.Time(), nullable=True),
        sa.Column("quiet_hours_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("quiet_hours_start", sa.Time(), nullable=True),
        sa.Column("quiet_hours_end", sa.Time(), nullable=True),
        sa.Column("fcm_token", sa.String(length=512), nullable=True),
        sa.Column("fcm_token_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default="now()", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default="now()", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_notification_preferences_user_id"),
    )
    op.create_index(
        op.f("ix_notification_preferences_user_id"),
        "notification_preferences",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_notification_preferences_user_id"), table_name="notification_preferences"
    )
    op.drop_table("notification_preferences")
