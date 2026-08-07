"""s42_workspace_annotations

Revision ID: s42_workspace_annotations
Revises: s41_daily_scoring_osym
Create Date: 2026-08-07 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 's42_workspace_annotations'
down_revision: Union[str, None] = 's41_daily_scoring_osym'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # study_workspaces table
    op.create_table(
        'study_workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subject_code', sa.String(), nullable=True),
        sa.Column('topic_code', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['resource_id'], ['study_resources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_workspaces_resource_id'), 'study_workspaces', ['resource_id'], unique=False)
    op.create_index(op.f('ix_study_workspaces_subject_code'), 'study_workspaces', ['subject_code'], unique=False)
    op.create_index(op.f('ix_study_workspaces_topic_code'), 'study_workspaces', ['topic_code'], unique=False)
    op.create_index(op.f('ix_study_workspaces_user_id'), 'study_workspaces', ['user_id'], unique=False)

    # annotation_layers table
    op.create_table(
        'annotation_layers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('page_index', sa.String(), nullable=False),
        sa.Column('objects_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['study_workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotation_layers_workspace_id'), 'annotation_layers', ['workspace_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_annotation_layers_workspace_id'), table_name='annotation_layers')
    op.drop_table('annotation_layers')
    
    op.drop_index(op.f('ix_study_workspaces_user_id'), table_name='study_workspaces')
    op.drop_index(op.f('ix_study_workspaces_topic_code'), table_name='study_workspaces')
    op.drop_index(op.f('ix_study_workspaces_subject_code'), table_name='study_workspaces')
    op.drop_index(op.f('ix_study_workspaces_resource_id'), table_name='study_workspaces')
    op.drop_table('study_workspaces')
