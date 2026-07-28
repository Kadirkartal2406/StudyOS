"""
StudyOS — NotificationPreference Repository
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_preference import NotificationPreference
from app.repositories.base import BaseRepository


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    def __init__(self, db: AsyncSession):
        super().__init__(NotificationPreference, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> NotificationPreference | None:
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()
