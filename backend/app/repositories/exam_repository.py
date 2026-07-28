"""
StudyOS — Exam Repository
Sprint-2.6
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exam import Exam, ExamResult
from app.repositories.base import BaseRepository


class ExamRepository(BaseRepository[Exam]):
    def __init__(self, db: AsyncSession):
        super().__init__(Exam, db)

    async def get_for_user(
        self, exam_id: uuid.UUID, user_id: uuid.UUID, *, with_results: bool = True
    ) -> Exam | None:
        stmt = select(Exam).where(Exam.id == exam_id, Exam.user_id == user_id)
        if with_results:
            stmt = stmt.options(selectinload(Exam.results))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        exam_type: str | None = None,
        limit: int = 100,
    ) -> list[Exam]:
        stmt = (
            select(Exam)
            .where(Exam.user_id == user_id)
            .options(selectinload(Exam.results))
            .order_by(Exam.exam_date.desc(), Exam.created_at.desc())
            .limit(limit)
        )
        if exam_type is not None:
            stmt = stmt.where(Exam.exam_type == exam_type)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_for_user(self, user_id: uuid.UUID) -> int:
        from sqlalchemy import func

        result = await self.db.execute(
            select(func.count()).select_from(Exam).where(Exam.user_id == user_id)
        )
        return int(result.scalar_one())

    async def list_between(
        self, user_id: uuid.UUID, start: date, end: date
    ) -> list[Exam]:
        stmt = (
            select(Exam)
            .where(
                Exam.user_id == user_id,
                Exam.exam_date >= start,
                Exam.exam_date <= end,
            )
            .options(selectinload(Exam.results))
            .order_by(Exam.exam_date.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def delete_results(self, exam_id: uuid.UUID) -> None:
        rows = await self.db.execute(select(ExamResult).where(ExamResult.exam_id == exam_id))
        for row in rows.scalars().all():
            await self.db.delete(row)
        await self.db.flush()
