"""
StudyOS — Memory Service
Sprint-2.3 (Meeting-021) — CRUD, search, privacy (export/clear/settings).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.memory import Memory, MemorySource
from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory import (
    MemoryCreate,
    MemoryExportResponse,
    MemoryListResponse,
    MemoryRead,
    MemorySearchRequest,
    MemorySettingsRead,
    MemorySettingsUpdate,
    MemoryUpdate,
)
from app.services.notification_settings_service import NotificationSettingsService


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MemoryRepository(db)
        self.notif = NotificationSettingsService(db)

    def _to_read(self, mem: Memory) -> MemoryRead:
        return MemoryRead(
            id=mem.id,
            user_id=mem.user_id,
            category=mem.category,
            importance=float(mem.importance),
            content=mem.content,
            source=mem.source,
            last_accessed_at=mem.last_accessed_at,
            access_count=int(mem.access_count or 0),
            is_active=bool(mem.is_active),
            metadata=dict(mem.metadata_ or {}),
            created_at=mem.created_at,
            updated_at=mem.updated_at,
        )

    async def list_memories(
        self, user_id: uuid.UUID, *, active_only: bool = True
    ) -> MemoryListResponse:
        items = await self.repo.list_for_user(user_id, active_only=active_only)
        return MemoryListResponse(items=[self._to_read(m) for m in items])

    async def get_memory(self, memory_id: uuid.UUID, user_id: uuid.UUID) -> MemoryRead:
        mem = await self.repo.get_for_user(memory_id, user_id)
        if mem is None:
            raise NotFoundError("Bellek", str(memory_id))
        await self.repo.touch(mem)
        return self._to_read(mem)

    async def create_memory(self, user_id: uuid.UUID, data: MemoryCreate) -> MemoryRead:
        content = data.content.strip()
        if not content:
            raise ValidationError("İçerik boş olamaz", field="content")
        meta = dict(data.metadata or {})
        meta.setdefault("embedding_ready", False)
        mem = Memory(
            user_id=user_id,
            category=data.category,
            importance=data.importance,
            content=content,
            source=data.source or MemorySource.MANUAL,
            metadata_=meta,
            is_active=True,
        )
        mem = await self.repo.add(mem)
        return self._to_read(mem)

    async def update_memory(
        self, memory_id: uuid.UUID, user_id: uuid.UUID, data: MemoryUpdate
    ) -> MemoryRead:
        mem = await self.repo.get_for_user(memory_id, user_id)
        if mem is None:
            raise NotFoundError("Bellek", str(memory_id))
        payload = data.model_dump(exclude_unset=True)
        if "content" in payload and payload["content"] is not None:
            payload["content"] = payload["content"].strip()
            if not payload["content"]:
                raise ValidationError("İçerik boş olamaz", field="content")
        if "metadata" in payload:
            meta = dict(payload.pop("metadata") or {})
            meta.setdefault("embedding_ready", False)
            mem.metadata_ = meta
        for key, value in payload.items():
            setattr(mem, key, value)
        mem.updated_at = datetime.now(UTC)
        await self.db.flush()
        return self._to_read(mem)

    async def delete_memory(self, memory_id: uuid.UUID, user_id: uuid.UUID) -> None:
        mem = await self.repo.get_for_user(memory_id, user_id)
        if mem is None:
            raise NotFoundError("Bellek", str(memory_id))
        await self.repo.delete(mem)

    async def search(self, user_id: uuid.UUID, data: MemorySearchRequest) -> MemoryListResponse:
        items = await self.repo.search(
            user_id, q=data.q, category=data.category, limit=data.limit
        )
        return MemoryListResponse(items=[self._to_read(m) for m in items])

    async def get_settings(self, user_id: uuid.UUID) -> MemorySettingsRead:
        pref = await self.notif.get_or_create(user_id)
        return MemorySettingsRead(ai_memory_enabled=bool(pref.ai_memory_enabled))

    async def update_settings(
        self, user_id: uuid.UUID, data: MemorySettingsUpdate
    ) -> MemorySettingsRead:
        pref = await self.notif.get_or_create(user_id)
        pref.ai_memory_enabled = data.ai_memory_enabled
        await self.db.flush()
        return MemorySettingsRead(ai_memory_enabled=bool(pref.ai_memory_enabled))

    async def is_memory_enabled(self, user_id: uuid.UUID) -> bool:
        pref = await self.notif.get_or_create(user_id)
        return bool(pref.ai_memory_enabled)

    async def export_memories(self, user_id: uuid.UUID) -> MemoryExportResponse:
        items = await self.repo.list_for_user(user_id, active_only=False, limit=1000)
        return MemoryExportResponse(
            exported_at=datetime.now(UTC),
            count=len(items),
            items=[self._to_read(m) for m in items],
        )

    async def clear_memories(self, user_id: uuid.UUID) -> int:
        return await self.repo.clear_for_user(user_id)
