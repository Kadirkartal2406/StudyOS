"""KnowledgeProvider factory."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.providers.knowledge.base import KnowledgeProvider
from app.providers.knowledge.local_provider import LocalKnowledgeProvider
from app.providers.knowledge.notebooklm_provider import NotebookLMKnowledgeProvider


@lru_cache
def get_knowledge_provider() -> KnowledgeProvider:
    name = (settings.KNOWLEDGE_PROVIDER or "notebooklm").strip().lower()
    if name in ("local", "local_rag", "rag"):
        return LocalKnowledgeProvider()
    # Varsayılan / notebooklm / gemini (ileride) → NotebookLM adaptör yüzeyi
    return NotebookLMKnowledgeProvider()
