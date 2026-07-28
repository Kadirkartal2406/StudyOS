"""
StudyOS — Achievement Repository
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.achievement import Achievement, AchievementProgress, UserAchievement
from app.repositories.base import BaseRepository


class AchievementRepository(BaseRepository[Achievement]):
    def __init__(self, db: AsyncSession):
        super().__init__(Achievement, db)

    async def list_active(self) -> list[Achievement]:
        result = await self.db.execute(
            select(Achievement)
            .where(Achievement.is_active.is_(True))
            .order_by(Achievement.sort_order.asc(), Achievement.code.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, achievement_id: uuid.UUID) -> Achievement | None:
        result = await self.db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Achievement | None:
        result = await self.db.execute(select(Achievement).where(Achievement.code == code))
        return result.scalar_one_or_none()

    async def list_unlocked(self, user_id: uuid.UUID) -> list[UserAchievement]:
        result = await self.db.execute(
            select(UserAchievement)
            .options(selectinload(UserAchievement.achievement))
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        return list(result.scalars().all())

    async def get_unlock(
        self, user_id: uuid.UUID, achievement_id: uuid.UUID
    ) -> UserAchievement | None:
        result = await self.db.execute(
            select(UserAchievement)
            .options(selectinload(UserAchievement.achievement))
            .where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
        )
        return result.scalar_one_or_none()

    async def unlocked_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        result = await self.db.execute(
            select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
        )
        return set(result.scalars().all())

    async def add_unlock(self, row: UserAchievement) -> UserAchievement:
        self.db.add(row)
        await self.db.flush()
        return row

    async def upsert_progress(
        self,
        user_id: uuid.UUID,
        achievement_id: uuid.UUID,
        current: float,
        target: float,
    ) -> AchievementProgress:
        result = await self.db.execute(
            select(AchievementProgress).where(
                AchievementProgress.user_id == user_id,
                AchievementProgress.achievement_id == achievement_id,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = AchievementProgress(
                user_id=user_id,
                achievement_id=achievement_id,
                current_value=current,
                target_value=target,
            )
            self.db.add(row)
        else:
            row.current_value = current
            row.target_value = target
        await self.db.flush()
        return row

    async def list_progress(self, user_id: uuid.UUID) -> list[AchievementProgress]:
        result = await self.db.execute(
            select(AchievementProgress)
            .options(selectinload(AchievementProgress.achievement))
            .where(AchievementProgress.user_id == user_id)
        )
        return list(result.scalars().all())
