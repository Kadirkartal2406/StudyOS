"""Weekly trial exam (deneme) scheduler — staggered Mon–Sat, ready Monday.

Packs are keyed by the week's Monday as SharedDailyBooklet.challenge_date.
Production builds the *next* Monday's packs during the prior week:
- Mon–Sat 03:00: up to AI_NIGHTLY_DENEME_PACKS packs (default 4)
- Sun 03:00: gap-fill remaining packs for next Monday
- Mon 03:00: gap-fill current week if needed, then start next week's batch 1

Users see packs for current_serve_monday() only.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date

from app.core.config import settings
from app.core.week_calendar import (
    current_serve_monday,
    now_istanbul,
    production_target_monday,
)
from app.services.booklet_generation import run_shared_booklet_generation

_ALL_EXAMS: tuple[tuple[str, str | None], ...] = (
    # High-priority: YKS users get TYT + AYT
    ("tyt", None),
    ("ayt", "sayisal"),
    ("ayt", "ea"),
    ("ayt", "sozel"),
    ("lgs", "sayisal"),
    ("lgs", "sozel"),
    ("kpss", "lisans"),
    ("kpss", "onlisans"),
    ("kpss", "ortaogretim"),
    ("ydt", "en"),
    ("ags", None),
    ("ales", "sayisal"),
    ("ales", "sozel"),
    ("dgs", "sayisal"),
    ("dgs", "sozel"),
    ("yds", "en"),
    ("yokdil", "fen"),
    ("yokdil", "saglik"),
    ("yokdil", "sosyal"),
)

logger = logging.getLogger("studyos.trial_exam_scheduler")

_RESUME_INTERVAL_SECONDS = 1800.0


def _now_istanbul():
    return now_istanbul()


def seconds_until_next_0300() -> float:
    from datetime import timedelta

    now = now_istanbul()
    nxt = now.replace(hour=3, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return max(1.0, (nxt - now).total_seconds())


def nightly_deneme_pack_limit() -> int:
    return max(1, int(getattr(settings, "AI_NIGHTLY_DENEME_PACKS", 4) or 4))


def _nightly_batch_sizes() -> list[int]:
    """Distribute all packs across Mon–Sat (6 nights)."""
    n = len(_ALL_EXAMS)
    nights = 6
    base, rem = divmod(n, nights)
    return [base + (1 if i < rem else 0) for i in range(nights)]


def packs_per_batch() -> int:
    return max(_nightly_batch_sizes())


def batch_slice_for_weekday(weekday: int) -> list[tuple[str, str | None]]:
    """weekday Mon=0 … Sat=5. Sunday returns full list (gap-fill)."""
    if weekday == 6:
        return list(_ALL_EXAMS)
    if weekday < 0 or weekday > 5:
        return []
    sizes = _nightly_batch_sizes()
    start = sum(sizes[:weekday])
    end = start + sizes[weekday]
    return list(_ALL_EXAMS[start:end])


async def _pack_ready(svc, exam: str, challenge_date: date, branch: str | None) -> bool:
    booklet = await svc.ensure_shared_booklet(
        exam, challenge_date, branch=branch, fill_now=False
    )
    plan = booklet.section_plan or {}
    return (
        booklet.status == "ready"
        and plan.get("generator") in ("gemini", "bank", "mixed")
        and bool(booklet.questions or [])
    )


async def generate_trial_exams_for_date(
    challenge_date: date,
    target_exam: str | None = None,
    *,
    limit: int | None = None,
    only_missing: bool = True,
) -> bool:
    """Generate deneme packs for a week Monday date.

    Returns True when all targeted packs are ready.
    """
    from app.database.base import AsyncSessionLocal
    from app.services.assessment_service import AssessmentService

    target_exams = [
        e for e in _ALL_EXAMS if target_exam is None or e[0] == target_exam.lower()
    ]
    if limit is not None:
        # Prefer missing first when limiting
        pass

    all_ready = True
    attempted = 0
    async with AsyncSessionLocal() as db:
        svc = AssessmentService(db)
        pending_list: list[tuple[str, str | None]] = []
        for exam, branch in target_exams:
            try:
                ready = await _pack_ready(svc, exam, challenge_date, branch)
                await db.commit()
                if ready:
                    continue
                pending_list.append((exam, branch))
            except Exception:
                await db.rollback()
                pending_list.append((exam, branch))

        if only_missing and limit is not None:
            pending_list = pending_list[:limit]
        elif limit is not None and not only_missing:
            pending_list = target_exams[:limit]

        for i, (exam, branch) in enumerate(pending_list):
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
                await run_shared_booklet_generation(booklet_id)
                attempted += 1
                refreshed = await svc.repo.get_shared_booklet_by_id(booklet_id)
                if refreshed is None or refreshed.status != "ready":
                    all_ready = False
                if i < len(pending_list) - 1:
                    await asyncio.sleep(5.0)
            except Exception:
                all_ready = False
                logger.exception(
                    "Weekly trial exam failed exam=%s branch=%s week_monday=%s",
                    exam,
                    branch,
                    challenge_date,
                )
                await db.rollback()

        # If we only ran a batch, overall week may still be incomplete
        if limit is not None:
            remaining = 0
            for exam, branch in target_exams:
                try:
                    if not await _pack_ready(svc, exam, challenge_date, branch):
                        remaining += 1
                    await db.commit()
                except Exception:
                    await db.rollback()
                    remaining += 1
            all_ready = remaining == 0

    logger.info(
        "Weekly deneme pass week_monday=%s attempted=%s all_ready=%s",
        challenge_date,
        attempted,
        all_ready,
    )
    return all_ready


async def run_weekly_deneme_nightly_pass() -> dict:
    """Single 03:00 pass — stagger assemble / gap-fill / ensure current week."""
    now = now_istanbul()
    wd = now.weekday()
    limit = nightly_deneme_pack_limit()

    if wd == 0:
        # Monday: ensure *current* week ready, then batch 1 for next week
        current = current_serve_monday(now)
        logger.info("Weekly deneme Monday — ensure current week %s", current)
        cur_ok = await generate_trial_exams_for_date(current, limit=None)
        nxt = production_target_monday(now)
        logger.info("Weekly deneme Monday — batch 1 for %s limit=%s", nxt, limit)
        nxt_ok = await generate_trial_exams_for_date(nxt, limit=limit)
        return {
            "phase": "monday_ensure_and_batch1",
            "current_week_monday": str(current),
            "current_ready": cur_ok,
            "next_week_monday": str(nxt),
            "next_batch_done": nxt_ok,
        }

    if wd == 6:
        nxt = production_target_monday(now)
        logger.info("Weekly deneme Sunday — gap-fill for %s", nxt)
        ok = await generate_trial_exams_for_date(nxt, limit=None)
        return {
            "phase": "sunday_gap_fill",
            "week_monday": str(nxt),
            "all_ready": ok,
        }

    # Tue–Sat: produce batch for next Monday
    nxt = production_target_monday(now)
    slice_packs = batch_slice_for_weekday(wd)
    # Cap by nightly limit but prefer this day's slice order
    batch = slice_packs[:limit] if slice_packs else list(_ALL_EXAMS)[:limit]
    logger.info(
        "Weekly deneme nightly assemble week=%s weekday=%s packs=%s",
        nxt,
        wd,
        [(e, b) for e, b in batch],
    )
    # Generate only these exams (filter by iterating generate with target missing)
    from app.database.base import AsyncSessionLocal
    from app.services.assessment_service import AssessmentService

    all_ready = True
    async with AsyncSessionLocal() as db:
        svc = AssessmentService(db)
        for i, (exam, branch) in enumerate(batch):
            try:
                booklet = await svc.ensure_shared_booklet(
                    exam, nxt, branch=branch, fill_now=False
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
                await run_shared_booklet_generation(booklet_id)
                refreshed = await svc.repo.get_shared_booklet_by_id(booklet_id)
                if refreshed is None or refreshed.status != "ready":
                    all_ready = False
                if i < len(batch) - 1:
                    await asyncio.sleep(5.0)
            except Exception:
                all_ready = False
                logger.exception(
                    "Weekly deneme batch failed exam=%s branch=%s week=%s",
                    exam,
                    branch,
                    nxt,
                )
                await db.rollback()

    return {
        "phase": "nightly_batch",
        "week_monday": str(nxt),
        "weekday": wd,
        "packs": [{"exam": e, "branch": b} for e, b in batch],
        "batch_ready": all_ready,
    }


async def midnight_trial_exam_loop() -> None:
    """Weekly deneme production loop — Istanbul 03:00."""
    logger.info(
        "Weekly trial exam scheduler started (stagger %s packs/night, Monday serve)",
        nightly_deneme_pack_limit(),
    )
    while True:
        wait_sec = seconds_until_next_0300()
        logger.info("Weekly deneme sleeping %.0f s (until 03:00)", wait_sec)
        await asyncio.sleep(wait_sec)
        try:
            summary = await run_weekly_deneme_nightly_pass()
            logger.info("Weekly deneme nightly pass done %s", summary)
        except Exception:
            logger.exception("Weekly deneme nightly pass crashed")
