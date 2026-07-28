"""add learning profile: students, exam_targets, subject_catalog, user_subjects

Revision ID: i5d6e7f8a9b0
Revises: h4c5d6e7f8a9
Create Date: 2026-07-17 13:00:00.000000

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "i5d6e7f8a9b0"
down_revision: str | None = "h4c5d6e7f8a9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SUBJECT_SEED = [
    ("yks_turkce", "Türkçe", ["yks", "tyt", "ayt"], 10),
    ("yks_matematik", "Matematik", ["yks", "tyt", "ayt"], 20),
    ("yks_geometri", "Geometri", ["yks", "tyt", "ayt"], 30),
    ("yks_fizik", "Fizik", ["yks", "tyt", "ayt"], 40),
    ("yks_kimya", "Kimya", ["yks", "tyt", "ayt"], 50),
    ("yks_biyoloji", "Biyoloji", ["yks", "tyt", "ayt"], 60),
    ("yks_tarih", "Tarih", ["yks", "tyt", "ayt"], 70),
    ("yks_cografya", "Coğrafya", ["yks", "tyt", "ayt"], 80),
    ("yks_felsefe", "Felsefe", ["yks", "tyt", "ayt"], 90),
    ("yks_din", "Din Kültürü", ["yks", "tyt"], 100),
    ("kpss_gy", "Genel Yetenek", ["kpss"], 10),
    ("kpss_gk", "Genel Kültür", ["kpss"], 20),
    ("kpss_eb", "Eğitim Bilimleri", ["kpss"], 30),
    ("lgs_turkce", "Türkçe", ["lgs"], 10),
    ("lgs_matematik", "Matematik", ["lgs"], 20),
    ("lgs_fen", "Fen Bilimleri", ["lgs"], 30),
    ("lgs_inkilap", "İnkılap Tarihi", ["lgs"], 40),
    ("lgs_din", "Din Kültürü", ["lgs"], 50),
    ("lgs_ingilizce", "İngilizce", ["lgs"], 60),
    ("ales_sayisal", "Sayısal", ["ales"], 10),
    ("ales_sozel", "Sözel", ["ales"], 20),
    ("dgs_sayisal", "Sayısal", ["dgs"], 10),
    ("dgs_sozel", "Sözel", ["dgs"], 20),
    ("yds_ingilizce", "İngilizce", ["yds", "custom"], 10),
    ("yds_kelime", "Kelime", ["yds", "custom"], 20),
    ("yds_okuma", "Okuma", ["yds", "custom"], 30),
]


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("journey_stage", sa.String(length=30), nullable=False, server_default="new_user"),
        sa.Column("onboarding_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("onboarding_skipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("daily_study_minutes", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("available_days", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("available_hours", sa.Float(), nullable=False, server_default="2"),
        sa.Column("baseline_level", sa.String(length=30), nullable=False, server_default="unknown"),
        sa.Column("baseline_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_students_user_id", "students", ["user_id"])
    op.create_index("ix_students_journey_stage", "students", ["journey_stage"])

    op.create_table(
        "exam_targets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("exam_type", sa.String(length=20), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("target_net", sa.Float(), nullable=True),
        sa.Column("target_score", sa.Float(), nullable=True),
        sa.Column("target_rank", sa.Integer(), nullable=True),
        sa.Column("target_university", sa.String(length=200), nullable=True),
        sa.Column("target_department", sa.String(length=200), nullable=True),
        sa.Column("branch", sa.String(length=100), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exam_type", name="uq_exam_targets_user_type"),
    )
    op.create_index("ix_exam_targets_user_id", "exam_targets", ["user_id"])
    op.create_index("ix_exam_targets_exam_type", "exam_targets", ["exam_type"])

    op.create_table(
        "subject_catalog",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("exam_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_subject_catalog_code", "subject_catalog", ["code"])

    op.create_table(
        "user_subjects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("subject_code", sa.String(length=80), nullable=False),
        sa.Column("subject_name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="onboarding"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "subject_code", name="uq_user_subjects_user_code"),
    )
    op.create_index("ix_user_subjects_user_id", "user_subjects", ["user_id"])
    op.create_index("ix_user_subjects_subject_code", "user_subjects", ["subject_code"])

    subjects = sa.table(
        "subject_catalog",
        sa.column("id", sa.UUID()),
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("exam_types", postgresql.JSONB()),
        sa.column("sort_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    rows = [
        {
            "id": uuid.uuid4(),
            "code": code,
            "name": name,
            "exam_types": exam_types,
            "sort_order": sort_order,
            "is_active": True,
        }
        for code, name, exam_types, sort_order in SUBJECT_SEED
    ]
    op.bulk_insert(subjects, rows)


def downgrade() -> None:
    op.drop_table("user_subjects")
    op.drop_table("subject_catalog")
    op.drop_table("exam_targets")
    op.drop_table("students")
