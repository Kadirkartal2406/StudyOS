"""AI Phase 1.002: generated_questions tablosu

Revision ID: ai_phase1_002
Revises: ai_phase1_001
Create Date: 2026-07-20
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'ai_phase1_002'
down_revision = 'ai_phase1_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'generated_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject_code', sa.String(100), nullable=False),
        sa.Column('topic_code', sa.String(200), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('correct_option', sa.String(5), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('confidence_level_at_generation', sa.String(20), nullable=True),
        sa.Column('belief_at_generation', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('user_answer', sa.String(5), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('generation_trigger', sa.String(40), nullable=False, server_default='on_demand'),
        sa.Column('ai_provider', sa.String(50), nullable=True),
        sa.Column('generation_context', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_generated_questions_user_id', 'generated_questions', ['user_id'])
    op.create_index('ix_generated_questions_topic_code', 'generated_questions', ['topic_code'])
    op.create_index('ix_generated_questions_status', 'generated_questions', ['status'])
    op.create_index('ix_generated_questions_created_at', 'generated_questions', ['created_at'])


def downgrade() -> None:
    op.drop_table('generated_questions')
