"""add observation_state to students (LOS Module 3)

Revision ID: q3e4f5a6b7c8
Revises: p2d3e4f5a6b7
Create Date: 2026-07-20 13:00:00.000000

LOS Module 3 — Observation Mode gate-based state machine.
Adds: students.observation_state, observation_gates, observation_entered_at
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "q3e4f5a6b7c8"
down_revision: str | None = "p2d3e4f5a6b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # observation_state: 'observing' | 'calibrating' | 'full'
    op.add_column(
        "students",
        sa.Column(
            "observation_state",
            sa.String(20),
            nullable=False,
            server_default="observing",
        ),
    )
    # observation_gates: hangi kapılar doldu (JSON)
    op.add_column(
        "students",
        sa.Column(
            "observation_gates",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "students",
        sa.Column("observation_entered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("observation_exited_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_students_observation_state", "students", ["observation_state"]
    )


def downgrade() -> None:
    op.drop_index("ix_students_observation_state", table_name="students")
    op.drop_column("students", "observation_exited_at")
    op.drop_column("students", "observation_entered_at")
    op.drop_column("students", "observation_gates")
    op.drop_column("students", "observation_state")
