"""Weekly Topic Test Catalog release scheduler.

Steady schedule: Monday 05:00 Europe/Istanbul.
If the current ISO week has no topic_test rows yet, also fires at the next
05:00 (mid-week catch-up — e.g. this week Thursday night → Friday 05:00).

ENABLE_MIDNIGHT_SCHEDULER must be on. Idempotent per (topic, week_id, difficulty).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.config import settings
from app.database.base import AsyncSessionLocal
from app.models.topic_test import TopicTest
from app.schemas.topic_test import TopicTestReleaseRequest
from app.services.question_pool_inventory_catalog import iter_catalog_inventory_slots
from app.services.topic_test_catalog_service import iso_week_id
from app.services.topic_test_release_service import TopicTestReleaseService

logger = logging.getLogger("studyos.topic_test_weekly_scheduler")

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


def _now_istanbul() -> datetime:
    return datetime.now(_TZ)


def _at_hour(dt: datetime, hour: int) -> datetime:
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0)


def seconds_until_next_monday_0500() -> float:
    now = _now_istanbul()
    days_ahead = (0 - now.weekday()) % 7
    nxt = _at_hour(now + timedelta(days=days_ahead), 5)
    if nxt <= now:
        nxt += timedelta(days=7)
    return max(1.0, (nxt - now).total_seconds())


async def _current_week_has_any_release(week_id: str) -> bool:
    async with AsyncSessionLocal() as db:
        n = await db.scalar(
            select(func.count()).select_from(TopicTest).where(TopicTest.week_id == week_id)
        )
        return int(n or 0) > 0


async def seconds_until_next_topic_test_release() -> float:
    """Monday 05:00 normally; next 05:00 if current ISO week not released yet."""
    now = _now_istanbul()
    week_id = iso_week_id(now)
    monday_wait = seconds_until_next_monday_0500()

    try:
        already = await asyncio.wait_for(
            _current_week_has_any_release(week_id), timeout=10.0
        )
    except Exception:
        logger.exception(
            "TopicTest: week release check failed week_id=%s — assume not released (catch-up 05:00)",
            week_id,
        )
        already = False

    if already:
        return monday_wait

    # Mid-week / first-week catch-up: run at the upcoming 05:00.
    nxt = _at_hour(now, 5)
    if nxt <= now:
        nxt += timedelta(days=1)
    catchup = max(1.0, (nxt - now).total_seconds())
    # Prefer the sooner of catch-up 05:00 and next Monday 05:00.
    wait = min(catchup, monday_wait)
    logger.info(
        "TopicTest: current week %s not released yet — next fire in %.0fs "
        "(catch-up 05:00 or Monday 05:00)",
        week_id,
        wait,
    )
    return wait


# Back-compat aliases
seconds_until_next_monday_0400 = seconds_until_next_monday_0500
seconds_until_next_monday_0300 = seconds_until_next_monday_0500


async def release_current_week(*, dry_run: bool = False, limit: int | None = None) -> dict:
    """Release easy/medium/hard for each catalog topic for current ISO week."""
    week_id = iso_week_id()
    # Deduplicate slots by (exam, subject, topic) — catalog yields medium-only by default
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

    created = skipped = failed = 0
    async with AsyncSessionLocal() as db:
        svc = TopicTestReleaseService(db)
        for exam, sub, top, sub_name, top_name in topics:
            result = await svc.release_topic_week(
                TopicTestReleaseRequest(
                    exam=exam,
                    subject_code=sub,
                    topic_code=top,
                    week_id=week_id,
                    subject_name=sub_name,
                    topic_name=top_name,
                    dry_run=dry_run,
                    fill_pool_if_short=not dry_run,
                )
            )
            created += len(result.created)
            skipped += len(result.skipped)
            failed += len(result.failed)
            if not dry_run:
                await db.commit()
        summary = {
            "week_id": week_id,
            "topics": len(topics),
            "created": created,
            "skipped": skipped,
            "failed": failed,
            "dry_run": dry_run,
        }
        logger.info("topic_test weekly release done %s", summary)
        return summary


async def topic_test_weekly_loop() -> None:
    logger.info(
        "TopicTest weekly scheduler starting dry_run=%s (Monday 05:00 + mid-week catch-up)",
        settings.QUESTION_POOL_SCHEDULER_DRY_RUN,
    )
    while True:
        wait_s = await seconds_until_next_topic_test_release()
        logger.info(
            "TopicTest: next weekly release in %.0f seconds",
            wait_s,
        )
        await asyncio.sleep(wait_s)
        try:
            await release_current_week(
                dry_run=settings.QUESTION_POOL_SCHEDULER_DRY_RUN
            )
        except Exception:
            logger.exception("TopicTest weekly release failed")
