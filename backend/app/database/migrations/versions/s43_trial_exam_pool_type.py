"""s43_trial_exam_pool_type

Revision ID: s43_trial_exam_pool_type
Revises: s42_workspace_annotations
Create Date: 2026-08-07 21:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 's43_trial_exam_pool_type'
down_revision: Union[str, None] = 's42_workspace_annotations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add pool_type column to question_pool_cards table
    op.add_column('question_pool_cards', sa.Column('pool_type', sa.String(length=50), server_default='general', nullable=False))


def downgrade() -> None:
    # Remove pool_type column from question_pool_cards table
    op.drop_column('question_pool_cards', 'pool_type')
