"""Topic Test Catalog — staggered weekly production + Monday publish.

Production window (Europe/Istanbul, 03:00 nightly):
- Mon–Sat: assemble up to 164 tests/night for the *upcoming* ISO week (draft only).
- Sun 03:00: gap-fill remaining tests, then publish all ready drafts.

Users only see PUBLISHED tests (Monday onward). Prior Mon–Sat work stays DRAFT.

ENABLE_MIDNIGHT_SCHEDULER must be on. Idempotent per (topic, week_id, difficulty).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.config import settings
from app.core.constants import (
    TOPIC_TEST_DIFFICULTIES,
    TOPIC_TEST_QUESTION_COUNT,
    normalize_exam_code,
)
from app.database.base import AsyncSessionLocal
from app.models.topic_test import TopicTest, TopicTestItem, TopicTestStatus
from app.schemas.topic_test import TopicTestReleaseRequest
from app.services.question_pool_inventory_catalog import iter_catalog_inventory_slots
from app.services.topic_test_catalog_service import iso_week_id, production_target_week_id
from app.services.topic_test_release_service import TopicTestReleaseService

logger = logging.getLogger("studyos.topic_test_weekly_scheduler")

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")
_NIGHT_HOUR = 3
_TESTS_PER_NIGHT = 164


def _now_istanbul() -> datetime:
    return datetime.now(_TZ)


def _at_hour(dt: datetime, hour: int) -> datetime:
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0)


def seconds_until_next_0300() -> float:
    now = _now_istanbul()
    nxt = _at_hour(now, _NIGHT_HOUR)
    if nxt <= now:
        nxt += timedelta(days=1)
    return max(1.0, (nxt - now).total_seconds())


def catalog_test_slot_count() -> int:
    return len(_iter_catalog_test_slots())


def _iter_catalog_topics(
    limit: int | None = None,
) -> list[tuple[str, str, str, str | None, str | None]]:
    """Deduplicate catalog slots by (exam, subject, topic)."""
    seen: set[tuple[str, str, str]] = set()
    topics: list[tuple[str, str, str, str | None, str | None]] = []
    for slot in iter_catalog_inventory_slots():
        key = (slot.exam, slot.subject_code, slot.topic_code)
        if key in seen:
            continue
        seen.add(key)
        topics.append(
            (
                slot.exam,
                slot.subject_code,
                slot.topic_code,
                slot.subject_name,
                slot.topic_name,
            )
        )
        if limit is not None and len(topics) >= limit:
            break
    return topics


def _iter_catalog_test_slots() -> list[
    tuple[str, str, str, str, str | None, str | None]
]:
    """Stable catalog order: every (topic × difficulty) slot."""
    slots: list[tuple[str, str, str, str, str | None, str | None]] = []
    for exam, sub, top, sub_name, top_name in _iter_catalog_topics():
        for diff in TOPIC_TEST_DIFFICULTIES:
            slots.append((exam, sub, top, diff, sub_name, top_name))
    return slots


async def _complete_slots_for_week(week_id: str) -> set[tuple[str, str, str, str]]:
    """Published tests or drafts with a full question snapshot."""
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(
                    TopicTest.exam,
                    TopicTest.subject_code,
                    TopicTest.topic_code,
                    TopicTest.difficulty,
                    TopicTest.status,
                    TopicTest.id,
                ).where(TopicTest.week_id == week_id)
            )
        ).all()

        complete: set[tuple[str, str, str, str]] = set()
        draft_ids: list = []
        draft_keys: dict = {}
        for exam, sub, top, diff, status, test_id in rows:
            key = (exam, sub, top, diff)
            if status == TopicTestStatus.PUBLISHED:
                complete.add(key)
            elif status == TopicTestStatus.DRAFT:
                draft_ids.append(test_id)
                draft_keys[test_id] = key

        if draft_ids:
            counts = (
                await db.execute(
                    select(TopicTestItem.test_id, func.count())
                    .where(TopicTestItem.test_id.in_(draft_ids))
                    .group_by(TopicTestItem.test_id)
                )
            ).all()
            for test_id, n in counts:
                if int(n or 0) >= TOPIC_TEST_QUESTION_COUNT:
                    complete.add(draft_keys[test_id])
        return complete


def topic_slot_needs_work(
    exam: str,
    subject_code: str,
    topic_code: str,
    difficulty: str,
    complete: set[tuple[str, str, str, str]],
) -> bool:
    exam_n = normalize_exam_code(exam)
    return (
        exam_n,
        subject_code.strip(),
        topic_code.strip(),
        difficulty,
    ) not in complete


async def assemble_batch(
    week_id: str,
    *,
    limit: int,
    dry_run: bool = False,
) -> dict:
    """Assemble up to *limit* pending catalog slots as DRAFT (no publish)."""
    complete = await _complete_slots_for_week(week_id)
    pending = [
        s
        for s in _iter_catalog_test_slots()
        if topic_slot_needs_work(s[0], s[1], s[2], s[3], complete)
    ][:limit]

    if not pending:
        return {
            "week_id": week_id,
            "phase": "assemble",
            "slots_total": catalog_test_slot_count(),
            "slots_complete": len(complete),
            "slots_attempted": 0,
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "dry_run": dry_run,
        }

    created = skipped = failed = 0
    async with AsyncSessionLocal() as db:
        svc = TopicTestReleaseService(db)
        for exam, sub, top, diff, sub_name, top_name in pending:
            outcome = await svc.release_or_skip_one(
                exam=exam,
                subject_code=sub,
                topic_code=top,
                week_id=week_id,
                difficulty=diff,
                subject_name=sub_name,
                topic_name=top_name,
                dry_run=dry_run,
                fill_pool_if_short=not dry_run,
                assemble_only=True,
            )
            if outcome.startswith("created"):
                created += 1
            elif outcome.startswith("skipped"):
                skipped += 1
            else:
                failed += 1
            if not dry_run:
                await db.commit()

    complete_after = await _complete_slots_for_week(week_id)
    summary = {
        "week_id": week_id,
        "phase": "assemble",
        "slots_total": catalog_test_slot_count(),
        "slots_complete": len(complete_after),
        "slots_attempted": len(pending),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "dry_run": dry_run,
    }
    logger.info("topic_test assemble batch %s", summary)
    return summary


async def assemble_all_pending(
    week_id: str, *, dry_run: bool = False
) -> dict:
    """Assemble every remaining slot (Sunday gap-fill)."""
    total = catalog_test_slot_count()
    return await assemble_batch(week_id, limit=total, dry_run=dry_run)


async def publish_week(week_id: str, *, dry_run: bool = False) -> dict:
    """Publish ready drafts; optionally assemble+publish any still missing."""
    if dry_run:
        complete = await _complete_slots_for_week(week_id)
        return {
            "week_id": week_id,
            "phase": "publish",
            "slots_complete": len(complete),
            "slots_total": catalog_test_slot_count(),
            "dry_run": True,
        }

    gap = await assemble_all_pending(week_id, dry_run=False)
    async with AsyncSessionLocal() as db:
        pub = await TopicTestReleaseService(db).publish_ready_drafts(week_id)
        await db.commit()

    complete = await _complete_slots_for_week(week_id)
    summary = {
        "week_id": week_id,
        "phase": "publish",
        "slots_total": catalog_test_slot_count(),
        "slots_complete": len(complete),
        "gap_fill": gap,
        "published": pub.get("published", 0),
        "publish_skipped": pub.get("skipped", 0),
        "publish_failed": pub.get("failed", 0),
        "dry_run": False,
    }
    logger.info("topic_test publish week %s", summary)
    return summary


async def run_nightly_pass(*, dry_run: bool | None = None) -> dict:
    """Single 03:00 pass — Mon–Sat assemble, Sun gap-fill, Mon publish + next batch."""
    dry = settings.QUESTION_POOL_SCHEDULER_DRY_RUN if dry_run is None else dry_run
    now = _now_istanbul()
    wd = now.weekday()

    if wd == 0:
        publish_week_id = iso_week_id(now)
        logger.info(
            "TopicTest Monday 03:00 — publish %s then batch 1 for next week",
            publish_week_id,
        )
        pub = await publish_week(publish_week_id, dry_run=dry)
        nxt = await assemble_batch(
            production_target_week_id(now),
            limit=_TESTS_PER_NIGHT,
            dry_run=dry,
        )
        return {"phase": "monday_publish_and_batch1", "publish": pub, "assemble": nxt}

    if wd == 6:
        week_id = production_target_week_id(now)
        logger.info("TopicTest Sunday 03:00 — gap-fill for %s", week_id)
        return await assemble_all_pending(week_id, dry_run=dry)

    week_id = production_target_week_id(now)
    batch_no = wd + 1
    logger.info(
        "TopicTest nightly assemble week=%s batch=%s/6 limit=%s",
        week_id,
        batch_no,
        _TESTS_PER_NIGHT,
    )
    return await assemble_batch(week_id, limit=_TESTS_PER_NIGHT, dry_run=dry)


# Back-compat for admin / scripts
async def release_current_week(*, dry_run: bool = False, limit: int | None = None) -> dict:
    week_id = production_target_week_id()
    if limit is not None:
        return await assemble_batch(week_id, limit=limit, dry_run=dry_run)
    return await publish_week(week_id, dry_run=dry_run)


async def retry_incomplete_current_week(
    *, dry_run: bool = False, limit: int | None = None
) -> dict:
    week_id = production_target_week_id()
    cap = limit if limit is not None else _TESTS_PER_NIGHT
    return await assemble_batch(week_id, limit=cap, dry_run=dry_run)


async def topic_test_staggered_loop() -> None:
    """Daily 03:00 Istanbul — staggered assemble Mon–Sat, publish Sun."""
    logger.info(
        "TopicTest staggered scheduler starting "
        "(%s tests/night Mon–Sat, Sun publish @03:00) dry_run=%s",
        _TESTS_PER_NIGHT,
        settings.QUESTION_POOL_SCHEDULER_DRY_RUN,
    )
    while True:
        wait_s = seconds_until_next_0300()
        logger.info("TopicTest: next nightly pass in %.0f seconds (03:00)", wait_s)
        await asyncio.sleep(wait_s)
        try:
            await run_nightly_pass()
        except Exception:
            logger.exception("TopicTest nightly pass failed")


# Legacy aliases — old hourly / Monday-05:00 loops removed
topic_test_weekly_loop = topic_test_staggered_loop
