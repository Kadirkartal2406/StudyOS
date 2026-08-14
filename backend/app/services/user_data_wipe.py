"""User-data wipe contract — never mutates question pool / published tests.

SQL builders only emit DELETE against the explicit user wipe allowlist.
Protected tables must not appear in DELETE / TRUNCATE / UPDATE.
"""

from __future__ import annotations

import re
from typing import Iterable

# ---------------------------------------------------------------------------
# Protected system assets — NEVER in DML from this wipe
# ---------------------------------------------------------------------------

PROTECTED_TABLES: frozenset[str] = frozenset(
    {
        "question_pool_cards",
        "question_pool_generation_history",
        "question_pool_generation_locks",
        "topic_tests",
        "topic_test_items",
        "ei_exams",
        "ei_packs",
        "ei_subjects",
        "ei_topics",
        "subject_catalog",
        "topic_catalog",
        "exam_style_profiles",
        "exam_style_stats",
        "educational_assets",
        "educational_asset_nodes",
        "educational_asset_versions",
        "achievements",
        "osym_coefficients",
        "shared_daily_booklets",
        "shared_daily_booklet_questions",
        "alembic_version",
    }
)

# Identity columns hashed in the pre/post snapshot (must include `id` except alembic).
PROTECTED_SNAPSHOT_COLUMNS: dict[str, tuple[str, ...]] = {
    "question_pool_cards": (
        "id",
        "fingerprint",
        "content_hash",
        "exam",
        "subject_code",
        "topic_code",
    ),
    "question_pool_generation_history": (
        "id",
        "exam",
        "subject_code",
        "topic_code",
        "accepted",
        "rejected",
    ),
    "question_pool_generation_locks": ("id", "lock_key"),
    "topic_tests": (
        "id",
        "exam",
        "subject_code",
        "topic_code",
        "week_id",
        "difficulty",
        "status",
        "question_count",
    ),
    "topic_test_items": ("id", "test_id", "pool_card_id", "content_hash", "ord_index"),
    "ei_exams": ("id", "code"),
    "ei_packs": ("id", "code"),
    "ei_subjects": ("id", "code"),
    "ei_topics": ("id", "code", "exam_code", "subject_code"),
    "subject_catalog": ("id", "code"),
    "topic_catalog": ("id", "code", "subject_code"),
    "exam_style_profiles": ("id", "exam_code"),
    "exam_style_stats": ("id", "exam_code", "subject_code", "skill_type"),
    "educational_assets": ("id", "asset_id", "version"),
    "educational_asset_nodes": ("id", "node_id"),
    "educational_asset_versions": ("id", "version"),
    "achievements": ("id", "code"),
    "osym_coefficients": ("id", "exam_type", "year"),
    "shared_daily_booklets": ("id", "exam_type", "challenge_date"),
    "shared_daily_booklet_questions": ("id", "booklet_id", "ord_index"),
    "alembic_version": ("version_num",),
}

assert PROTECTED_TABLES == frozenset(PROTECTED_SNAPSHOT_COLUMNS)

# Explicit DELETEs (CASCADE from users does not cover these).
WIPE_EXPLICIT_TABLES: tuple[str, ...] = (
    "analytics_events",
    "beta_feedback",
    "daily_challenge_statistics",
)

# Root delete — ON DELETE CASCADE walks the user tree (including system_admin).
WIPE_ROOT_TABLE = "users"

# Counted for the before/after user-data report (CASCADE children + explicit).
USER_REPORT_TABLES: tuple[str, ...] = (
    "users",
    "refresh_tokens",
    "password_reset_tokens",
    "notification_preferences",
    "students",
    "exam_targets",
    "user_subjects",
    "study_plans",
    "study_sessions",
    "study_resources",
    "study_workspaces",
    "annotation_layers",
    "activities",
    "question_records",
    "memories",
    "conversations",
    "messages",
    "exams",
    "exam_results",
    "goals",
    "planner_drafts",
    "revision_items",
    "revision_schedules",
    "revision_reviews",
    "generated_questions",
    "topic_evidence",
    "topic_confidence",
    "behavioral_memory",
    "topic_quiz_generations",
    "topic_quiz_items",
    "assessment_sessions",
    "assessment_questions",
    "daily_challenges",
    "daily_challenge_scores",
    "estimated_score_snapshots",
    "knowledge_notebooks",
    "knowledge_sources",
    "knowledge_chunks",
    "knowledge_citations",
    "user_achievements",
    "achievement_progress",
    "qie_human_evaluations",
    "topic_test_attempts",
    "topic_test_attempt_answers",
    "analytics_events",
    "beta_feedback",
    "daily_challenge_statistics",
)

_IDENT = re.compile(r"^[a-z][a-z0-9_]*$")
_DML_TABLE = re.compile(
    r"\b(?:DELETE\s+FROM|TRUNCATE(?:\s+TABLE)?|UPDATE)\s+([a-z][a-z0-9_]*)",
    re.IGNORECASE,
)

ALLOWED_DELETE_TABLES: frozenset[str] = frozenset(
    (WIPE_ROOT_TABLE,) + WIPE_EXPLICIT_TABLES
)


def _ident(name: str) -> str:
    if not _IDENT.fullmatch(name):
        raise ValueError(f"unsafe SQL identifier: {name!r}")
    return name


def wipe_statements() -> tuple[str, ...]:
    """Only DELETEs against the user-data allowlist. No WHERE (all users)."""
    stmts: list[str] = []
    for table in WIPE_EXPLICIT_TABLES:
        stmts.append(f"DELETE FROM {_ident(table)}")
    stmts.append(f"DELETE FROM {_ident(WIPE_ROOT_TABLE)}")
    assert_wipe_sql_safe(stmts)
    return tuple(stmts)


def assert_wipe_sql_safe(statements: Iterable[str]) -> None:
    """Refuse any DML that names a protected table."""
    for stmt in statements:
        if ";" in stmt.strip().rstrip(";"):
            raise RuntimeError(f"refusing multi-statement SQL: {stmt!r}")
        for match in _DML_TABLE.finditer(stmt):
            table = match.group(1).lower()
            if table in PROTECTED_TABLES:
                raise RuntimeError(
                    f"refusing DML on protected table {table}: {stmt}"
                )
            verb = match.group(0).split()[0].upper()
            if verb in {"DELETE", "TRUNCATE", "UPDATE"} and table not in ALLOWED_DELETE_TABLES:
                raise RuntimeError(
                    f"refusing DML on non-allowlisted table {table}: {stmt}"
                )


def snapshot_sql(table: str) -> str:
    cols = PROTECTED_SNAPSHOT_COLUMNS[table]
    table_sql = _ident(table)
    col_sql = ", ".join(f"COALESCE({_ident(c)}::text, '')" for c in cols)
    order_col = "id" if "id" in cols else cols[0]
    return (
        f"SELECT COUNT(*)::bigint AS n, "
        f"md5(COALESCE(string_agg(concat_ws('|', {col_sql}), E'\\n' "
        f"ORDER BY {_ident(order_col)}::text), '')) AS digest "
        f"FROM {table_sql}"
    )


def count_sql(table: str) -> str:
    return f"SELECT COUNT(*)::bigint AS n FROM {_ident(table)}"


def fk_contract_sql() -> str:
    """Inspect FKs that touch protected tables or users."""
    return """
    SELECT
        src.relname AS src_table,
        dst.relname AS dst_table,
        a.attname AS src_column,
        CASE c.confdeltype
            WHEN 'a' THEN 'NO ACTION'
            WHEN 'r' THEN 'RESTRICT'
            WHEN 'c' THEN 'CASCADE'
            WHEN 'n' THEN 'SET NULL'
            WHEN 'd' THEN 'SET DEFAULT'
            ELSE c.confdeltype::text
        END AS on_delete
    FROM pg_constraint c
    JOIN pg_class src ON src.oid = c.conrelid
    JOIN pg_class dst ON dst.oid = c.confrelid
    JOIN pg_namespace nsp ON nsp.oid = src.relnamespace
    JOIN LATERAL unnest(c.conkey) WITH ORDINALITY AS ck(attnum, ord) ON true
    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ck.attnum
    WHERE c.contype = 'f'
      AND nsp.nspname = 'public'
    """


def validate_fk_rows(rows: Iterable[tuple[str, str, str, str]]) -> list[str]:
    """Return human-readable contract violations (empty = ok)."""
    errors: list[str] = []
    saw_pool_restrict = False
    for src, dst, col, on_delete in rows:
        rule = (on_delete or "").upper().replace(" ", "_")
        if src in PROTECTED_TABLES and dst == "users":
            errors.append(f"protected {src}.{col} must not reference users")
        if src in {"question_pool_cards", "topic_tests", "topic_test_items"} and dst == "users":
            errors.append(f"{src}.{col} unexpectedly references users")
        if dst == "question_pool_cards" and rule == "CASCADE":
            errors.append(
                f"{src}.{col} ON DELETE CASCADE → question_pool_cards "
                "(pool cards would be deleted)"
            )
        if (
            src == "topic_test_items"
            and dst == "question_pool_cards"
            and col == "pool_card_id"
        ):
            if rule not in {"RESTRICT", "NO_ACTION"}:
                errors.append(
                    f"topic_test_items.pool_card_id on_delete={on_delete!r} "
                    "(expected RESTRICT)"
                )
            else:
                saw_pool_restrict = True
    if not saw_pool_restrict:
        errors.append(
            "missing topic_test_items.pool_card_id → question_pool_cards RESTRICT"
        )
    return errors
