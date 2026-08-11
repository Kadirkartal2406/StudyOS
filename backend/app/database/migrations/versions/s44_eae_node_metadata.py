"""s44_eae_node_metadata

Revision ID: s44_eae_node_metadata
Revises: s43_trial_exam_pool_type
Create Date: 2026-08-11 11:20:00.000000

Adds educational_asset_nodes.educational_metadata (JSONB, nullable).
Idempotent: safe if the column was applied manually ahead of Alembic.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "s44_eae_node_metadata"
down_revision: Union[str, None] = "s43_trial_exam_pool_type"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("educational_asset_nodes")}
    if "educational_metadata" not in columns:
        op.add_column(
            "educational_asset_nodes",
            sa.Column(
                "educational_metadata",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("educational_asset_nodes")}
    if "educational_metadata" in columns:
        op.drop_column("educational_asset_nodes", "educational_metadata")
