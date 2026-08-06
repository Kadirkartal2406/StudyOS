"""Sprint 35 — Educational Asset Engine (EAE) tables.

Revision ID: s35_educational_asset_engine
Revises: s34_question_pool_inventory_manager
Create Date: 2026-08-05 17:48:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "s35_educational_asset_engine"
down_revision: Union[str, None] = "s34_qpool_mgr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "educational_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", sa.String(255), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("domain", sa.String(100), nullable=False),
        sa.Column("format", sa.String(50), nullable=False, server_default="svg"),
        sa.Column("title", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("viewport", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("license_type", sa.String(50), nullable=False, server_default="studyos_core"),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_deprecated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("bundle_hash_sha256", sa.String(64), nullable=True),
        sa.Column("bundle_size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_educational_assets_asset_id", "educational_assets", ["asset_id"], unique=True
    )
    op.create_index(
        "ix_educational_assets_domain", "educational_assets", ["domain"]
    )
    op.create_index(
        "ix_educational_assets_tenant_id", "educational_assets", ["tenant_id"]
    )
    op.create_index(
        "idx_educational_assets_domain_deprecated",
        "educational_assets",
        ["domain", "is_deprecated"],
    )
    op.create_index(
        "idx_educational_assets_tags_gin",
        "educational_assets",
        ["tags"],
        postgresql_using="gin",
    )

    op.create_table(
        "educational_asset_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "asset_db_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("educational_assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("node_id", sa.String(255), nullable=False),
        sa.Column("name", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("bounding_box", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
    )
    op.create_index(
        "ix_educational_asset_nodes_asset_db_id", "educational_asset_nodes", ["asset_db_id"]
    )
    op.create_index(
        "ix_educational_asset_nodes_node_id", "educational_asset_nodes", ["node_id"]
    )
    op.create_index(
        "idx_asset_nodes_asset_node_id",
        "educational_asset_nodes",
        ["asset_db_id", "node_id"],
        unique=True,
    )

    op.create_table(
        "educational_asset_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "asset_db_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("educational_assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("change_log", sa.Text(), nullable=True),
        sa.Column("is_breaking", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_educational_asset_versions_asset_db_id", "educational_asset_versions", ["asset_db_id"]
    )
    op.create_index(
        "idx_asset_versions_asset_ver",
        "educational_asset_versions",
        ["asset_db_id", "version"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("educational_asset_versions")
    op.drop_table("educational_asset_nodes")
    op.drop_table("educational_assets")
