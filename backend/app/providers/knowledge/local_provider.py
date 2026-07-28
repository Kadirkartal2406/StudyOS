"""Local RAG KnowledgeProvider — harici API olmadan çalışır."""

from __future__ import annotations

import hashlib
import math
import re

from app.providers.knowledge.base import (
    KnowledgeProvider,
    ParsedChunk,
    RawDocument,
    RetrievedPassage,
)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+", text.lower())


def _chunk_text(text: str, *, max_chars: int = 700) -> list[str]:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]
    parts: list[str] = []
    # Prefer paragraph / sentence breaks
    paragraphs = re.split(r"(?<=[.!?])\s+|\n{2,}", cleaned)
    buf = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(buf) + len(p) + 1 <= max_chars:
            buf = f"{buf} {p}".strip()
        else:
            if buf:
                parts.append(buf)
            if len(p) <= max_chars:
                buf = p
            else:
                for i in range(0, len(p), max_chars):
                    parts.append(p[i : i + max_chars])
                buf = ""
    if buf:
        parts.append(buf)
    return parts


def _hash_embed(text: str, dim: int = 64) -> list[float]:
    """Deterministik bag-of-hash embedding (harici model yok)."""
    vec = [0.0] * dim
    toks = _tokenize(text)
    if not toks:
        return vec
    for t in toks:
        h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b, strict=True))


class LocalKnowledgeProvider(KnowledgeProvider):
    @property
    def provider_name(self) -> str:
        return "local"

    async def parse_and_chunk(self, doc: RawDocument) -> list[ParsedChunk]:
        body = doc.text.strip()
        if not body:
            # En azından başlık + meta ile indexlenebilir iz bırak
            bits = [doc.title]
            if doc.url:
                bits.append(f"Kaynak URL: {doc.url}")
            if doc.metadata.get("description"):
                bits.append(str(doc.metadata["description"]))
            body = "\n".join(bits)
        pieces = _chunk_text(body)
        chunks: list[ParsedChunk] = []
        for i, content in enumerate(pieces):
            page = None
            if doc.metadata.get("page_hint"):
                page = str(doc.metadata["page_hint"])
            elif i > 0:
                page = f"bölüm {i + 1}"
            chunks.append(
                ParsedChunk(
                    content=content,
                    ord_index=i,
                    page_hint=page,
                    token_estimate=max(1, len(content) // 4),
                    embedding=_hash_embed(content),
                    metadata={"resource_type": doc.resource_type},
                )
            )
        return chunks

    async def embed(self, texts: list[str]) -> list[list[float] | None]:
        return [_hash_embed(t) for t in texts]

    async def retrieve(
        self,
        query: str,
        passages: list[RetrievedPassage],
        *,
        top_k: int = 5,
    ) -> list[RetrievedPassage]:
        if not passages:
            return []
        q_emb = _hash_embed(query)
        q_toks = set(_tokenize(query))
        scored: list[RetrievedPassage] = []
        for p in passages:
            emb = p.metadata.get("embedding")
            cos = _cosine(q_emb, emb) if isinstance(emb, list) else 0.0
            overlap = 0.0
            if q_toks:
                pt = set(_tokenize(p.content))
                overlap = len(q_toks & pt) / max(len(q_toks), 1)
            score = 0.65 * cos + 0.35 * overlap
            scored.append(
                RetrievedPassage(
                    content=p.content,
                    score=score,
                    source_title=p.source_title,
                    page_hint=p.page_hint,
                    chunk_id=p.chunk_id,
                    source_id=p.source_id,
                    metadata=p.metadata,
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return [s for s in scored if s.score > 0.02][:top_k] or scored[: min(top_k, len(scored))]
