"""
StudyOS — QuestionRecord Repository
"""

import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_record import ExamType, QuestionRecord, QuestionSource
from app.repositories.base import BaseRepository


class QuestionRecordRepository(BaseRepository[QuestionRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(QuestionRecord, db)

    async def get_by_id_for_user(
        self, record_id: uuid.UUID, user_id: uuid.UUID
    ) -> QuestionRecord | None:
        result = await self.db.execute(
            select(QuestionRecord).where(
                QuestionRecord.id == record_id,
                QuestionRecord.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        user_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
        date_from: date | None = None,
        date_to: date | None = None,
        subject: str | None = None,
        topic: str | None = None,
        exam_type: ExamType | None = None,
        source: QuestionSource | None = None,
        study_plan_id: uuid.UUID | None = None,
        study_session_id: uuid.UUID | None = None,
    ) -> tuple[list[QuestionRecord], int]:
        filters = [QuestionRecord.user_id == user_id]
        if date_from is not None:
            filters.append(func.date(QuestionRecord.created_at) >= date_from)
        if date_to is not None:
            filters.append(func.date(QuestionRecord.created_at) <= date_to)
        if subject:
            filters.append(QuestionRecord.subject.ilike(subject))
        if topic:
            filters.append(QuestionRecord.topic.ilike(f"%{topic}%"))
        if exam_type is not None:
            filters.append(QuestionRecord.exam_type == exam_type)
        if source is not None:
            filters.append(QuestionRecord.source == source)
        if study_plan_id is not None:
            filters.append(QuestionRecord.study_plan_id == study_plan_id)
        if study_session_id is not None:
            filters.append(QuestionRecord.study_session_id == study_session_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(QuestionRecord).where(*filters)
        )
        total = int(count_result.scalar_one())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(QuestionRecord)
            .where(*filters)
            .order_by(QuestionRecord.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def aggregate_between(
        self,
        user_id: uuid.UUID,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> tuple[int, int, int, int, float, int, int]:
        """(questions, correct, wrong, blank, net, duration, record_count)."""
        filters = [QuestionRecord.user_id == user_id]
        if created_from is not None:
            filters.append(QuestionRecord.created_at >= created_from)
        if created_to is not None:
            filters.append(QuestionRecord.created_at < created_to)

        result = await self.db.execute(
            select(
                func.coalesce(func.sum(QuestionRecord.question_count), 0),
                func.coalesce(func.sum(QuestionRecord.correct_count), 0),
                func.coalesce(func.sum(QuestionRecord.wrong_count), 0),
                func.coalesce(func.sum(QuestionRecord.blank_count), 0),
                func.coalesce(func.sum(QuestionRecord.net_score), 0),
                func.coalesce(func.sum(QuestionRecord.duration_minutes), 0),
                func.count(QuestionRecord.id),
            ).where(*filters)
        )
        row = result.one()
        return (
            int(row[0]),
            int(row[1]),
            int(row[2]),
            int(row[3]),
            float(row[4]),
            int(row[5]),
            int(row[6]),
        )

    async def daily_buckets(
        self,
        user_id: uuid.UUID,
        created_from: datetime,
        created_to: datetime,
    ) -> list[tuple]:
        day_col = func.date(QuestionRecord.created_at)
        result = await self.db.execute(
            select(
                day_col,
                func.coalesce(func.sum(QuestionRecord.question_count), 0),
                func.coalesce(func.sum(QuestionRecord.correct_count), 0),
                func.coalesce(func.sum(QuestionRecord.wrong_count), 0),
                func.coalesce(func.sum(QuestionRecord.blank_count), 0),
                func.coalesce(func.sum(QuestionRecord.net_score), 0),
                func.coalesce(func.sum(QuestionRecord.duration_minutes), 0),
            )
            .where(
                QuestionRecord.user_id == user_id,
                QuestionRecord.created_at >= created_from,
                QuestionRecord.created_at < created_to,
            )
            .group_by(day_col)
            .order_by(day_col.asc())
        )
        return list(result.all())

    async def group_by_subject(
        self,
        user_id: uuid.UUID,
        *,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int = 20,
    ) -> list[tuple]:
        return await self._group_by_field(
            user_id,
            QuestionRecord.subject,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
        )

    async def group_by_topic(
        self,
        user_id: uuid.UUID,
        *,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int = 20,
    ) -> list[tuple]:
        topic_label = func.coalesce(QuestionRecord.topic, "Genel")
        return await self._group_by_field(
            user_id,
            topic_label,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
        )

    async def group_by_exam(
        self,
        user_id: uuid.UUID,
        *,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int = 20,
    ) -> list[tuple]:
        exam_label = func.coalesce(QuestionRecord.exam_type, "custom")
        return await self._group_by_field(
            user_id,
            exam_label,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
        )

    async def _group_by_field(
        self,
        user_id: uuid.UUID,
        field,
        *,
        created_from: datetime | None,
        created_to: datetime | None,
        limit: int,
    ) -> list[tuple]:
        filters = [QuestionRecord.user_id == user_id]
        if created_from is not None:
            filters.append(QuestionRecord.created_at >= created_from)
        if created_to is not None:
            filters.append(QuestionRecord.created_at < created_to)

        result = await self.db.execute(
            select(
                field,
                func.coalesce(func.sum(QuestionRecord.question_count), 0),
                func.coalesce(func.sum(QuestionRecord.correct_count), 0),
                func.coalesce(func.sum(QuestionRecord.wrong_count), 0),
                func.coalesce(func.sum(QuestionRecord.blank_count), 0),
                func.coalesce(func.sum(QuestionRecord.net_score), 0),
                func.coalesce(func.sum(QuestionRecord.duration_minutes), 0),
            )
            .where(*filters)
            .group_by(field)
            .order_by(func.sum(QuestionRecord.question_count).desc())
            .limit(limit)
        )
        return list(result.all())
