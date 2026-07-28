"""add topic_evidence table and bind study_sessions to topic

Revision ID: o1c2d3e4f5a6
Revises: n0b1c2d3e4f5
Create Date: 2026-07-20 12:30:00.000000

LOS Module 1 — Evidence Engine foundation.
- topic_evidence: LOS § 3 canonical evidence store
- study_sessions: subject_code + topic_code bind columns (nullable)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "o1c2d3e4f5a6"
down_revision: str | None = "n0b1c2d3e4f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── topic_evidence ─────────────────────────────────────────────
    op.create_table(
        "topic_evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("subject_code", sa.String(100), nullable=False),
        sa.Column("topic_code", sa.String(200), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("horizon", sa.String(20), nullable=False, server_default="instant"),
        sa.Column("value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("quality_weight", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_topic_evidence_user_id", "topic_evidence", ["user_id"])
    op.create_index("ix_topic_evidence_subject_code", "topic_evidence", ["subject_code"])
    op.create_index("ix_topic_evidence_topic_code", "topic_evidence", ["topic_code"])
    op.create_index("ix_topic_evidence_category", "topic_evidence", ["user_id", "category"])
    op.create_index(
        "ix_topic_evidence_user_topic", "topic_evidence", ["user_id", "topic_code"]
    )
    op.create_index(
        "ix_topic_evidence_user_subject", "topic_evidence", ["user_id", "subject_code"]
    )
    op.create_index(
        "ix_topic_evidence_occurred", "topic_evidence", ["user_id", "occurred_at"]
    )
    op.create_index(
        "ix_topic_evidence_source", "topic_evidence", ["source_type", "source_id"]
    )

    # ── study_sessions: Topic binding columns ──────────────────────
    op.add_column(
        "study_sessions",
        sa.Column("subject_code", sa.String(100), nullable=True),
    )
    op.add_column(
        "study_sessions",
        sa.Column("topic_code", sa.String(200), nullable=True),
    )
    op.create_index(
        "ix_study_sessions_topic_code", "study_sessions", ["topic_code"]
    )


def downgrade() -> None:
    op.drop_index("ix_study_sessions_topic_code", table_name="study_sessions")
    op.drop_column("study_sessions", "topic_code")
    op.drop_column("study_sessions", "subject_code")

    op.drop_index("ix_topic_evidence_source", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_occurred", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_user_subject", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_user_topic", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_category", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_topic_code", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_subject_code", table_name="topic_evidence")
    op.drop_index("ix_topic_evidence_user_id", table_name="topic_evidence")
    op.drop_table("topic_evidence")
