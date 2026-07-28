"""add behavioral_memory table (LOS Module 7)

Revision ID: r4f5a6b7c8d9
Revises: q3e4f5a6b7c8
Create Date: 2026-07-20 13:30:00.000000

LOS Module 7 — Behavioral Learning Memory.
Not: Chat Memory (memories tablosu) kullanıcıya açık CRUD'dur.
Bu tablo sistem tarafından sessizce güncellenen davranış modelidir.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "r4f5a6b7c8d9"
down_revision: str | None = "q3e4f5a6b7c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "behavioral_memory",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        # LOS § 7.1 alanları — tüm JSON; soft update ile güncellenir
        sa.Column("chronotype", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("tempo", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("difficulty_signature", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("acquisition_speed", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("forgetting_curve", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("pomodoro_signature", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("break_signature", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("resource_preference", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("schedule_signature", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("motivation_dips", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("plan_receptivity", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("exam_context", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "last_updated_at",
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_behavioral_memory_user"),
    )
    op.create_index("ix_behavioral_memory_user_id", "behavioral_memory", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_behavioral_memory_user_id", table_name="behavioral_memory")
    op.drop_table("behavioral_memory")
