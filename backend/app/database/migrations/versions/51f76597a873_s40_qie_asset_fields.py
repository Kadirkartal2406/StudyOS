"""s40_qie_asset_fields

Revision ID: 51f76597a873
Revises: s35_educational_asset_engine
Create Date: 2026-08-05 19:16:27.809129
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "51f76597a873"
down_revision: Union[str, None] = "s35_educational_asset_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("question_pool_cards", sa.Column("target_asset_id", sa.UUID(), nullable=True))
    op.add_column("question_pool_cards", sa.Column("correct_node_id", sa.String(length=255), nullable=True))
    op.create_index(
        op.f("ix_question_pool_cards_target_asset_id"),
        "question_pool_cards",
        ["target_asset_id"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(op.f("ix_question_pool_cards_target_asset_id"), table_name="question_pool_cards")
    op.drop_column("question_pool_cards", "correct_node_id")
    op.drop_column("question_pool_cards", "target_asset_id")
