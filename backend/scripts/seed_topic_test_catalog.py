"""Seed / audit Topic Test Catalog (launch stock).

Usage (from backend/):
  python -m scripts.seed_topic_test_catalog --audit
  python -m scripts.seed_topic_test_catalog --dry-run
  python -m scripts.seed_topic_test_catalog --pilot --dry-run
  python -m scripts.seed_topic_test_catalog --pilot
  python -m scripts.seed_topic_test_catalog --exam kpss_lisans --limit 5
  python -m scripts.seed_topic_test_catalog --report-out data/seed_report.json

NEVER run full catalog without --confirm-full.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.constants import TOPIC_TEST_DIFFICULTIES, TOPIC_TEST_QUESTION_COUNT
from app.core.config import settings
from app.database.base import AsyncSessionLocal
from app.schemas.topic_test import TopicTestReleaseRequest
from app.services.question_pool_inventory_catalog import iter_catalog_inventory_slots
from app.services.topic_test_catalog_service import iso_week_id
from app.services.topic_test_release_service import TopicTestReleaseService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("seed_topic_test_catalog")

# Launch pilot: 3 exams × 3 topics (diverse subjects within each exam).
PILOT_EXAM_LIMITS = {
    "kpss_lisans": 3,
    "tyt": 3,
    "ayt_sayisal": 3,
}


def _all_unique_topics() -> list[tuple[str, str, str, str | None, str | None, str]]:
    """(exam, subject_code, topic_code, subject_name, topic_name, exam_label)."""
    seen: set[tuple[str, str, str]] = set()
    out: list[tuple[str, str, str, str | None, str | None, str]] = []
    for slot in iter_catalog_inventory_slots():
        key = (slot.exam, slot.subject_code, slot.topic_code)
        if key in seen or not slot.topic_code:
            continue
        seen.add(key)
        out.append(
            (
                slot.exam,
                slot.subject_code,
                slot.topic_code,
                slot.subject_name,
                slot.topic_name,
                slot.exam_label,
            )
        )
    return out


def build_audit_report() -> dict:
    topics = _all_unique_topics()
    by_exam: dict[str, dict] = defaultdict(
        lambda: {"topics": 0, "subjects": set(), "label": ""}
    )
    for exam, sub, _top, _sn, _tn, label in topics:
        by_exam[exam]["topics"] += 1
        by_exam[exam]["subjects"].add(sub)
        by_exam[exam]["label"] = label or exam

    n = len(topics)
    diffs = list(TOPIC_TEST_DIFFICULTIES)
    per_topic_tests = len(diffs)
    per_topic_q = per_topic_tests * TOPIC_TEST_QUESTION_COUNT
    exam_rows = []
    for exam, d in sorted(by_exam.items(), key=lambda x: -x[1]["topics"]):
        t = d["topics"]
        exam_rows.append(
            {
                "exam": exam,
                "label": d["label"],
                "subjects": len(d["subjects"]),
                "topics": t,
                "easy_tests": t,
                "medium_tests": t,
                "hard_tests": t,
                "total_tests": t * per_topic_tests,
                "total_questions": t * per_topic_q,
            }
        )

    keys_present = sum(
        1
        for k in (
            settings.GEMINI_API_KEY,
            settings.GEMINI_API_KEY_2,
            settings.GEMINI_API_KEY_3,
        )
        if (k or "").strip() and not str(k).startswith("<MagicMock")
    )

    # Batch generate does generate + verify ≈ 2 Gemini calls per batch of ≤10.
    # With ~40–60% accept rate expect ~2–3 batches/difficulty → ~4–6 calls/diff.
    calls_per_diff_low = 2
    calls_per_diff_high = 6
    total_diffs = n * per_topic_tests
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "week_id": iso_week_id(),
        "audit": {
            "exam_count": len(by_exam),
            "subject_count": len({(e, s) for e, s, *_ in topics}),
            "topic_count": n,
        },
        "target": {
            "easy_tests": n,
            "medium_tests": n,
            "hard_tests": n,
            "total_tests": n * per_topic_tests,
            "total_questions": n * per_topic_q,
            "questions_per_test": TOPIC_TEST_QUESTION_COUNT,
            "difficulties": diffs,
        },
        "by_exam": exam_rows,
        "quota": {
            "gemini_keys_configured": keys_present,
            "ai_provider": settings.AI_PROVIDER,
            "estimated_gemini_calls_low": total_diffs * calls_per_diff_low,
            "estimated_gemini_calls_high": total_diffs * calls_per_diff_high,
            "notes": [
                "batch_generate = 1 generate + 1 verify call per batch (≤10 plans)",
                "reject/retry increases batches; high estimate assumes ~50% accept",
                "free-tier flash-lite historically ~500 req/day/key — verify current Google limits",
                f"with {keys_present} key(s): theoretical day capacity ~{keys_present * 500} calls (if 500/day/key)",
            ],
            "full_seed_duration_hours_estimate": round(
                (total_diffs * calls_per_diff_high) / max(1, keys_present * 30), 1
            ),
            "quota_risk": "HIGH"
            if keys_present < 2
            else ("MEDIUM" if n > 100 else "LOW"),
        },
    }


def select_topics(
    *,
    exam: str | None,
    limit: int | None,
    pilot: bool,
    topic_codes: list[str] | None,
) -> list[tuple[str, str, str, str | None, str | None]]:
    all_topics = _all_unique_topics()
    if topic_codes:
        wanted = {c.strip() for c in topic_codes if c.strip()}
        return [
            (e, s, t, sn, tn)
            for e, s, t, sn, tn, _ in all_topics
            if t in wanted
        ]

    if pilot:
        picked: list[tuple[str, str, str, str | None, str | None]] = []
        counts: Counter[str] = Counter()
        used_subjects: set[tuple[str, str]] = set()

        def _is_junk(topic_code: str, topic_name: str | None) -> bool:
            blob = f"{topic_code} {topic_name or ''}".lower()
            return any(
                x in blob
                for x in ("uncertain", "sınıflanamayan", "siniflanamayan", "diğer", "diger", "other")
            )

        # Pass 1: distinct subjects, skip junk topics
        for e, s, t, sn, tn, _ in all_topics:
            need = PILOT_EXAM_LIMITS.get(e)
            if need is None or counts[e] >= need:
                continue
            if _is_junk(t, tn):
                continue
            if (e, s) in used_subjects:
                continue
            used_subjects.add((e, s))
            picked.append((e, s, t, sn, tn))
            counts[e] += 1

        # Pass 2: fill remaining with non-junk even if subject repeats
        if len(picked) < sum(PILOT_EXAM_LIMITS.values()):
            for e, s, t, sn, tn, _ in all_topics:
                need = PILOT_EXAM_LIMITS.get(e)
                if need is None or counts[e] >= need:
                    continue
                if _is_junk(t, tn):
                    continue
                if any(p[2] == t for p in picked):
                    continue
                picked.append((e, s, t, sn, tn))
                counts[e] += 1
        return picked

    out: list[tuple[str, str, str, str | None, str | None]] = []
    for e, s, t, sn, tn, _ in all_topics:
        if exam and e != exam.strip().lower():
            continue
        out.append((e, s, t, sn, tn))
        if limit is not None and len(out) >= limit:
            break
    return out


async def run_seed(
    *,
    dry_run: bool,
    topics: list[tuple[str, str, str, str | None, str | None]],
    week_id: str | None = None,
) -> dict:
    week = (week_id or "").strip() or iso_week_id()
    created = skipped = failed = 0
    details: list[dict] = []
    published_before = 0

    async with AsyncSessionLocal() as db:
        svc = TopicTestReleaseService(db)
        for i, (ex, sub, top, sn, tn) in enumerate(topics, 1):
            logger.info(
                "[%s/%s] %s release exam=%s subject=%s topic=%s",
                i,
                len(topics),
                "DRY-RUN" if dry_run else "SEED",
                ex,
                sub,
                top,
            )
            try:
                result = await svc.release_topic_week(
                    TopicTestReleaseRequest(
                        exam=ex,
                        subject_code=sub,
                        topic_code=top,
                        week_id=week,
                        subject_name=sn,
                        topic_name=tn,
                        dry_run=dry_run,
                        fill_pool_if_short=not dry_run,
                    )
                )
                created += len(result.created)
                skipped += len(result.skipped)
                failed += len(result.failed)
                details.append(
                    {
                        "exam": ex,
                        "subject_code": sub,
                        "topic_code": top,
                        "topic_name": tn,
                        "created": result.created,
                        "skipped": result.skipped,
                        "failed": result.failed,
                    }
                )
                if not dry_run:
                    await db.commit()
            except Exception as exc:
                logger.exception(
                    "topic seed aborted for topic=%s — continuing: %s", top, exc
                )
                try:
                    await db.rollback()
                except Exception:
                    pass
                failed += 3
                details.append(
                    {
                        "exam": ex,
                        "subject_code": sub,
                        "topic_code": top,
                        "error": str(exc),
                        "failed": ["easy:crash", "medium:crash", "hard:crash"],
                    }
                )

        # Post status snapshot (DB)
        if not dry_run:
            from sqlalchemy import func, select

            from app.models.topic_test import TopicTest, TopicTestStatus

            rows = (
                await db.execute(
                    select(TopicTest.status, func.count())
                    .where(TopicTest.week_id == week)
                    .group_by(TopicTest.status)
                )
            ).all()
            status_counts = {str(s): int(c) for s, c in rows}
        else:
            status_counts = {}

    return {
        "week_id": week,
        "dry_run": dry_run,
        "topics": len(topics),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "status_counts": status_counts,
        "details": details,
        "published_before_hint": published_before,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Seed topic test catalog")
    p.add_argument("--audit", action="store_true", help="Catalog size report only (no DB)")
    p.add_argument(
        "--plan-only",
        action="store_true",
        help="Select topics and print plan without DB/Gemini",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--pilot", action="store_true", help="9-topic launch pilot")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--exam", type=str, default=None)
    p.add_argument("--week-id", type=str, default=None)
    p.add_argument(
        "--topic-code",
        action="append",
        default=None,
        help="Repeatable topic_code filter",
    )
    p.add_argument(
        "--confirm-full",
        action="store_true",
        help="Required to seed all topics without --pilot/--limit/--exam/--topic-code",
    )
    p.add_argument("--report-out", type=str, default=None)
    args = p.parse_args()

    audit = build_audit_report()
    if args.audit:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        if args.report_out:
            Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.report_out).write_text(
                json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        return

    topics = select_topics(
        exam=args.exam,
        limit=args.limit,
        pilot=args.pilot,
        topic_codes=args.topic_code,
    )
    if not topics:
        logger.error("No topics selected")
        sys.exit(2)

    if args.plan_only:
        plan = {
            "week_id": args.week_id or audit["week_id"],
            "pilot": args.pilot,
            "topic_count": len(topics),
            "tests": len(topics) * 3,
            "questions": len(topics) * 30,
            "topics": [
                {
                    "exam": e,
                    "subject_code": s,
                    "topic_code": t,
                    "subject_name": sn,
                    "topic_name": tn,
                }
                for e, s, t, sn, tn in topics
            ],
            "quota": audit["quota"],
        }
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if args.report_out:
            Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.report_out).write_text(
                json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        return

    is_scoped = bool(args.pilot or args.limit or args.exam or args.topic_code)
    if not args.dry_run and not is_scoped and not args.confirm_full:
        logger.error(
            "Refusing full seed without --confirm-full. "
            "Use --pilot or --limit/--exam first."
        )
        sys.exit(2)

    logger.info(
        "Selected %s topics (pilot=%s dry_run=%s week=%s)",
        len(topics),
        args.pilot,
        args.dry_run,
        args.week_id or audit["week_id"],
    )
    for e, s, t, _sn, tn in topics:
        logger.info("  - %s / %s / %s (%s)", e, s, t, tn)

    result = asyncio.run(
        run_seed(dry_run=args.dry_run, topics=topics, week_id=args.week_id)
    )
    report = {
        "audit": audit["audit"],
        "target_full": audit["target"],
        "quota": audit["quota"],
        "selection": {
            "pilot": args.pilot,
            "exam": args.exam,
            "limit": args.limit,
            "topic_count": len(topics),
            "topics": [
                {"exam": e, "subject_code": s, "topic_code": t, "topic_name": tn}
                for e, s, t, _sn, tn in topics
            ],
        },
        "run": result,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.report_out:
        Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Wrote report %s", args.report_out)


if __name__ == "__main__":
    main()
