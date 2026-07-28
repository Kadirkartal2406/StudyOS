"""Sprint 23 M23.7 — wrong_explain cache column on assessment_questions."""

from alembic import op
import sqlalchemy as sa

revision = "s27_assessment_wrong_explain"
down_revision = "s26_exam_style_intelligence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "assessment_questions",
        sa.Column("wrong_explain", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assessment_questions", "wrong_explain")
