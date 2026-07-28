"""add goals.product_goal_type (Sprint-3.0.2)

Revision ID: k7f8a9b0c1d2
Revises: j6e7f8a9b0c1
Create Date: 2026-07-17 16:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "k7f8a9b0c1d2"
down_revision: str | None = "j6e7f8a9b0c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "goals",
        sa.Column("product_goal_type", sa.String(length=40), nullable=True),
    )
    op.create_index(
        op.f("ix_goals_product_goal_type"),
        "goals",
        ["product_goal_type"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_goals_product_goal_type"), table_name="goals")
    op.drop_column("goals", "product_goal_type")
