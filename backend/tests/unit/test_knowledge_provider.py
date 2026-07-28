"""Sprint 19 — Local KnowledgeProvider unit tests."""

from __future__ import annotations

import pytest

from app.providers.knowledge.base import RawDocument, RetrievedPassage
from app.providers.knowledge.local_provider import LocalKnowledgeProvider
from app.providers.knowledge.notebooklm_provider import NotebookLMKnowledgeProvider


@pytest.mark.asyncio
async def test_local_chunk_and_retrieve() -> None:
    provider = LocalKnowledgeProvider()
    doc = RawDocument(
        title="Pegem Paragraf",
        text=(
            "Paragraf sorularında ana fikir cümlenin tamamını kapsar. "
            "Destekleyici cümleler örnek verir. "
            "Çeldiriciler kısmi doğrular içerir."
        ),
        resource_type="pdf",
        metadata={"page_hint": "Sayfa 42"},
    )
    chunks = await provider.parse_and_chunk(doc)
    assert len(chunks) >= 1
    assert chunks[0].embedding is not None

    passages = [
        RetrievedPassage(
            content=c.content,
            score=0.0,
            source_title=doc.title,
            page_hint=c.page_hint,
            chunk_id=str(i),
            source_id="s1",
            metadata={"embedding": c.embedding},
        )
        for i, c in enumerate(chunks)
    ]
    hit = await provider.retrieve("ana fikir paragraf", passages, top_k=2)
    assert hit
    assert hit[0].score >= 0


@pytest.mark.asyncio
async def test_notebooklm_adapter_name() -> None:
    p = NotebookLMKnowledgeProvider()
    assert p.provider_name == "notebooklm"
    chunks = await p.parse_and_chunk(
        RawDocument(title="Not", text="Vatandaşlık anayasa", resource_type="note")
    )
    assert chunks
