"""
NotebookLM KnowledgeProvider — Sprint 19 ilk provider adaptörü.

Gerçek NotebookLM HTTP API bağlanana kadar Local RAG üzerinde çalışır;
provider_name = notebooklm kalır. Domain servisleri değişmez.
"""

from __future__ import annotations

from app.providers.knowledge.base import (
    KnowledgeProvider,
    ParsedChunk,
    RawDocument,
    RetrievedPassage,
)
from app.providers.knowledge.local_provider import LocalKnowledgeProvider


class NotebookLMKnowledgeProvider(KnowledgeProvider):
    """
    İlk Knowledge provider yüzeyi.
    Şimdilik Local pipeline'ı sarmalar; API gelince yalnızca bu sınıf değişir.
    """

    def __init__(self) -> None:
        self._local = LocalKnowledgeProvider()

    @property
    def provider_name(self) -> str:
        return "notebooklm"

    async def parse_and_chunk(self, doc: RawDocument) -> list[ParsedChunk]:
        chunks = await self._local.parse_and_chunk(doc)
        for c in chunks:
            c.metadata = {**(c.metadata or {}), "via": "notebooklm_adapter"}
        return chunks

    async def embed(self, texts: list[str]) -> list[list[float] | None]:
        return await self._local.embed(texts)

    async def retrieve(
        self,
        query: str,
        passages: list[RetrievedPassage],
        *,
        top_k: int = 5,
    ) -> list[RetrievedPassage]:
        return await self._local.retrieve(query, passages, top_k=top_k)

    async def summarize(self, title: str, passages: list[str]) -> str | None:
        return await self._local.summarize(title, passages)
