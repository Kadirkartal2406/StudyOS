"""
StudyOS — Temel Repository
Tüm repository sınıflarının türediği generic CRUD taban sınıfı.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base


class BaseRepository[ModelType: Base]:
    """Generic CRUD işlemleri sağlayan taban repository sınıfı."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelType | None:
        # Projedeki tüm modeller UUID `id` alanına sahiptir (database-design.md),
        # ancak Base sınıfı bunu garanti etmez; mypy bu yüzden uyarı verir.
        result = await self.db.execute(
            select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def delete(self, entity: ModelType) -> None:
        await self.db.delete(entity)
        await self.db.flush()
