"""add planner_drafts and study_plan planner fields

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-07-17 10:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f2a3b4c5d6e7"
down_revision: str | None = "e1f2a3b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "planner_drafts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("target_exam", sa.String(length=20), nullable=False),
        sa.Column("target_net", sa.Float(), nullable=False),
        sa.Column("available_days", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("available_hours", sa.Float(), nullable=False, server_default="2"),
        sa.Column("plan_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_planner_drafts_user_id"), "planner_drafts", ["user_id"])
    op.create_index(op.f("ix_planner_drafts_status"), "planner_drafts", ["status"])

    op.add_column(
        "study_plans",
        sa.Column("source", sa.String(length=30), nullable=False, server_default="manual"),
    )
    op.add_column("study_plans", sa.Column("planner_draft_id", sa.UUID(), nullable=True))
    op.create_index(
        op.f("ix_study_plans_planner_draft_id"), "study_plans", ["planner_draft_id"]
    )
    op.create_foreign_key(
        "fk_study_plans_planner_draft_id",
        "study_plans",
        "planner_drafts",
        ["planner_draft_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_study_plans_planner_draft_id", "study_plans", type_="foreignkey")
    op.drop_index(op.f("ix_study_plans_planner_draft_id"), table_name="study_plans")
    op.drop_column("study_plans", "planner_draft_id")
    op.drop_column("study_plans", "source")
    op.drop_index(op.f("ix_planner_drafts_status"), table_name="planner_drafts")
    op.drop_index(op.f("ix_planner_drafts_user_id"), table_name="planner_drafts")
    op.drop_table("planner_drafts")
