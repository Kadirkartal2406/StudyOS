"""add question_records table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-16 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("study_plan_id", sa.UUID(), nullable=True),
        sa.Column("study_session_id", sa.UUID(), nullable=True),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("topic", sa.String(length=200), nullable=True),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blank_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("difficulty", sa.String(length=20), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=True),
        sa.Column("exam_type", sa.String(length=20), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("net_score", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default="now()", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default="now()", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["study_plan_id"], ["study_plans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["study_session_id"], ["study_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_question_records_user_id"), "question_records", ["user_id"])
    op.create_index(op.f("ix_question_records_study_plan_id"), "question_records", ["study_plan_id"])
    op.create_index(
        op.f("ix_question_records_study_session_id"), "question_records", ["study_session_id"]
    )
    op.create_index(op.f("ix_question_records_subject"), "question_records", ["subject"])
    op.create_index(op.f("ix_question_records_topic"), "question_records", ["topic"])
    op.create_index(op.f("ix_question_records_exam_type"), "question_records", ["exam_type"])
    op.create_index(op.f("ix_question_records_created_at"), "question_records", ["created_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_question_records_created_at"), table_name="question_records")
    op.drop_index(op.f("ix_question_records_exam_type"), table_name="question_records")
    op.drop_index(op.f("ix_question_records_topic"), table_name="question_records")
    op.drop_index(op.f("ix_question_records_subject"), table_name="question_records")
    op.drop_index(op.f("ix_question_records_study_session_id"), table_name="question_records")
    op.drop_index(op.f("ix_question_records_study_plan_id"), table_name="question_records")
    op.drop_index(op.f("ix_question_records_user_id"), table_name="question_records")
    op.drop_table("question_records")
