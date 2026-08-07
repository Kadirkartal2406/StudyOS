"""Daily scoring scheduler — her gün 22:30 (Europe/Istanbul) istatistik finalize eder."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.database.base import AsyncSessionLocal
from app.services.booklet_generation import _WARM_EXAMS
from app.services.scoring_engine import ScoringEngine

logger = logging.getLogger("studyos.scoring_scheduler")

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


def _now_istanbul() -> datetime:
    return datetime.now(_TZ)


def seconds_until_next_2230() -> float:
    now = _now_istanbul()
    nxt = now.replace(hour=22, minute=30, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return max(1.0, (nxt - now).total_seconds())


async def finalize_scores_for_today() -> None:
    today = _now_istanbul().date()
    async with AsyncSessionLocal() as db:
        scoring_engine = ScoringEngine(db)
        for exam, _ in _WARM_EXAMS:
            try:
                await scoring_engine.finalize_daily_challenge(today, exam)
            except Exception:
                logger.exception("Failed to finalize daily challenge for %s on %s", exam, today)
                await db.rollback()


async def scoring_loop() -> None:
    """Sürekli: her gece 22:30'da o günün istatistiklerini finalize et."""
    from app.services.ai_cost.flags import midnight_scheduler_enabled

    if not midnight_scheduler_enabled():
        logger.info("Scoring scheduler idle (ENABLE_MIDNIGHT_SCHEDULER off)")
        return

    while True:
        wait_s = seconds_until_next_2230()
        logger.info("Next scoring finalize in %.0f seconds (Istanbul 22:30)", wait_s)
        await asyncio.sleep(wait_s)

        if not midnight_scheduler_enabled():
            logger.info("Scoring scheduler disabled mid-loop — exiting")
            return
            
        try:
            logger.info("Finalizing scores for today")
            await finalize_scores_for_today()
        except Exception:
            logger.exception("Scoring finalization crashed")
        await asyncio.sleep(2)
