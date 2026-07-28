"""
StudyOS — Goal Repository
"""

import uuid
from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal, GoalPeriod, GoalStatus
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Goal, db)

    async def get_by_id_for_user(
        self, goal_id: uuid.UUID, user_id: uuid.UUID
    ) -> Goal | None:
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        )
        return result.scalar_one_or_none()

    def _base_query(self, user_id: uuid.UUID) -> Select[tuple[Goal]]:
        return select(Goal).where(Goal.user_id == user_id)

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        status: GoalStatus | None = None,
        period: GoalPeriod | None = None,
        active_on: date | None = None,
        exam_type: str | None = None,
    ) -> list[Goal]:
        stmt = self._base_query(user_id)
        if status is not None:
            stmt = stmt.where(Goal.status == status)
        if period is not None:
            stmt = stmt.where(Goal.period == period)
        if active_on is not None:
            stmt = stmt.where(Goal.start_date <= active_on, Goal.end_date >= active_on)
        if exam_type is not None:
            stmt = stmt.where(Goal.exam_type == exam_type)
        stmt = stmt.order_by(Goal.priority.asc(), Goal.end_date.asc(), Goal.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_active(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        return await self.list_for_user(
            user_id, status=GoalStatus.ACTIVE, exam_type=exam_type
        )

    async def list_completed(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        stmt = (
            self._base_query(user_id)
            .where(Goal.status == GoalStatus.COMPLETED)
            .order_by(Goal.completed_at.desc().nullslast(), Goal.updated_at.desc())
        )
        if exam_type is not None:
            stmt = stmt.where(Goal.exam_type == exam_type)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_period(
        self,
        user_id: uuid.UUID,
        period: GoalPeriod,
        *,
        exam_type: str | None = None,
    ) -> list[Goal]:
        return await self.list_for_user(
            user_id, period=period, exam_type=exam_type
        )

    async def count_by_status(
        self,
        user_id: uuid.UUID,
        status: GoalStatus,
        *,
        exam_type: str | None = None,
    ) -> int:
        filters = [Goal.user_id == user_id, Goal.status == status]
        if exam_type is not None:
            filters.append(Goal.exam_type == exam_type)
        result = await self.db.execute(
            select(func.count()).select_from(Goal).where(*filters)
        )
        return int(result.scalar_one())
