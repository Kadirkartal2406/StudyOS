"""add subject section, enrich catalog, goals.exam_type

Revision ID: j6e7f8a9b0c1
Revises: i5d6e7f8a9b0
Create Date: 2026-07-17 13:15:00.000000

"""

import json
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "j6e7f8a9b0c1"
down_revision: str | None = "i5d6e7f8a9b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (code, name, exam_types, sort_order, section)
ENRICHED = [
    ("tyt_turkce", "Türkçe", ["yks", "tyt"], 10, "tyt"),
    ("tyt_matematik", "Matematik", ["yks", "tyt"], 20, "tyt"),
    ("tyt_sosyal", "Sosyal Bilimler", ["yks", "tyt"], 30, "tyt"),
    ("tyt_fen", "Fen Bilimleri", ["yks", "tyt"], 40, "tyt"),
    ("ayt_matematik", "Matematik", ["yks", "ayt"], 50, "ayt"),
    ("ayt_fizik", "Fizik", ["yks", "ayt"], 60, "ayt"),
    ("ayt_kimya", "Kimya", ["yks", "ayt"], 70, "ayt"),
    ("ayt_biyoloji", "Biyoloji", ["yks", "ayt"], 80, "ayt"),
    ("ayt_edebiyat", "Edebiyat", ["yks", "ayt"], 90, "ayt"),
    ("ayt_tarih", "Tarih", ["yks", "ayt"], 100, "ayt"),
    ("ayt_cografya", "Coğrafya", ["yks", "ayt"], 110, "ayt"),
    ("ayt_felsefe", "Felsefe", ["yks", "ayt"], 120, "ayt"),
    ("kpss_gy", "Genel Yetenek", ["kpss"], 10, None),
    ("kpss_gk", "Genel Kültür", ["kpss"], 20, None),
    ("kpss_eb", "Eğitim Bilimleri", ["kpss"], 30, None),
    ("lgs_turkce", "Türkçe", ["lgs"], 10, None),
    ("lgs_matematik", "Matematik", ["lgs"], 20, None),
    ("lgs_fen", "Fen Bilimleri", ["lgs"], 30, None),
    ("lgs_inkilap", "İnkılap Tarihi", ["lgs"], 40, None),
    ("lgs_din", "Din Kültürü", ["lgs"], 50, None),
    ("lgs_ingilizce", "İngilizce", ["lgs"], 60, None),
    ("yds_vocabulary", "Vocabulary", ["yds"], 10, None),
    ("yds_grammar", "Grammar", ["yds"], 20, None),
    ("yds_reading", "Reading", ["yds"], 30, None),
    ("yds_listening", "Listening", ["yds"], 40, None),
    ("ales_sayisal", "Sayısal", ["ales"], 10, None),
    ("ales_sozel", "Sözel", ["ales"], 20, None),
    ("dgs_sayisal", "Sayısal", ["dgs"], 10, None),
    ("dgs_sozel", "Sözel", ["dgs"], 20, None),
]

LEGACY_DEACTIVATE = (
    "yks_turkce",
    "yks_matematik",
    "yks_geometri",
    "yks_fizik",
    "yks_kimya",
    "yks_biyoloji",
    "yks_tarih",
    "yks_cografya",
    "yks_felsefe",
    "yks_din",
    "yds_ingilizce",
    "yds_kelime",
    "yds_okuma",
)


def upgrade() -> None:
    op.add_column(
        "subject_catalog",
        sa.Column("section", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "goals",
        sa.Column("exam_type", sa.String(length=20), nullable=True),
    )
    op.create_index("ix_goals_exam_type", "goals", ["exam_type"])

    conn = op.get_bind()
    for code, name, exam_types, sort_order, section in ENRICHED:
        exists = conn.execute(
            sa.text("SELECT id FROM subject_catalog WHERE code = :code"),
            {"code": code},
        ).fetchone()
        params = {
            "code": code,
            "name": name,
            "et": json.dumps(exam_types),
            "so": sort_order,
            "sec": section,
        }
        if exists:
            conn.execute(
                sa.text(
                    "UPDATE subject_catalog SET name = :name, exam_types = CAST(:et AS jsonb), "
                    "sort_order = :so, section = :sec, is_active = true WHERE code = :code"
                ),
                params,
            )
        else:
            conn.execute(
                sa.text(
                    "INSERT INTO subject_catalog "
                    "(id, code, name, exam_types, sort_order, is_active, section) "
                    "VALUES (:id, :code, :name, CAST(:et AS jsonb), :so, true, :sec)"
                ),
                {**params, "id": str(uuid.uuid4())},
            )

    for code in LEGACY_DEACTIVATE:
        conn.execute(
            sa.text("UPDATE subject_catalog SET is_active = false WHERE code = :code"),
            {"code": code},
        )


def downgrade() -> None:
    op.drop_index("ix_goals_exam_type", table_name="goals")
    op.drop_column("goals", "exam_type")
    op.drop_column("subject_catalog", "section")
