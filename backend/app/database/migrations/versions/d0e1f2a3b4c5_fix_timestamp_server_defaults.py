"""fix frozen timestamp server defaults to now()

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-07-17 09:30:00.000000

Bazı tablolarda created_at/updated_at DEFAULT değeri migration anındaki
sabit timestamp olarak kalmıştı; 'bugün' aggregate testleri kırılıyordu.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES_BOTH = (
    "users",
    "study_plans",
    "study_sessions",
    "question_records",
    "notification_preferences",
)
_TABLES_CREATED_ONLY = (
    "refresh_tokens",
    "activities",
)


def upgrade() -> None:
    for table in _TABLES_BOTH:
        op.alter_column(
            table,
            "created_at",
            server_default=sa.text("now()"),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        op.alter_column(
            table,
            "updated_at",
            server_default=sa.text("now()"),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
    for table in _TABLES_CREATED_ONLY:
        op.alter_column(
            table,
            "created_at",
            server_default=sa.text("now()"),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )


def downgrade() -> None:
    # Geri alma: sabit timestamp'e dönülmez; now() bırakılır.
    pass
