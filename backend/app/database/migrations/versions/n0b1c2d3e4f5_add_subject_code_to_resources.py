"""add subject_code to study_resources (per-subject filtering)

Revision ID: n0b1c2d3e4f5
Revises: m9a0b1c2d3e4
Create Date: 2026-07-20 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "n0b1c2d3e4f5"
down_revision: str | None = "m9a0b1c2d3e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "study_resources",
        sa.Column("subject_code", sa.String(100), nullable=True),
    )
    op.create_index(
        "ix_study_resources_subject_code",
        "study_resources",
        ["subject_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_study_resources_subject_code", table_name="study_resources")
    op.drop_column("study_resources", "subject_code")
