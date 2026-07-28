"""add study_resources table

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-07-17 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c9d0e1f2a3b4"
down_revision: str | None = "b8c9d0e1f2a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "study_resources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("study_plan_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("resource_type", sa.String(length=40), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=2000), nullable=True),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="not_started"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.ForeignKeyConstraint(["study_plan_id"], ["study_plans.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_study_resources_user_id"), "study_resources", ["user_id"])
    op.create_index(op.f("ix_study_resources_study_plan_id"), "study_resources", ["study_plan_id"])
    op.create_index(op.f("ix_study_resources_resource_type"), "study_resources", ["resource_type"])
    op.create_index(op.f("ix_study_resources_status"), "study_resources", ["status"])


def downgrade() -> None:
    op.drop_index(op.f("ix_study_resources_status"), table_name="study_resources")
    op.drop_index(op.f("ix_study_resources_resource_type"), table_name="study_resources")
    op.drop_index(op.f("ix_study_resources_study_plan_id"), table_name="study_resources")
    op.drop_index(op.f("ix_study_resources_user_id"), table_name="study_resources")
    op.drop_table("study_resources")
