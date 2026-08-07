"""Add scoring models

Revision ID: s41_daily_scoring_osym
Revises: 5217b338bf32
Create Date: 2026-08-07 10:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 's41_daily_scoring_osym'
down_revision: Union[str, None] = '5217b338bf32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns to daily_challenge_scores
    op.add_column('daily_challenge_scores', sa.Column('studyos_score', sa.Float(), server_default='0.0', nullable=False))
    op.add_column('daily_challenge_scores', sa.Column('studyos_rank', sa.Integer(), nullable=True))
    op.add_column('daily_challenge_scores', sa.Column('is_official', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('daily_challenge_scores', sa.Column('osym_estimations', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))

    # 2. Add column to shared_daily_booklets
    op.add_column('shared_daily_booklets', sa.Column('is_finalized', sa.Boolean(), server_default='false', nullable=False))

    # 3. Create daily_challenge_statistics table
    op.create_table('daily_challenge_statistics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('exam_type', sa.String(length=40), nullable=False),
        sa.Column('challenge_date', sa.Date(), nullable=False),
        sa.Column('participant_count', sa.Integer(), nullable=False),
        sa.Column('subject_averages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('subject_std_devs', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('score_mean', sa.Float(), nullable=False),
        sa.Column('score_std_dev', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_type', 'challenge_date', name='uq_daily_challenge_statistics_exam_date')
    )
    op.create_index(op.f('ix_daily_challenge_statistics_challenge_date'), 'daily_challenge_statistics', ['challenge_date'], unique=False)
    op.create_index(op.f('ix_daily_challenge_statistics_exam_type'), 'daily_challenge_statistics', ['exam_type'], unique=False)

    # 4. Create osym_coefficients table
    op.create_table('osym_coefficients',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('exam_type', sa.String(length=40), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('base_point', sa.Float(), nullable=False),
        sa.Column('subject_weights', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('subject_means', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('subject_std_devs', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_type', 'year', name='uq_osym_coefficients_exam_year')
    )
    op.create_index(op.f('ix_osym_coefficients_exam_type'), 'osym_coefficients', ['exam_type'], unique=False)
    op.create_index(op.f('ix_osym_coefficients_year'), 'osym_coefficients', ['year'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_osym_coefficients_year'), table_name='osym_coefficients')
    op.drop_index(op.f('ix_osym_coefficients_exam_type'), table_name='osym_coefficients')
    op.drop_table('osym_coefficients')

    op.drop_index(op.f('ix_daily_challenge_statistics_exam_type'), table_name='daily_challenge_statistics')
    op.drop_index(op.f('ix_daily_challenge_statistics_challenge_date'), table_name='daily_challenge_statistics')
    op.drop_table('daily_challenge_statistics')

    op.drop_column('shared_daily_booklets', 'is_finalized')

    op.drop_column('daily_challenge_scores', 'osym_estimations')
    op.drop_column('daily_challenge_scores', 'is_official')
    op.drop_column('daily_challenge_scores', 'studyos_rank')
    op.drop_column('daily_challenge_scores', 'studyos_score')
