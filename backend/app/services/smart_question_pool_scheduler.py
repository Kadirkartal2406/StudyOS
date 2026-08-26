"""M33 — Smart Night Scheduler.

ENABLE_MIDNIGHT_SCHEDULER=true iken her gün Istanbul 06:00'da
stock hedeflerini korumak için soru havuzunu "fill-missing" ile günceller.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.database.base import AsyncSessionLocal
from app.services.question_pool_manager import QuestionPoolManagerService

logger = logging.getLogger("studyos.smart_question_pool_scheduler")

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


def _now_istanbul() -> datetime:
    return datetime.now(_TZ)


def seconds_until_next_0600() -> float:
    now = _now_istanbul()
    nxt = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return max(1.0, (nxt - now).total_seconds())


# Back-compat aliases
seconds_until_next_1100 = seconds_until_next_0600
seconds_until_next_0300 = seconds_until_next_0600


async def midnight_question_pool_loop() -> None:
    mgr = QuestionPoolManagerService()
    logger.info(
        "M33: QuestionPool scheduler loop starting dry_run=%s "
        "(runs after deneme+topic nightly jobs; uses remaining AI budget)",
        settings.QUESTION_POOL_SCHEDULER_DRY_RUN,
    )

    while True:
        wait_s = seconds_until_next_0600()
        logger.info(
            "M33: Next question pool fill in %.0f seconds (Istanbul 06:00)", wait_s
        )
        await asyncio.sleep(wait_s)
        try:
            from app.services.ai_cost.budget import get_daily_budget

            budget = get_daily_budget()
            min_rem = int(getattr(settings, "AI_POOL_FILL_MIN_REMAINING", 50) or 0)
            if budget.limit > 0 and budget.remaining() < min_rem:
                logger.info(
                    "M33: skip pool fill — remaining=%s < min=%s (deneme/topic used budget)",
                    budget.remaining(),
                    min_rem,
                )
                continue
            logger.info(
                "M33: pool fill starting remaining_budget=%s limit=%s",
                budget.remaining() if budget.limit > 0 else "unlimited",
                budget.limit,
            )
            async with AsyncSessionLocal() as db:
                summary = await mgr.fill_missing(
                    db=db, dry_run=settings.QUESTION_POOL_SCHEDULER_DRY_RUN
                )
            logger.info("M33: pool fill done %s", summary)
        except Exception:
            logger.exception("M33: scheduler fill_missing failed")
