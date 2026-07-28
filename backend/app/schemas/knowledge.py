"""Sprint 19 — Knowledge Layer schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeCitationRead(BaseModel):
    id: uuid.UUID
    source_title: str | None = None
    quote: str | None = None
    page_hint: str | None = None
    used_by: str
    relevance: float | None = None
    source_id: uuid.UUID | None = None
    chunk_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeSourceRead(BaseModel):
    id: uuid.UUID
    study_resource_id: uuid.UUID
    title: str
    resource_type: str
    health: str
    provider_name: str
    chunk_count: int = 0
    citation_count: int = 0
    quiz_generated_count: int = 0
    used_by_ai: bool = False
    last_explain_at: datetime | None = None
    last_quiz_at: datetime | None = None
    error_message: str | None = None
    indexed_at: datetime | None = None

    model_config = {"from_attributes": True}


class KnowledgeNotebookRead(BaseModel):
    id: uuid.UUID
    subject_code: str
    topic_code: str
    topic_name: str | None = None
    ai_summary: str | None = None
    source_count: int = 0
    chunk_count: int = 0
    citation_count: int = 0
    last_indexed_at: datetime | None = None
    sources: list[KnowledgeSourceRead] = Field(default_factory=list)
    recent_citations: list[KnowledgeCitationRead] = Field(default_factory=list)
    provider_name: str = "notebooklm"
    # Ürün dili — marka yok
    display_title: str = "Kaynak özeti"

    model_config = {"from_attributes": True}


class IndexResourceRequest(BaseModel):
    force: bool = False


class IndexResourceResult(BaseModel):
    source: KnowledgeSourceRead
    notebook_id: uuid.UUID
    message: str


class ReindexNotebookRequest(BaseModel):
    subject_code: str
    topic_code: str
    force: bool = True


class KnowledgePassageRead(BaseModel):
    content: str
    score: float
    source_title: str
    page_hint: str | None = None
    source_id: uuid.UUID | None = None
    chunk_id: uuid.UUID | None = None
