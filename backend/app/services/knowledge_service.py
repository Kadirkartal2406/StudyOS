"""
Sprint 19 — Knowledge Service (LOS §12).
Resource → parse → chunk → embed → notebook index.
Decision / Confidence / Policy üretmez.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.knowledge import (
    CitationUsedBy,
    KnowledgeChunk,
    KnowledgeCitation,
    KnowledgeHealth,
    KnowledgeNotebook,
    KnowledgeSource,
)
from app.models.study_resource import StudyResource
from app.providers.knowledge import get_knowledge_provider
from app.providers.knowledge.base import RawDocument, RetrievedPassage
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import (
    IndexResourceResult,
    KnowledgeCitationRead,
    KnowledgeNotebookRead,
    KnowledgePassageRead,
    KnowledgeSourceRead,
)


class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.provider = get_knowledge_provider()

    def _source_read(self, s: KnowledgeSource) -> KnowledgeSourceRead:
        return KnowledgeSourceRead.model_validate(s)

    async def get_notebook(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        topic_name: str | None = None,
    ) -> KnowledgeNotebookRead:
        nb = await self.repo.get_or_create_notebook(
            user_id, subject_code, topic_code, topic_name=topic_name
        )
        citations = await self.repo.list_citations(nb.id, limit=8)
        return KnowledgeNotebookRead(
            id=nb.id,
            subject_code=nb.subject_code,
            topic_code=nb.topic_code,
            topic_name=nb.topic_name or topic_name,
            ai_summary=nb.ai_summary,
            source_count=nb.source_count,
            chunk_count=nb.chunk_count,
            citation_count=nb.citation_count,
            last_indexed_at=nb.last_indexed_at,
            sources=[self._source_read(s) for s in (nb.sources or [])],
            recent_citations=[
                KnowledgeCitationRead.model_validate(c) for c in citations
            ],
            provider_name=self.provider.provider_name,
            display_title="Kaynak özeti",
        )

    async def get_notebook_by_id(
        self, user_id: uuid.UUID, notebook_id: uuid.UUID
    ) -> KnowledgeNotebookRead:
        nb = await self.repo.get_notebook_by_id(notebook_id, user_id)
        if nb is None:
            raise NotFoundError("Notebook", str(notebook_id))
        return await self.get_notebook(
            user_id, nb.subject_code, nb.topic_code, topic_name=nb.topic_name
        )

    async def list_citations(
        self, user_id: uuid.UUID, notebook_id: uuid.UUID
    ) -> list[KnowledgeCitationRead]:
        nb = await self.repo.get_notebook_by_id(notebook_id, user_id)
        if nb is None:
            raise NotFoundError("Notebook", str(notebook_id))
        rows = await self.repo.list_citations(notebook_id, limit=100)
        return [KnowledgeCitationRead.model_validate(c) for c in rows]

    async def index_resource(
        self,
        user_id: uuid.UUID,
        resource_id: uuid.UUID,
        *,
        force: bool = False,
    ) -> IndexResourceResult:
        resource = await self.db.scalar(
            select(StudyResource).where(
                StudyResource.id == resource_id,
                StudyResource.user_id == user_id,
            )
        )
        if resource is None:
            raise NotFoundError("StudyResource", str(resource_id))
        if not resource.topic_code or not resource.subject_code:
            raise ValidationError(
                "Kaynak topic_code ve subject_code olmadan indexlenemez"
            )

        nb = await self.repo.get_or_create_notebook(
            user_id,
            resource.subject_code,
            resource.topic_code,
        )
        source = await self.repo.get_source_by_resource(resource.id)
        if source is None:
            source = KnowledgeSource(
                user_id=user_id,
                notebook_id=nb.id,
                study_resource_id=resource.id,
                subject_code=resource.subject_code,
                topic_code=resource.topic_code,
                title=resource.title,
                resource_type=str(resource.resource_type),
                health=KnowledgeHealth.PROCESSING,
                provider_name=self.provider.provider_name,
            )
            self.db.add(source)
            await self.db.flush()
        elif (
            not force
            and source.health == KnowledgeHealth.READY
            and source.chunk_count > 0
        ):
            return IndexResourceResult(
                source=self._source_read(source),
                notebook_id=nb.id,
                message="Kaynak zaten indexli",
            )

        source.health = KnowledgeHealth.PROCESSING
        source.error_message = None
        source.title = resource.title
        source.provider_name = self.provider.provider_name
        await self.db.flush()

        try:
            text = self._extract_text(resource)
            doc = RawDocument(
                title=resource.title,
                text=text,
                resource_type=str(resource.resource_type),
                url=resource.url,
                metadata={
                    "description": resource.description,
                    "provider": resource.provider,
                },
            )
            parsed = await self.provider.parse_and_chunk(doc)
            await self.repo.delete_chunks_for_source(source.id)
            await self.db.flush()

            for pc in parsed:
                self.db.add(
                    KnowledgeChunk(
                        notebook_id=nb.id,
                        source_id=source.id,
                        user_id=user_id,
                        subject_code=resource.subject_code,
                        topic_code=resource.topic_code,
                        ord_index=pc.ord_index,
                        content=pc.content,
                        page_hint=pc.page_hint,
                        token_estimate=pc.token_estimate,
                        embedding=pc.embedding,
                        metadata_=pc.metadata or {},
                    )
                )
            source.chunk_count = len(parsed)
            source.health = (
                KnowledgeHealth.READY if parsed else KnowledgeHealth.ERROR
            )
            if not parsed:
                source.error_message = "İçerik çıkarılamadı"
            source.indexed_at = datetime.now(UTC)
            await self.db.flush()

            await self._refresh_notebook_stats(nb.id)
            # AI summary (ürün dili)
            chunks = await self.repo.list_chunks_for_notebook(nb.id)
            summary = await self.provider.summarize(
                resource.topic_code,
                [c.content for c in chunks[:12]],
            )
            nb = await self.repo.get_notebook_by_id(nb.id, user_id)
            if nb and summary:
                nb.ai_summary = summary
                nb.last_indexed_at = datetime.now(UTC)
                await self.db.flush()

            return IndexResourceResult(
                source=self._source_read(source),
                notebook_id=nb.id if nb else source.notebook_id,
                message="Kaynak indexlendi" if parsed else "Index hatası",
            )
        except Exception as exc:  # noqa: BLE001
            source.health = KnowledgeHealth.ERROR
            source.error_message = str(exc)[:500]
            await self.db.flush()
            return IndexResourceResult(
                source=self._source_read(source),
                notebook_id=source.notebook_id,
                message="Index başarısız",
            )

    async def reindex_topic(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        force: bool = True,
    ) -> KnowledgeNotebookRead:
        rows = (
            await self.db.scalars(
                select(StudyResource).where(
                    StudyResource.user_id == user_id,
                    StudyResource.subject_code == subject_code,
                    StudyResource.topic_code == topic_code,
                )
            )
        ).all()
        for r in rows:
            await self.index_resource(user_id, r.id, force=force)
        return await self.get_notebook(user_id, subject_code, topic_code)

    async def retrieve_for_topic(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[KnowledgePassageRead]:
        nb = await self.repo.get_notebook(user_id, subject_code, topic_code)
        if nb is None:
            return []
        chunks = await self.repo.list_chunks_for_notebook(nb.id)
        if not chunks:
            return []
        source_map = {
            s.id: s for s in await self.repo.list_sources_for_topic(
                user_id, subject_code, topic_code
            )
        }
        passages = [
            RetrievedPassage(
                content=c.content,
                score=0.0,
                source_title=(
                    source_map[c.source_id].title
                    if c.source_id in source_map
                    else "Kaynak"
                ),
                page_hint=c.page_hint,
                chunk_id=str(c.id),
                source_id=str(c.source_id),
                metadata={"embedding": c.embedding or []},
            )
            for c in chunks
        ]
        hit = await self.provider.retrieve(query, passages, top_k=top_k)
        return [
            KnowledgePassageRead(
                content=h.content,
                score=h.score,
                source_title=h.source_title,
                page_hint=h.page_hint,
                source_id=uuid.UUID(h.source_id) if h.source_id else None,
                chunk_id=uuid.UUID(h.chunk_id) if h.chunk_id else None,
            )
            for h in hit
        ]

    async def record_citations(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        passages: list[KnowledgePassageRead],
        *,
        used_by: str = CitationUsedBy.EXPLAIN,
    ) -> list[KnowledgeCitation]:
        if not passages:
            return []
        nb = await self.repo.get_or_create_notebook(
            user_id, subject_code, topic_code
        )
        created: list[KnowledgeCitation] = []
        now = datetime.now(UTC)
        for p in passages:
            cit = KnowledgeCitation(
                notebook_id=nb.id,
                chunk_id=p.chunk_id,
                source_id=p.source_id,
                user_id=user_id,
                subject_code=subject_code,
                topic_code=topic_code,
                used_by=used_by,
                source_title=p.source_title,
                quote=(p.content[:400] if p.content else None),
                page_hint=p.page_hint,
                relevance=p.score,
            )
            self.db.add(cit)
            created.append(cit)
            if p.source_id:
                src = await self.db.get(KnowledgeSource, p.source_id)
                if src:
                    src.used_by_ai = True
                    src.citation_count = (src.citation_count or 0) + 1
                    if used_by == CitationUsedBy.EXPLAIN:
                        src.last_explain_at = now
                    elif used_by == CitationUsedBy.QUIZ:
                        src.last_quiz_at = now
                        src.quiz_generated_count = (src.quiz_generated_count or 0) + 1
        await self.db.flush()
        await self._refresh_notebook_stats(nb.id)
        return created

    async def _refresh_notebook_stats(self, notebook_id: uuid.UUID) -> None:
        nb = await self.db.get(KnowledgeNotebook, notebook_id)
        if nb is None:
            return
        sources = await self.repo.list_sources_for_topic(
            nb.user_id, nb.subject_code, nb.topic_code
        )
        chunks = await self.repo.list_chunks_for_notebook(notebook_id)
        nb.source_count = len(sources)
        nb.chunk_count = len(chunks)
        nb.citation_count = await self.repo.count_citations(notebook_id)
        nb.last_indexed_at = datetime.now(UTC)
        await self.db.flush()

    @staticmethod
    def _extract_text(resource: StudyResource) -> str:
        parts: list[str] = []
        if resource.title:
            parts.append(resource.title)
        if resource.description:
            parts.append(resource.description)
        meta = resource.metadata_ or {}
        for key in ("text", "notes", "content", "transcript", "body"):
            val = meta.get(key)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
        if resource.author:
            parts.append(f"Yazar: {resource.author}")
        if resource.provider:
            parts.append(f"Sağlayıcı: {resource.provider}")
        if resource.url and not parts:
            parts.append(f"Kaynak bağlantısı: {resource.url}")
        return "\n\n".join(parts)
