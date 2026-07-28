"""Sprint 21 RC — analytics_events + beta_feedback

Revision ID: s21_rc_beta_ops
Revises: s19_knowledge_layer
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s21_rc_beta_ops"
down_revision = "s19_knowledge_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("platform", sa.String(40), nullable=True),
        sa.Column("app_version", sa.String(40), nullable=True),
        sa.Column("session_id", sa.String(80), nullable=True),
        sa.Column(
            "properties",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"])
    op.create_index("ix_analytics_events_name", "analytics_events", ["name"])
    op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])

    op.create_table(
        "beta_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("screen_hint", sa.String(200), nullable=True),
        sa.Column("app_version", sa.String(40), nullable=True),
        sa.Column("platform", sa.String(40), nullable=True),
        sa.Column("log_excerpt", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_beta_feedback_user_id", "beta_feedback", ["user_id"])
    op.create_index("ix_beta_feedback_kind", "beta_feedback", ["kind"])


def downgrade() -> None:
    op.drop_table("beta_feedback")
    op.drop_table("analytics_events")
