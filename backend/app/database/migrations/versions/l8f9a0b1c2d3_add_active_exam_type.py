"""add students.active_exam_type (Sprint-3.1.A)

Revision ID: l8f9a0b1c2d3
Revises: k7f8a9b0c1d2
Create Date: 2026-07-18 18:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "l8f9a0b1c2d3"
down_revision: str | None = "k7f8a9b0c1d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("active_exam_type", sa.String(length=20), nullable=True),
    )
    op.create_index(
        op.f("ix_students_active_exam_type"),
        "students",
        ["active_exam_type"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_students_active_exam_type"), table_name="students")
    op.drop_column("students", "active_exam_type")
