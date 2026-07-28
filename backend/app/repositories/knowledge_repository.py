"""Sprint 19 — Knowledge repository."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.knowledge import (
    KnowledgeChunk,
    KnowledgeCitation,
    KnowledgeNotebook,
    KnowledgeSource,
)


class KnowledgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_notebook(
        self, user_id: uuid.UUID, subject_code: str, topic_code: str
    ) -> KnowledgeNotebook | None:
        return await self.db.scalar(
            select(KnowledgeNotebook)
            .where(
                KnowledgeNotebook.user_id == user_id,
                KnowledgeNotebook.subject_code == subject_code,
                KnowledgeNotebook.topic_code == topic_code,
            )
            .options(
                selectinload(KnowledgeNotebook.sources),
                selectinload(KnowledgeNotebook.chunks),
            )
        )

    async def get_notebook_by_id(
        self, notebook_id: uuid.UUID, user_id: uuid.UUID
    ) -> KnowledgeNotebook | None:
        return await self.db.scalar(
            select(KnowledgeNotebook)
            .where(
                KnowledgeNotebook.id == notebook_id,
                KnowledgeNotebook.user_id == user_id,
            )
            .options(selectinload(KnowledgeNotebook.sources))
        )

    async def get_or_create_notebook(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        topic_name: str | None = None,
    ) -> KnowledgeNotebook:
        nb = await self.get_notebook(user_id, subject_code, topic_code)
        if nb:
            if topic_name and not nb.topic_name:
                nb.topic_name = topic_name
            return nb
        nb = KnowledgeNotebook(
            user_id=user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            topic_name=topic_name,
        )
        self.db.add(nb)
        await self.db.flush()
        return nb

    async def get_source_by_resource(
        self, study_resource_id: uuid.UUID
    ) -> KnowledgeSource | None:
        return await self.db.scalar(
            select(KnowledgeSource).where(
                KnowledgeSource.study_resource_id == study_resource_id
            )
        )

    async def list_sources_for_topic(
        self, user_id: uuid.UUID, subject_code: str, topic_code: str
    ) -> list[KnowledgeSource]:
        rows = await self.db.scalars(
            select(KnowledgeSource).where(
                KnowledgeSource.user_id == user_id,
                KnowledgeSource.subject_code == subject_code,
                KnowledgeSource.topic_code == topic_code,
            )
        )
        return list(rows.all())

    async def list_chunks_for_notebook(
        self, notebook_id: uuid.UUID
    ) -> list[KnowledgeChunk]:
        rows = await self.db.scalars(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.notebook_id == notebook_id)
            .order_by(KnowledgeChunk.ord_index.asc())
        )
        return list(rows.all())

    async def delete_chunks_for_source(self, source_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(KnowledgeChunk).where(KnowledgeChunk.source_id == source_id)
        )

    async def list_citations(
        self, notebook_id: uuid.UUID, *, limit: int = 50
    ) -> list[KnowledgeCitation]:
        rows = await self.db.scalars(
            select(KnowledgeCitation)
            .where(KnowledgeCitation.notebook_id == notebook_id)
            .order_by(KnowledgeCitation.created_at.desc())
            .limit(limit)
        )
        return list(rows.all())

    async def count_citations(self, notebook_id: uuid.UUID) -> int:
        return int(
            await self.db.scalar(
                select(func.count())
                .select_from(KnowledgeCitation)
                .where(KnowledgeCitation.notebook_id == notebook_id)
            )
            or 0
        )
