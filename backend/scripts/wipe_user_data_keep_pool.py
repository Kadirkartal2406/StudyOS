"""Wipe all user rows; keep question pool and published topic tests.

Default: --dry-run (BEGIN → DELETE → snapshot compare → ROLLBACK).
Real delete: --execute (COMMIT only if protected snapshots match).

Never run against production from this agent. Operator must pass --execute.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.core.config import settings  # noqa: E402
from app.services.user_data_wipe import (  # noqa: E402
    PROTECTED_TABLES,
    USER_REPORT_TABLES,
    WIPE_EXPLICIT_TABLES,
    WIPE_ROOT_TABLE,
    assert_wipe_sql_safe,
    count_sql,
    fk_contract_sql,
    snapshot_sql,
    validate_fk_rows,
    wipe_statements,
)


def _redact_db_target(url: str) -> str:
    raw = (url or "").replace("postgresql+asyncpg://", "postgresql://", 1)
    parsed = urlparse(raw)
    db = (parsed.path or "").lstrip("/") or "?"
    host = parsed.hostname or "?"
    return f"{host}/{db}"


async def _scalar_count(conn: AsyncConnection, table: str) -> int | None:
    exists = await conn.execute(
        text("SELECT to_regclass(:reg)"), {"reg": f"public.{table}"}
    )
    if exists.scalar() is None:
        return None
    n = (await conn.execute(text(count_sql(table)))).scalar()
    return int(n or 0)


async def _snapshot(conn: AsyncConnection) -> dict[str, tuple[int, str]]:
    out: dict[str, tuple[int, str]] = {}
    for table in sorted(PROTECTED_TABLES):
        exists = await conn.execute(
            text("SELECT to_regclass(:reg)"), {"reg": f"public.{table}"}
        )
        if exists.scalar() is None:
            raise RuntimeError(f"protected table missing: {table}")
        row = (await conn.execute(text(snapshot_sql(table)))).one()
        out[table] = (int(row.n or 0), str(row.digest or ""))
    return out


async def _user_counts(conn: AsyncConnection) -> dict[str, int | None]:
    counts: dict[str, int | None] = {}
    for table in USER_REPORT_TABLES:
        counts[table] = await _scalar_count(conn, table)
    return counts


async def _assert_fk_contract(conn: AsyncConnection) -> list[tuple[str, str, str, str]]:
    result = await conn.execute(text(fk_contract_sql()))
    rows = [(r.src_table, r.dst_table, r.src_column, r.on_delete) for r in result]
    errors = validate_fk_rows(rows)
    if errors:
        raise RuntimeError("FK contract failed:\n- " + "\n- ".join(errors))
    return rows


def _print_counts(title: str, counts: dict[str, int | None]) -> None:
    print(title)
    for table, n in counts.items():
        label = "absent" if n is None else str(n)
        print(f"  {table:36} {label}")


def _print_snapshot(title: str, snap: dict[str, tuple[int, str]]) -> None:
    print(title)
    for table in sorted(snap):
        n, digest = snap[table]
        print(f"  {table:36} n={n:<8} digest={digest}")


def _diff_snapshots(
    before: dict[str, tuple[int, str]], after: dict[str, tuple[int, str]]
) -> list[str]:
    diffs: list[str] = []
    for table in sorted(PROTECTED_TABLES):
        if before[table] != after[table]:
            diffs.append(
                f"{table}: {before[table]} → {after[table]}"
            )
    return diffs


async def run(*, execute: bool) -> int:
    statements = wipe_statements()
    assert_wipe_sql_safe(statements)

    target = _redact_db_target(settings.DATABASE_URL)
    mode = "EXECUTE (commit if snapshots match)" if execute else "DRY-RUN (always rollback)"
    print(f"mode: {mode}")
    print(f"database: {target}")
    print("protected tables (no DELETE/TRUNCATE/UPDATE):")
    for t in sorted(PROTECTED_TABLES):
        print(f"  KEEP  {t}")
    print("wipe DML:")
    for stmt in statements:
        print(f"  {stmt}")
    print(f"root: DELETE FROM {WIPE_ROOT_TABLE}  (includes system_admin; no allowlist)")
    print(f"explicit (CASCADE does not cover): {', '.join(WIPE_EXPLICIT_TABLES)}")
    print()

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    committed = False
    try:
        async with engine.connect() as conn:
            trans = await conn.begin()
            try:
                await _assert_fk_contract(conn)
                print("FK contract: OK (pool_card_id RESTRICT; pool/tests not tied to users)")
                before_snap = await _snapshot(conn)
                before_users = await _user_counts(conn)
                _print_snapshot("snapshot BEFORE (protected)", before_snap)
                _print_counts("user-data counts BEFORE", before_users)

                for stmt in statements:
                    await conn.execute(text(stmt))

                after_snap = await _snapshot(conn)
                after_users = await _user_counts(conn)
                _print_snapshot("snapshot AFTER (protected)", after_snap)
                _print_counts("user-data counts AFTER", after_users)

                diffs = _diff_snapshots(before_snap, after_snap)
                if diffs:
                    print("PROTECTED SNAPSHOT MISMATCH — ROLLBACK")
                    for line in diffs:
                        print(f"  {line}")
                    await trans.rollback()
                    return 2

                print("protected snapshots identical (count + identity hash)")
                if execute:
                    await trans.commit()
                    committed = True
                    print("COMMITTED user-data wipe")
                    print(
                        "Admin: none remain. Restart the API so "
                        "ensure_admin_user() recreates from ADMIN_BOOTSTRAP_*."
                    )
                else:
                    await trans.rollback()
                    print("DRY-RUN ROLLBACK — no rows committed")
                return 0
            except Exception:
                await trans.rollback()
                raise
    finally:
        await engine.dispose()
        if not committed and execute:
            print("EXECUTE aborted; transaction rolled back")
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Delete all users and user-owned rows. Preserve question_pool_cards, "
            "topic_tests, topic_test_items, exam catalog, and other system tables."
        )
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate wipe in a transaction and ROLLBACK (default)",
    )
    g.add_argument(
        "--execute",
        action="store_true",
        help="COMMIT the wipe only if protected snapshots match",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    execute = bool(args.execute)
    return asyncio.run(run(execute=execute))


if __name__ == "__main__":
    raise SystemExit(main())
