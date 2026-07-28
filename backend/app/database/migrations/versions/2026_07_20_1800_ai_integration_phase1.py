"""AI Integration Phase 1: topic_code on resources, topic/subject on conversations

Revision ID: ai_phase1_001
Revises: s6_add_topic_to_question_records
Create Date: 2026-07-20
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = 'ai_phase1_001'
down_revision = 's6_add_topic_to_question_records'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # study_resources: topic_code ekle
    op.add_column('study_resources', sa.Column('topic_code', sa.String(200), nullable=True))
    op.create_index('ix_study_resources_topic_code', 'study_resources', ['topic_code'], unique=False)
    
    # conversations: topic_code ve subject_code ekle
    op.add_column('conversations', sa.Column('topic_code', sa.String(200), nullable=True))
    op.add_column('conversations', sa.Column('subject_code', sa.String(100), nullable=True))
    op.create_index('ix_conversations_topic_code', 'conversations', ['topic_code'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_conversations_topic_code', table_name='conversations')
    op.drop_column('conversations', 'subject_code')
    op.drop_column('conversations', 'topic_code')
    op.drop_index('ix_study_resources_topic_code', table_name='study_resources')
    op.drop_column('study_resources', 'topic_code')
