"""M33 — Smart Night Scheduler.

ENABLE_MIDNIGHT_SCHEDULER=true iken her gün Istanbul 00:00'da
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


def seconds_until_next_midnight() -> float:
    now = _now_istanbul()
    nxt = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(1.0, (nxt - now).total_seconds())


async def midnight_question_pool_loop() -> None:
    mgr = QuestionPoolManagerService()
    logger.info(
        "M33: QuestionPool scheduler loop starting dry_run=%s",
        settings.QUESTION_POOL_SCHEDULER_DRY_RUN,
    )

    while True:
        wait_s = seconds_until_next_midnight()
        logger.info("M33: Next question pool fill in %.0f seconds", wait_s)
        await asyncio.sleep(wait_s)
        try:
            async with AsyncSessionLocal() as db:
                await mgr.fill_missing(db=db, dry_run=settings.QUESTION_POOL_SCHEDULER_DRY_RUN)
        except Exception:
            # This branch should never hit; real db session is injected elsewhere
            logger.exception("M33: scheduler fill_missing failed")

