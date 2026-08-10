"""s43_trial_exam_pool_type

Revision ID: s43_trial_exam_pool_type
Revises: s42_workspace_annotations
Create Date: 2026-08-07 21:18:00.000000

Adds question_pool_cards.pool_type (trial vs general pool isolation).
Idempotent: safe if the column/index were applied manually ahead of Alembic.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "s43_trial_exam_pool_type"
down_revision: Union[str, None] = "s42_workspace_annotations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_INDEX = "ix_question_pool_cards_pool_type"


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("question_pool_cards")}
    if "pool_type" not in columns:
        op.add_column(
            "question_pool_cards",
            sa.Column(
                "pool_type",
                sa.String(length=50),
                server_default="general",
                nullable=False,
            ),
        )

    indexes = {ix["name"] for ix in insp.get_indexes("question_pool_cards")}
    if _INDEX not in indexes:
        op.create_index(_INDEX, "question_pool_cards", ["pool_type"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = {ix["name"] for ix in insp.get_indexes("question_pool_cards")}
    if _INDEX in indexes:
        op.drop_index(_INDEX, table_name="question_pool_cards")

    columns = {c["name"] for c in insp.get_columns("question_pool_cards")}
    if "pool_type" in columns:
        op.drop_column("question_pool_cards", "pool_type")
