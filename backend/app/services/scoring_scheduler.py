"""Weekly scoring finalize — Sunday 22:30 Europe/Istanbul for week Monday packs."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from app.core.week_calendar import current_serve_monday, now_istanbul
from app.services.trial_exam_scheduler import _ALL_EXAMS

logger = logging.getLogger("studyos.scoring_scheduler")


def seconds_until_next_2230() -> float:
    now = now_istanbul()
    nxt = now.replace(hour=22, minute=30, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return max(1.0, (nxt - now).total_seconds())


async def finalize_scores_for_week(week_monday=None) -> None:
    from app.database.base import AsyncSessionLocal
    from app.services.scoring_engine import ScoringEngine

    day = week_monday or current_serve_monday()
    async with AsyncSessionLocal() as db:
        scoring_engine = ScoringEngine(db)
        seen_exams: set[str] = set()
        for exam, _branch in _ALL_EXAMS:
            if exam in seen_exams:
                continue
            seen_exams.add(exam)
            try:
                await scoring_engine.finalize_daily_challenge(day, exam)
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception(
                    "Failed to finalize weekly deneme for %s on %s", exam, day
                )


# Back-compat
async def finalize_scores_for_today() -> None:
    await finalize_scores_for_week()


async def scoring_loop() -> None:
    """Finalize weekly deneme stats on Sunday 22:30; other nights no-op."""
    logger.info("Weekly scoring scheduler started (Sunday 22:30)")
    while True:
        wait_s = seconds_until_next_2230()
        logger.info("Next scoring check in %.0f seconds (Istanbul 22:30)", wait_s)
        await asyncio.sleep(wait_s)
        try:
            now = now_istanbul()
            if now.weekday() == 6:
                logger.info("Sunday 22:30 — finalizing week %s", current_serve_monday(now))
                await finalize_scores_for_week()
            else:
                logger.info("Scoring skip — finalize only on Sunday (weekday=%s)", now.weekday())
        except Exception:
            logger.exception("Scoring finalize crashed")
        await asyncio.sleep(2)
