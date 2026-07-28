"""add achievements engine tables + seed + notification toggle

Revision ID: h4c5d6e7f8a9
Revises: g3b4c5d6e7f8
Create Date: 2026-07-17 12:00:00.000000

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "h4c5d6e7f8a9"
down_revision: str | None = "g3b4c5d6e7f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "achievements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False, server_default="easy"),
        sa.Column("points", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("icon_key", sa.String(length=80), nullable=False, server_default="trophy"),
        sa.Column("criteria", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_achievements_code"), "achievements", ["code"])
    op.create_index(op.f("ix_achievements_category"), "achievements", ["category"])

    op.create_table(
        "user_achievements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("achievement_id", sa.UUID(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("source_event", sa.String(length=64), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "unlocked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["achievement_id"], ["achievements.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "achievement_id", name="uq_user_achievements_user_achievement"
        ),
    )
    op.create_index(op.f("ix_user_achievements_user_id"), "user_achievements", ["user_id"])
    op.create_index(
        op.f("ix_user_achievements_achievement_id"), "user_achievements", ["achievement_id"]
    )
    op.create_index(op.f("ix_user_achievements_unlocked_at"), "user_achievements", ["unlocked_at"])

    op.create_table(
        "achievement_progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("achievement_id", sa.UUID(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("target_value", sa.Float(), nullable=False, server_default="1"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["achievement_id"], ["achievements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "achievement_id", name="uq_achievement_progress_user_achievement"
        ),
    )
    op.create_index(op.f("ix_achievement_progress_user_id"), "achievement_progress", ["user_id"])
    op.create_index(
        op.f("ix_achievement_progress_achievement_id"),
        "achievement_progress",
        ["achievement_id"],
    )

    op.add_column(
        "notification_preferences",
        sa.Column(
            "achievement_notifications_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    # Seed catalog (C1)
    from app.services.ai.achievement_catalog import ACHIEVEMENT_SEED

    achievements = sa.table(
        "achievements",
        sa.column("id", sa.UUID()),
        sa.column("code", sa.String()),
        sa.column("title", sa.String()),
        sa.column("description", sa.String()),
        sa.column("category", sa.String()),
        sa.column("tier", sa.String()),
        sa.column("points", sa.Integer()),
        sa.column("icon_key", sa.String()),
        sa.column("criteria", postgresql.JSONB()),
        sa.column("is_active", sa.Boolean()),
        sa.column("sort_order", sa.Integer()),
    )
    rows = []
    for item in ACHIEVEMENT_SEED:
        rows.append(
            {
                "id": uuid.uuid4(),
                "code": item["code"],
                "title": item["title"],
                "description": item["description"],
                "category": item["category"],
                "tier": item["tier"],
                "points": item["points"],
                "icon_key": item["icon_key"],
                "criteria": item["criteria"],
                "is_active": True,
                "sort_order": item["sort_order"],
            }
        )
    op.bulk_insert(achievements, rows)


def downgrade() -> None:
    op.drop_column("notification_preferences", "achievement_notifications_enabled")
    op.drop_index(op.f("ix_achievement_progress_achievement_id"), table_name="achievement_progress")
    op.drop_index(op.f("ix_achievement_progress_user_id"), table_name="achievement_progress")
    op.drop_table("achievement_progress")
    op.drop_index(op.f("ix_user_achievements_unlocked_at"), table_name="user_achievements")
    op.drop_index(op.f("ix_user_achievements_achievement_id"), table_name="user_achievements")
    op.drop_index(op.f("ix_user_achievements_user_id"), table_name="user_achievements")
    op.drop_table("user_achievements")
    op.drop_index(op.f("ix_achievements_category"), table_name="achievements")
    op.drop_index(op.f("ix_achievements_code"), table_name="achievements")
    op.drop_table("achievements")
