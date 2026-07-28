"""
StudyOS — Activity Repository
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, db: AsyncSession):
        super().__init__(Activity, db)

    async def list_recent_for_user(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        event_types: list[str] | None = None,
    ) -> list[Activity]:
        filters = [Activity.user_id == user_id]
        if event_types:
            filters.append(Activity.event_type.in_(event_types))

        result = await self.db.execute(
            select(Activity)
            .where(*filters)
            .order_by(Activity.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_activity(
        self,
        *,
        user_id: uuid.UUID,
        event_type: str,
        title: str,
        description: str | None = None,
        study_session_id: uuid.UUID | None = None,
        study_plan_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
        occurred_at: Any = None,
    ) -> Activity:
        from datetime import UTC, datetime

        activity = Activity(
            user_id=user_id,
            event_type=event_type,
            title=title,
            description=description,
            study_session_id=study_session_id,
            study_plan_id=study_plan_id,
            metadata_=metadata,
            occurred_at=occurred_at or datetime.now(UTC),
        )
        return await self.add(activity)
