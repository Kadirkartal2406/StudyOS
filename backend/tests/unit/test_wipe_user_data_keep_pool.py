"""User wipe must not touch question_pool_cards / topic_tests (no live DB)."""

from __future__ import annotations

import sqlite3

import pytest

import app.models  # noqa: F401 — register metadata
from app.database.base import Base
from app.models.question_pool import QuestionPoolCard
from app.models.topic_test import TopicTest, TopicTestAttempt, TopicTestItem
from app.services.user_data_wipe import (
    ALLOWED_DELETE_TABLES,
    PROTECTED_TABLES,
    USER_REPORT_TABLES,
    WIPE_EXPLICIT_TABLES,
    WIPE_ROOT_TABLE,
    assert_wipe_sql_safe,
    validate_fk_rows,
    wipe_statements,
)
from scripts.wipe_user_data_keep_pool import parse_args


def test_wipe_sql_only_allowlisted_deletes():
    stmts = wipe_statements()
    blob = "\n".join(stmts).lower()
    for table in sorted(PROTECTED_TABLES):
        assert table not in blob
    assert stmts[-1] == f"DELETE FROM {WIPE_ROOT_TABLE}"
    assert {s.split()[-1] for s in stmts} <= ALLOWED_DELETE_TABLES
    for table in WIPE_EXPLICIT_TABLES:
        assert f"DELETE FROM {table}" in stmts
    assert_wipe_sql_safe(stmts)


def test_wipe_sql_rejects_pool_and_test_dml():
    with pytest.raises(RuntimeError, match="protected"):
        assert_wipe_sql_safe(["DELETE FROM question_pool_cards"])
    with pytest.raises(RuntimeError, match="protected"):
        assert_wipe_sql_safe(["TRUNCATE topic_tests"])
    with pytest.raises(RuntimeError, match="protected"):
        assert_wipe_sql_safe(["UPDATE topic_test_items SET content_hash = 'x'"])
    with pytest.raises(RuntimeError, match="non-allowlisted"):
        assert_wipe_sql_safe(["DELETE FROM topic_quiz_generations"])


def test_cli_defaults_to_dry_run():
    assert parse_args([]).execute is False
    assert parse_args(["--dry-run"]).execute is False
    assert parse_args(["--execute"]).execute is True
    with pytest.raises(SystemExit):
        parse_args(["--dry-run", "--execute"])


def test_model_fk_contract_pool_restrict_and_no_user_link():
    assert "user_id" not in QuestionPoolCard.__table__.c
    assert "user_id" not in TopicTest.__table__.c

    pool_fks = [
        (table.name, fk.parent.name, (fk.ondelete or "").upper())
        for table in Base.metadata.tables.values()
        for fk in table.foreign_keys
        if fk.column.table.name == "question_pool_cards"
    ]
    assert pool_fks == [("topic_test_items", "pool_card_id", "RESTRICT")]

    item_pool = [
        fk
        for fk in TopicTestItem.__table__.foreign_keys
        if fk.column.table.name == "question_pool_cards"
    ]
    assert len(item_pool) == 1
    assert (item_pool[0].ondelete or "").upper() == "RESTRICT"

    user_fk = [
        fk
        for fk in TopicTestAttempt.__table__.foreign_keys
        if fk.column.table.name == "users"
    ]
    assert len(user_fk) == 1
    assert (user_fk[0].ondelete or "").upper() == "CASCADE"

    for table in Base.metadata.tables.values():
        for fk in table.foreign_keys:
            if fk.column.table.name != "users":
                continue
            rule = (fk.ondelete or "").upper()
            assert rule in {"CASCADE", "SET NULL"}, (table.name, fk.parent.name, rule)
            assert table.name not in PROTECTED_TABLES


def test_validate_fk_rows_rejects_cascade_to_pool():
    ok = [
        (
            "topic_test_items",
            "question_pool_cards",
            "pool_card_id",
            "RESTRICT",
        ),
        ("topic_test_attempts", "users", "user_id", "CASCADE"),
        ("topic_test_attempts", "topic_tests", "test_id", "CASCADE"),
        (
            "topic_test_attempt_answers",
            "topic_test_items",
            "item_id",
            "CASCADE",
        ),
    ]
    assert validate_fk_rows(ok) == []
    bad = ok + [
        ("evil", "question_pool_cards", "pool_card_id", "CASCADE"),
    ]
    errors = validate_fk_rows(bad)
    assert any("CASCADE" in e and "question_pool_cards" in e for e in errors)


def test_report_tables_do_not_include_pool():
    overlap = PROTECTED_TABLES.intersection(USER_REPORT_TABLES)
    assert overlap == set()
    assert "question_pool_cards" not in USER_REPORT_TABLES
    assert "topic_tests" not in USER_REPORT_TABLES
    assert "topic_test_items" not in USER_REPORT_TABLES


def test_sqlite_delete_users_keeps_pool_cards_and_test_items():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(
        """
        CREATE TABLE users (id TEXT PRIMARY KEY);
        CREATE TABLE question_pool_cards (
            id TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL
        );
        CREATE TABLE topic_tests (id TEXT PRIMARY KEY, status TEXT NOT NULL);
        CREATE TABLE topic_test_items (
            id TEXT PRIMARY KEY,
            test_id TEXT NOT NULL REFERENCES topic_tests(id) ON DELETE CASCADE,
            pool_card_id TEXT NOT NULL REFERENCES question_pool_cards(id) ON DELETE RESTRICT
        );
        CREATE TABLE topic_test_attempts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            test_id TEXT NOT NULL REFERENCES topic_tests(id) ON DELETE CASCADE
        );
        CREATE TABLE topic_test_attempt_answers (
            id TEXT PRIMARY KEY,
            attempt_id TEXT NOT NULL REFERENCES topic_test_attempts(id) ON DELETE CASCADE,
            item_id TEXT NOT NULL REFERENCES topic_test_items(id) ON DELETE CASCADE
        );
        """
    )
    con.execute("INSERT INTO users VALUES ('u1')")
    con.execute("INSERT INTO question_pool_cards VALUES ('p1', 'fp-keep')")
    con.execute("INSERT INTO topic_tests VALUES ('t1', 'published')")
    con.execute("INSERT INTO topic_test_items VALUES ('i1', 't1', 'p1')")
    con.execute("INSERT INTO topic_test_attempts VALUES ('a1', 'u1', 't1')")
    con.execute("INSERT INTO topic_test_attempt_answers VALUES ('ans1', 'a1', 'i1')")
    con.commit()

    con.execute("DELETE FROM users")
    con.commit()

    assert con.execute("SELECT COUNT(*) FROM question_pool_cards").fetchone()[0] == 1
    assert con.execute("SELECT fingerprint FROM question_pool_cards").fetchone()[0] == (
        "fp-keep"
    )
    assert con.execute("SELECT COUNT(*) FROM topic_tests").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM topic_test_items").fetchone()[0] == 1
    assert con.execute("SELECT pool_card_id FROM topic_test_items").fetchone()[0] == "p1"
    assert con.execute("SELECT COUNT(*) FROM topic_test_attempts").fetchone()[0] == 0
    assert (
        con.execute("SELECT COUNT(*) FROM topic_test_attempt_answers").fetchone()[0]
        == 0
    )

    with pytest.raises(sqlite3.IntegrityError):
        con.execute("DELETE FROM question_pool_cards")
    con.rollback()
    assert con.execute("SELECT COUNT(*) FROM question_pool_cards").fetchone()[0] == 1
    con.close()
