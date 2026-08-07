"""Trial exam (deneme) scheduler — her gün 03:00 (Europe/Istanbul) Gemini üretimi."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.services.booklet_generation import run_shared_booklet_generation
from app.services.booklet_generation import _WARM_EXAMS

logger = logging.getLogger("studyos.trial_exam_scheduler")

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")
_RESUME_INTERVAL_SECONDS = 1800.0

def _now_istanbul() -> datetime:
    return datetime.now(_TZ)

def seconds_until_next_0300() -> float:
    now = _now_istanbul()
    nxt = now.replace(hour=3, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return max(1.0, (nxt - now).total_seconds())

async def generate_trial_exams_for_date(challenge_date) -> bool:
    """Belirli gün için tüm deneme (trial exam) pack'lerini üretir."""
    from app.database.base import AsyncSessionLocal
    from app.services.assessment_service import AssessmentService

    all_ready = True
    async with AsyncSessionLocal() as db:
        svc = AssessmentService(db)
        for exam, branch in _WARM_EXAMS:
            try:
                booklet = await svc.ensure_shared_booklet(
                    exam,
                    challenge_date,
                    branch=branch,
                    fill_now=False,
                )
                plan = booklet.section_plan or {}
                if (
                    booklet.status == "ready"
                    and plan.get("generator") in ("gemini", "bank", "mixed")
                    and (booklet.questions or [])
                ):
                    await db.commit()
                    continue
                booklet_id = booklet.id
                booklet.status = "pending"
                await db.commit()
                # Run generation which will now isolate into pool_type="trial"
                await run_shared_booklet_generation(booklet_id)
                refreshed = await svc.repo.get_shared_booklet_by_id(booklet_id)
                if refreshed is None or refreshed.status != "ready":
                    all_ready = False
            except Exception:
                all_ready = False
                logger.exception(
                    "Midnight trial exam failed exam=%s branch=%s date=%s",
                    exam,
                    branch,
                    challenge_date,
                )
                await db.rollback()
    return all_ready

async def midnight_trial_exam_loop() -> None:
    """Arka planda çalışır, her gece 03:00'te deneme sınavlarını üretir."""
    logger.info("Trial exam (03:00) scheduler started.")
    while True:
        wait_sec = seconds_until_next_0300()
        logger.info("Trial exam scheduler sleeping for %.0f s (until 03:00)", wait_sec)
        await asyncio.sleep(wait_sec)
        
        challenge_date = _now_istanbul().date()
        logger.info("Woke up for 03:00 trial exam generation pass: date=%s", challenge_date)
        while True:
            try:
                done = await generate_trial_exams_for_date(challenge_date)
            except Exception:
                logger.exception("Trial exam generation pass crashed for %s", challenge_date)
                done = False
            if done:
                logger.info("Trial exams ready for %s", challenge_date)
                break
            
            remaining = seconds_until_next_0300()
            if remaining <= _RESUME_INTERVAL_SECONDS:
                break
            logger.info("Trial exams incomplete for %s — retrying in %.0f s", challenge_date, _RESUME_INTERVAL_SECONDS)
            await asyncio.sleep(_RESUME_INTERVAL_SECONDS)
