"""Daily shared booklet scheduler — her gece 00:00 (Europe/Istanbul) Gemini üretimi."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.services.booklet_generation import (
    _WARM_EXAMS,
    run_shared_booklet_generation,
)

logger = logging.getLogger("studyos.booklet_scheduler")

# Türkiye 2016'dan beri kalıcı UTC+3 (tzdata paketi gerekmez)
_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")

# Kota / geçici hata sonrası kaldığı yerden devam denemesi aralığı
_RESUME_INTERVAL_SECONDS = 1800.0


def _now_istanbul() -> datetime:
    return datetime.now(_TZ)


def seconds_until_next_midnight() -> float:
    now = _now_istanbul()
    nxt = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(1.0, (nxt - now).total_seconds())


async def generate_booklets_for_date(challenge_date) -> bool:
    """Belirli gün için tüm sınav pack'lerini Gemini ile üret (sadece AI).

    Dönüş: tüm pack'ler hazır mı.
    """
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
                    # Hazır pack'i bozma — kota riskinde Gemini yükseltmesi
                    # yarım kalırsa kullanıcıya boş gün kalır.
                    await db.commit()
                    continue
                booklet_id = booklet.id
                booklet.status = "pending"
                await db.commit()
                await run_shared_booklet_generation(booklet_id)
                refreshed = await svc.repo.get_shared_booklet_by_id(booklet_id)
                if refreshed is None or refreshed.status != "ready":
                    all_ready = False
            except Exception:
                all_ready = False
                logger.exception(
                    "Midnight/catch-up booklet failed exam=%s branch=%s date=%s",
                    exam,
                    branch,
                    challenge_date,
                )
                await db.rollback()
    return all_ready


async def generate_until_complete(challenge_date) -> None:
    """Kota/geçici hata durumunda gün içinde kaldığı yerden devam eder."""
    while True:
        try:
            done = await generate_booklets_for_date(challenge_date)
        except Exception:
            logger.exception("Booklet generation pass crashed for %s", challenge_date)
            done = False
        if done:
            logger.info("Booklet packs ready for %s", challenge_date)
            return
        remaining = seconds_until_next_midnight()
        if remaining <= _RESUME_INTERVAL_SECONDS:
            # Gün bitiyor — yeni günün job'ı devralır
            return
        logger.info(
            "Booklet packs incomplete for %s — retrying in %.0f s",
            challenge_date,
            _RESUME_INTERVAL_SECONDS,
        )
        await asyncio.sleep(_RESUME_INTERVAL_SECONDS)


async def midnight_booklet_loop() -> None:
    """Sürekli: her gece 00:00'da o günün Gemini pack'lerini üret."""
    from app.services.ai_cost.flags import (
        auto_booklet_enabled,
        catchup_enabled,
        midnight_scheduler_enabled,
    )

    if not midnight_scheduler_enabled() or not auto_booklet_enabled():
        logger.info(
            "M32 booklet scheduler idle (ENABLE_MIDNIGHT_SCHEDULER/AUTO_BOOKLET off)"
        )
        return

    try:
        today = _now_istanbul().date()
        if catchup_enabled():
            logger.info("Booklet catch-up for %s starting", today)
            await generate_until_complete(today)
        else:
            logger.info("M32: ENABLE_CATCHUP=false — startup catch-up skipped")
    except Exception:
        logger.exception("Booklet catch-up failed")

    while True:
        wait_s = seconds_until_next_midnight()
        logger.info(
            "Next booklet generation in %.0f seconds (Istanbul midnight)", wait_s
        )
        await asyncio.sleep(wait_s)
        if not midnight_scheduler_enabled() or not auto_booklet_enabled():
            logger.info("M32 booklet scheduler disabled mid-loop — exiting")
            return
        try:
            day = _now_istanbul().date()
            logger.info("Midnight booklet generation for %s", day)
            await generate_until_complete(day)
        except Exception:
            logger.exception("Midnight booklet generation crashed")
        await asyncio.sleep(2)
