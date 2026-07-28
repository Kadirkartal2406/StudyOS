"""add revision items/schedules/reviews + revision_reminders_enabled

Revision ID: g3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-07-17 11:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "g3b4c5d6e7f8"
down_revision: str | None = "f2a3b4c5d6e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "revision_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("topic", sa.String(length=200), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=40), nullable=False, server_default="manual"),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("reason", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_revision_items_user_id"), "revision_items", ["user_id"])
    op.create_index(op.f("ix_revision_items_subject"), "revision_items", ["subject"])
    op.create_index(op.f("ix_revision_items_topic"), "revision_items", ["topic"])
    op.create_index(op.f("ix_revision_items_source_type"), "revision_items", ["source_type"])
    op.create_index(op.f("ix_revision_items_source_id"), "revision_items", ["source_id"])
    op.create_index(op.f("ix_revision_items_status"), "revision_items", ["status"])

    op.create_table(
        "revision_schedules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("revision_item_id", sa.UUID(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("repetition_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lapse_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["revision_item_id"], ["revision_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("revision_item_id", name="uq_revision_schedules_item"),
    )
    op.create_index(
        op.f("ix_revision_schedules_revision_item_id"),
        "revision_schedules",
        ["revision_item_id"],
    )
    op.create_index(op.f("ix_revision_schedules_due_at"), "revision_schedules", ["due_at"])

    op.create_table(
        "revision_reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("revision_item_id", sa.UUID(), nullable=False),
        sa.Column("grade", sa.String(length=20), nullable=False),
        sa.Column("previous_interval_days", sa.Integer(), nullable=False),
        sa.Column("new_interval_days", sa.Integer(), nullable=False),
        sa.Column("previous_difficulty", sa.Integer(), nullable=False),
        sa.Column("new_difficulty", sa.Integer(), nullable=False),
        sa.Column("previous_ease", sa.Float(), nullable=False),
        sa.Column("new_ease", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["revision_item_id"], ["revision_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_revision_reviews_revision_item_id"),
        "revision_reviews",
        ["revision_item_id"],
    )
    op.create_index(op.f("ix_revision_reviews_reviewed_at"), "revision_reviews", ["reviewed_at"])

    op.add_column(
        "notification_preferences",
        sa.Column(
            "revision_reminders_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


def downgrade() -> None:
    op.drop_column("notification_preferences", "revision_reminders_enabled")
    op.drop_index(op.f("ix_revision_reviews_reviewed_at"), table_name="revision_reviews")
    op.drop_index(op.f("ix_revision_reviews_revision_item_id"), table_name="revision_reviews")
    op.drop_table("revision_reviews")
    op.drop_index(op.f("ix_revision_schedules_due_at"), table_name="revision_schedules")
    op.drop_index(
        op.f("ix_revision_schedules_revision_item_id"), table_name="revision_schedules"
    )
    op.drop_table("revision_schedules")
    op.drop_index(op.f("ix_revision_items_status"), table_name="revision_items")
    op.drop_index(op.f("ix_revision_items_source_id"), table_name="revision_items")
    op.drop_index(op.f("ix_revision_items_source_type"), table_name="revision_items")
    op.drop_index(op.f("ix_revision_items_topic"), table_name="revision_items")
    op.drop_index(op.f("ix_revision_items_subject"), table_name="revision_items")
    op.drop_index(op.f("ix_revision_items_user_id"), table_name="revision_items")
    op.drop_table("revision_items")
