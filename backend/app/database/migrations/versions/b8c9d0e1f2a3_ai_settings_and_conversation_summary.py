"""ai preferred settings and conversation summary fields

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-07-16 22:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "notification_preferences",
        sa.Column("ai_preferred_provider", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "notification_preferences",
        sa.Column("ai_preferred_model", sa.String(length=120), nullable=True),
    )
    op.add_column("conversations", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column(
        "conversations",
        sa.Column("summary_updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("conversations", "summary_updated_at")
    op.drop_column("conversations", "summary")
    op.drop_column("notification_preferences", "ai_preferred_model")
    op.drop_column("notification_preferences", "ai_preferred_provider")
