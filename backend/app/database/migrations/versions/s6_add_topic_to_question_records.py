"""add subject_code and topic_code to question_records (Sprint-6)

Revision ID: s6_add_topic_to_question_records
Revises: m9a0b1c2d3e4_add_topic_catalog
Create Date: 2026-07-20

Adds: question_records.subject_code, question_records.topic_code
Both columns are nullable; existing rows keep NULL until backfilled.
"""

from alembic import op
import sqlalchemy as sa

revision = "s6_add_topic_to_question_records"
down_revision = "r4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "question_records",
        sa.Column("subject_code", sa.String(100), nullable=True),
    )
    op.add_column(
        "question_records",
        sa.Column("topic_code", sa.String(200), nullable=True),
    )
    op.create_index(
        "ix_question_records_subject_code", "question_records", ["subject_code"]
    )
    op.create_index(
        "ix_question_records_topic_code", "question_records", ["topic_code"]
    )


def downgrade() -> None:
    op.drop_index("ix_question_records_topic_code", table_name="question_records")
    op.drop_index("ix_question_records_subject_code", table_name="question_records")
    op.drop_column("question_records", "topic_code")
    op.drop_column("question_records", "subject_code")
