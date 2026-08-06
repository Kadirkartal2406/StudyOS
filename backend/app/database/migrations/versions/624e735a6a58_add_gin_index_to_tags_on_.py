"""Add GIN index to tags on EducationalAsset

Revision ID: 624e735a6a58
Revises: e72c51f4a4aa
Create Date: 2026-08-05 19:49:45.338057

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "624e735a6a58"
down_revision: Union[str, None] = "e72c51f4a4aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_educational_assets_tags_gin",
        "educational_assets",
        ["tags"],
        unique=False,
        postgresql_using="gin",
    )

def downgrade() -> None:
    op.drop_index("ix_educational_assets_tags_gin", table_name="educational_assets")
