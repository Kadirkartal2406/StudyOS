"""Add bundle_payload to EducationalAssetVersion

Revision ID: e72c51f4a4aa
Revises: 51f76597a873
Create Date: 2026-08-05 19:46:43.286513

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e72c51f4a4aa"
down_revision: Union[str, None] = "51f76597a873"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "educational_asset_versions", sa.Column("bundle_payload", sa.LargeBinary(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column("educational_asset_versions", "bundle_payload")

