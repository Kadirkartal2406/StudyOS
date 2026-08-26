"""Daily shared booklet scheduler — deprecated; weekly deneme owns packs.

Kept as a no-op loop so ENABLE_AUTO_BOOKLET / lifespan wiring stays stable.
"""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger("studyos.booklet_scheduler")


async def generate_booklets_for_date(challenge_date) -> bool:
    """Deprecated — use trial_exam_scheduler.generate_trial_exams_for_date."""
    from app.services.trial_exam_scheduler import generate_trial_exams_for_date

    return await generate_trial_exams_for_date(challenge_date)


async def generate_until_complete(challenge_date) -> None:
    await generate_booklets_for_date(challenge_date)


async def midnight_booklet_loop() -> None:
    """No-op: weekly deneme scheduler (03:00) produces all packs."""
    logger.info(
        "Booklet scheduler idle — weekly deneme scheduler owns pack production"
    )
    while True:
        await asyncio.sleep(86400.0)
