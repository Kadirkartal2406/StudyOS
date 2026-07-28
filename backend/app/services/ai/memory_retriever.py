"""
StudyOS — MemoryRetriever
Sprint-2.3: Kural tabanlı sıralama + touch (embedding yok).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AI_CONTEXT_MEMORIES
from app.models.memory import Memory
from app.repositories.memory_repository import MemoryRepository


class MemoryRetriever:
    def __init__(self, db: AsyncSession):
        self.repo = MemoryRepository(db)

    async def retrieve_for_context(
        self, user_id: uuid.UUID, *, limit: int | None = None
    ) -> list[Memory]:
        cap = limit or AI_CONTEXT_MEMORIES
        items = await self.repo.list_for_user(user_id, active_only=True, limit=cap)
        for mem in items:
            await self.repo.touch(mem)
        return items

    async def to_context_items(self, user_id: uuid.UUID) -> list[dict[str, Any]]:
        items = await self.retrieve_for_context(user_id)
        return [
            {
                "id": str(m.id),
                "category": str(m.category),
                "importance": float(m.importance),
                "content": m.content,
                "source": str(m.source),
            }
            for m in items
        ]
