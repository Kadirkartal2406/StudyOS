"""Sprint 18 — Assessment repository."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import (
    AssessmentSession,
    AssessmentSessionStatus,
    DailyChallenge,
    EstimatedScoreSnapshot,
    SharedDailyBooklet,
)
from app.repositories.base import BaseRepository


class AssessmentRepository(BaseRepository[AssessmentSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(AssessmentSession, db)

    async def get_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> AssessmentSession | None:
        result = await self.db.execute(
            select(AssessmentSession)
            .options(selectinload(AssessmentSession.questions))
            .where(
                AssessmentSession.id == session_id,
                AssessmentSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_submitted_for_exam(
        self, user_id: uuid.UUID, exam_type: str, *, kind: str | None = None
    ) -> list[AssessmentSession]:
        stmt = select(AssessmentSession).where(
            AssessmentSession.user_id == user_id,
            AssessmentSession.exam_type == exam_type,
            AssessmentSession.status == AssessmentSessionStatus.SUBMITTED,
        )
        if kind:
            stmt = stmt.where(AssessmentSession.kind == kind)
        stmt = stmt.order_by(AssessmentSession.submitted_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_calibration(
        self, user_id: uuid.UUID, exam_type: str, subject_code: str
    ) -> AssessmentSession | None:
        result = await self.db.execute(
            select(AssessmentSession)
            .where(
                AssessmentSession.user_id == user_id,
                AssessmentSession.exam_type == exam_type,
                AssessmentSession.kind == "initial_calibration",
                AssessmentSession.subject_code == subject_code,
                AssessmentSession.status == AssessmentSessionStatus.SUBMITTED,
            )
            .order_by(AssessmentSession.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def find_branch_today(
        self,
        user_id: uuid.UUID,
        exam_type: str,
        subject_code: str,
        challenge_date: date,
    ) -> AssessmentSession | None:
        result = await self.db.execute(
            select(AssessmentSession)
            .options(selectinload(AssessmentSession.questions))
            .where(
                AssessmentSession.user_id == user_id,
                AssessmentSession.exam_type == exam_type,
                AssessmentSession.kind == "branch_question",
                AssessmentSession.subject_code == subject_code,
                AssessmentSession.challenge_date == challenge_date,
            )
            .order_by(AssessmentSession.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_daily_challenge(
        self,
        user_id: uuid.UUID,
        exam_type: str,
        challenge_date: date,
        subject_code: str | None = None,
    ) -> DailyChallenge | None:
        stmt = select(DailyChallenge).where(
            DailyChallenge.user_id == user_id,
            DailyChallenge.exam_type == exam_type,
            DailyChallenge.challenge_date == challenge_date,
        )
        if subject_code:
            stmt = stmt.where(DailyChallenge.subject_code == subject_code)
        else:
            # Prefer booklet row (Sprint 23)
            stmt = stmt.order_by(
                (DailyChallenge.subject_code == "booklet").desc(),
                DailyChallenge.created_at.desc(),
            )
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def list_daily_challenges(
        self, user_id: uuid.UUID, exam_type: str, challenge_date: date
    ) -> list[DailyChallenge]:
        result = await self.db.execute(
            select(DailyChallenge).where(
                DailyChallenge.user_id == user_id,
                DailyChallenge.exam_type == exam_type,
                DailyChallenge.challenge_date == challenge_date,
            )
        )
        return list(result.scalars().all())

    async def get_shared_booklet(
        self,
        exam_type: str,
        challenge_date: date,
        *,
        branch_key: str = "",
    ) -> SharedDailyBooklet | None:
        result = await self.db.execute(
            select(SharedDailyBooklet)
            .options(selectinload(SharedDailyBooklet.questions))
            .where(
                SharedDailyBooklet.exam_type == exam_type,
                SharedDailyBooklet.branch_key == (branch_key or ""),
                SharedDailyBooklet.challenge_date == challenge_date,
            )
        )
        return result.scalar_one_or_none()

    async def get_shared_booklet_by_id(
        self, booklet_id: uuid.UUID
    ) -> SharedDailyBooklet | None:
        result = await self.db.execute(
            select(SharedDailyBooklet)
            .options(selectinload(SharedDailyBooklet.questions))
            .where(SharedDailyBooklet.id == booklet_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def list_peer_accuracies(
        self, exam_type: str, *, exclude_user: uuid.UUID | None = None
    ) -> list[float]:
        stmt = select(AssessmentSession.accuracy).where(
            AssessmentSession.exam_type == exam_type,
            AssessmentSession.status == AssessmentSessionStatus.SUBMITTED,
            AssessmentSession.accuracy.is_not(None),
        )
        if exclude_user:
            stmt = stmt.where(AssessmentSession.user_id != exclude_user)
        result = await self.db.execute(stmt)
        return [float(a) for (a,) in result.all() if a is not None]

    async def latest_score_snapshot(
        self, user_id: uuid.UUID, exam_type: str
    ) -> EstimatedScoreSnapshot | None:
        result = await self.db.execute(
            select(EstimatedScoreSnapshot)
            .where(
                EstimatedScoreSnapshot.user_id == user_id,
                EstimatedScoreSnapshot.exam_type == exam_type,
            )
            .order_by(EstimatedScoreSnapshot.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
