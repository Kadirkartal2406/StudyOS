"""add topic_catalog (Sprint-3.2.A Topic Foundation)

Revision ID: m9a0b1c2d3e4
Revises: l8f9a0b1c2d3
Create Date: 2026-07-19 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m9a0b1c2d3e4"
down_revision: str | None = "l8f9a0b1c2d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "topic_catalog",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("subject_code", sa.String(length=80), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["subject_code"],
            ["subject_catalog.code"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subject_code", "code", name="uq_topic_catalog_subject_code"),
    )
    op.create_index("ix_topic_catalog_code", "topic_catalog", ["code"], unique=True)
    op.create_index("ix_topic_catalog_subject_code", "topic_catalog", ["subject_code"])


def downgrade() -> None:
    op.drop_index("ix_topic_catalog_subject_code", table_name="topic_catalog")
    op.drop_index("ix_topic_catalog_code", table_name="topic_catalog")
    op.drop_table("topic_catalog")
