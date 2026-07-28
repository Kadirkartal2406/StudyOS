"""
Sprint 19 — KnowledgeProvider soyutlaması.
Provider değişince domain servisleri değişmez.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RawDocument:
    """Indexlenecek ham belge."""

    title: str
    text: str
    resource_type: str
    url: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedChunk:
    content: str
    ord_index: int
    page_hint: str | None = None
    token_estimate: int = 0
    embedding: list[float] | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievedPassage:
    content: str
    score: float
    source_title: str
    page_hint: str | None = None
    chunk_id: str | None = None
    source_id: str | None = None
    metadata: dict = field(default_factory=dict)


class KnowledgeProvider(ABC):
    """Knowledge Layer adaptör sözleşmesi — Decision üretmez."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def parse_and_chunk(self, doc: RawDocument) -> list[ParsedChunk]:
        """PDF/not/url metnini chunk'lara ayır."""
        ...

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float] | None]:
        """Opsiyonel embedding; yoksa None listesi."""
        ...

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        passages: list[RetrievedPassage],
        *,
        top_k: int = 5,
    ) -> list[RetrievedPassage]:
        """Aday passage'lar arasından en ilgili olanları seç."""
        ...

    async def summarize(self, title: str, passages: list[str]) -> str | None:
        """Opsiyonel notebook özeti."""
        if not passages:
            return None
        joined = " ".join(p[:200] for p in passages[:8])
        return f"{title}: {joined[:400]}…"
