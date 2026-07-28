"""
StudyOS — StudyResource Repository
"""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_resource import ResourceStatus, ResourceType, StudyResource
from app.repositories.base import BaseRepository


class StudyResourceRepository(BaseRepository[StudyResource]):
    def __init__(self, db: AsyncSession):
        super().__init__(StudyResource, db)

    async def get_for_user(
        self, resource_id: uuid.UUID, user_id: uuid.UUID
    ) -> StudyResource | None:
        result = await self.db.execute(
            select(StudyResource).where(
                StudyResource.id == resource_id, StudyResource.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        study_plan_id: uuid.UUID | None = None,
        subject_code: str | None = None,
        topic_code: str | None = None,
        status: ResourceStatus | None = None,
        resource_type: ResourceType | None = None,
        limit: int = 100,
    ) -> list[StudyResource]:
        stmt = select(StudyResource).where(StudyResource.user_id == user_id)
        if study_plan_id is not None:
            stmt = stmt.where(StudyResource.study_plan_id == study_plan_id)
        if subject_code is not None:
            stmt = stmt.where(StudyResource.subject_code == subject_code)
        if topic_code is not None:
            stmt = stmt.where(StudyResource.topic_code == topic_code)
        if status is not None:
            stmt = stmt.where(StudyResource.status == status)
        if resource_type is not None:
            stmt = stmt.where(StudyResource.resource_type == resource_type)
        stmt = stmt.order_by(
            StudyResource.order_index.asc(),
            StudyResource.created_at.desc(),
        ).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def max_order_index(
        self, user_id: uuid.UUID, study_plan_id: uuid.UUID | None
    ) -> int:
        stmt = select(func.coalesce(func.max(StudyResource.order_index), -1)).where(
            StudyResource.user_id == user_id
        )
        if study_plan_id is not None:
            stmt = stmt.where(StudyResource.study_plan_id == study_plan_id)
        else:
            stmt = stmt.where(StudyResource.study_plan_id.is_(None))
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def count_opened_on(self, user_id: uuid.UUID, day: date) -> int:
        start = datetime(day.year, day.month, day.day, tzinfo=UTC)
        end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=UTC)
        result = await self.db.execute(
            select(func.count())
            .select_from(StudyResource)
            .where(
                StudyResource.user_id == user_id,
                StudyResource.last_opened_at.is_not(None),
                StudyResource.last_opened_at >= start,
                StudyResource.last_opened_at <= end,
            )
        )
        return int(result.scalar_one())

    async def count_completed_on(self, user_id: uuid.UUID, day: date) -> int:
        start = datetime(day.year, day.month, day.day, tzinfo=UTC)
        end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=UTC)
        result = await self.db.execute(
            select(func.count())
            .select_from(StudyResource)
            .where(
                StudyResource.user_id == user_id,
                StudyResource.status == ResourceStatus.COMPLETED,
                StudyResource.completed_at.is_not(None),
                StudyResource.completed_at >= start,
                StudyResource.completed_at <= end,
            )
        )
        return int(result.scalar_one())

    async def list_recent(self, user_id: uuid.UUID, *, limit: int = 5) -> list[StudyResource]:
        result = await self.db.execute(
            select(StudyResource)
            .where(StudyResource.user_id == user_id)
            .order_by(StudyResource.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def find_duplicate_url(
        self,
        user_id: uuid.UUID,
        url: str,
        *,
        topic_code: str | None = None,
        subject_code: str | None = None,
    ) -> StudyResource | None:
        """Same URL on same topic (or subject-only if topic null) = duplicate."""
        stmt = select(StudyResource).where(
            StudyResource.user_id == user_id,
            StudyResource.url == url,
        )
        if topic_code is not None:
            stmt = stmt.where(StudyResource.topic_code == topic_code)
        elif subject_code is not None:
            stmt = stmt.where(
                StudyResource.subject_code == subject_code,
                StudyResource.topic_code.is_(None),
            )
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none()
