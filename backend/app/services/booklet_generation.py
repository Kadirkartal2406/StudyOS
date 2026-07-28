"""Background generation for shared daily booklets."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.database.base import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Warm these exams at startup / nightly — sadece temel set (hızlı)
_WARM_EXAMS: tuple[tuple[str, str | None], ...] = (
    ("kpss", None),
    ("tyt", None),
    ("lgs", None),
)


async def run_booklet_generation(session_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Legacy: fill a pending user booklet via shared pack clone."""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload

            from app.models.assessment import AssessmentSession, AssessmentSessionStatus
            from app.services.assessment_service import AssessmentService

            svc = AssessmentService(db)
            result = await db.execute(
                select(AssessmentSession)
                .options(selectinload(AssessmentSession.questions))
                .where(
                    AssessmentSession.id == session_id,
                    AssessmentSession.user_id == user_id,
                )
            )
            session = result.scalar_one_or_none()
            if session is None:
                return
            if session.status == AssessmentSessionStatus.READY and session.questions:
                return
            if session.status == AssessmentSessionStatus.SUBMITTED:
                return
            await svc.fill_booklet_session(session, synthetic=None)
            await db.commit()
        except Exception:
            logger.exception("Booklet generation failed for %s", session_id)
            await db.rollback()


async def run_shared_booklet_generation(booklet_id: uuid.UUID) -> None:
    """Gemini-only fill. Bank/sentetik yok."""
    async with AsyncSessionLocal() as db:
        try:
            from app.services.assessment_service import AssessmentService

            svc = AssessmentService(db)
            booklet = await svc.repo.get_shared_booklet_by_id(booklet_id)
            if booklet is None:
                return
            await svc.fill_shared_booklet(booklet, synthetic=False)
            await db.commit()
        except Exception:
            logger.exception("Shared booklet generation failed for %s", booklet_id)
            await db.rollback()


async def warm_todays_shared_booklets() -> None:
    """Deprecated path — midnight_booklet_loop kullan."""
    from app.services.booklet_scheduler import generate_booklets_for_date

    today = datetime.now(UTC).date()
    await generate_booklets_for_date(today)
