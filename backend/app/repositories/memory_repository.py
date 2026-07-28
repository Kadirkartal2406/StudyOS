"""
StudyOS — Memory Repository
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryCategory
from app.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[Memory]):
    def __init__(self, db: AsyncSession):
        super().__init__(Memory, db)

    async def get_for_user(self, memory_id: uuid.UUID, user_id: uuid.UUID) -> Memory | None:
        result = await self.db.execute(
            select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        active_only: bool = True,
        category: MemoryCategory | None = None,
        limit: int = 100,
    ) -> list[Memory]:
        stmt = select(Memory).where(Memory.user_id == user_id)
        if active_only:
            stmt = stmt.where(Memory.is_active.is_(True))
        if category is not None:
            stmt = stmt.where(Memory.category == category)
        stmt = stmt.order_by(
            Memory.importance.desc(),
            Memory.access_count.desc(),
            Memory.last_accessed_at.desc().nullslast(),
            Memory.updated_at.desc(),
        ).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self,
        user_id: uuid.UUID,
        *,
        q: str | None = None,
        category: MemoryCategory | None = None,
        limit: int = 20,
    ) -> list[Memory]:
        stmt = select(Memory).where(Memory.user_id == user_id, Memory.is_active.is_(True))
        if category is not None:
            stmt = stmt.where(Memory.category == category)
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(Memory.content.ilike(pattern), Memory.category.ilike(pattern))
            )
        stmt = stmt.order_by(
            Memory.importance.desc(),
            Memory.access_count.desc(),
            Memory.last_accessed_at.desc().nullslast(),
        ).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_similar_active(
        self, user_id: uuid.UUID, category: MemoryCategory, content: str
    ) -> Memory | None:
        """Basit dedup: aynı category + içerik ILIKE."""
        result = await self.db.execute(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.category == category,
                Memory.is_active.is_(True),
                Memory.content.ilike(content.strip()),
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def touch(self, memory: Memory) -> None:
        memory.last_accessed_at = datetime.now(UTC)
        memory.access_count = int(memory.access_count or 0) + 1
        await self.db.flush()

    async def clear_for_user(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            delete(Memory).where(Memory.user_id == user_id)
        )
        await self.db.flush()
        return int(result.rowcount or 0)

    async def count_active(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Memory)
            .where(Memory.user_id == user_id, Memory.is_active.is_(True))
        )
        return int(result.scalar_one())
