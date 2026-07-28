"""
StudyOS — Conversation Summary Service (J1)
Sprint-2.4: altyapı hazır; chat akışında aktif üretilmez / kullanılmaz.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.conversation_repository import ConversationRepository


class ConversationSummaryService:
    """Pasif CRUD iskeleti — generate_summary bilinçli olarak no-op."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversations = ConversationRepository(db)

    async def get_summary(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> str | None:
        conv = await self.conversations.get_for_user(conversation_id, user_id)
        if conv is None:
            raise NotFoundError("Sohbet", str(conversation_id))
        return conv.summary

    async def upsert_summary(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        summary: str | None,
    ) -> str | None:
        """Manuel/gelecek kullanım için; ChatService çağırmıyor."""
        conv = await self.conversations.get_for_user(conversation_id, user_id)
        if conv is None:
            raise NotFoundError("Sohbet", str(conversation_id))
        conv.summary = summary
        conv.summary_updated_at = datetime.now(UTC) if summary else None
        await self.db.flush()
        return conv.summary

    async def generate_summary(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """J1: aktif değil — bilerek no-op (sonraki sprint)."""
        return None
