"""
StudyOS — Topic Notebook Service (AI Sprint - FAZ 2)
LOS § 3+4 — Her Topic'in yaşayan bilgi katmanı.

Notebook karar motoru değildir.
Yalnızca Topic bağlamındaki bilgileri toplar ve sunar.

Notebook içerir:
  - Topic'e ait kaynaklar (PDF, YouTube, Not)
  - Confidence + Evidence özeti
  - Son AI açıklamaları (meta)
  - Quiz özeti
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.topic_context_builder import TopicAIContext, TopicContextBuilder


class NotebookResourceItem(BaseModel):
    """Notebook'ta gösterilen kaynak."""
    title: str
    resource_type: str
    status: str
    url: str | None = None
    provider: str | None = None


class TopicNotebookSummary(BaseModel):
    """
    Topic Notebook özeti — Work Surface'te gösterilir.
    Karar içermez; LOS verisini sunar.
    """
    topic_code: str
    subject_code: str
    topic_name: str | None = None

    # Confidence özeti (LOS § 4)
    confidence_level: str = "unknown"
    belief_pct: float = 50.0
    trend: str = "stable"
    needs_explain: bool = False

    # Evidence özeti (LOS § 3)
    sample_count: int = 0
    accuracy_pct: float | None = None
    effort_minutes: float = 0.0

    # Kaynaklar
    resource_count: int = 0
    resources: list[NotebookResourceItem] = Field(default_factory=list)

    # AI panel erişilebilirliği
    explain_available: bool = False
    quiz_available: bool = False
    quiz_difficulty: str = "easy"

    # Sprint 19 — Knowledge Layer (ürün dili)
    knowledge_ready: bool = False
    knowledge_summary: str | None = None
    knowledge_chunk_count: int = 0
    knowledge_citation_count: int = 0
    knowledge_source_count: int = 0
    display_title: str = "Kaynak özeti"

    # Meta
    built_at: str = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TopicNotebookService:
    """
    LOS § 3+4 — Topic Notebook özet servisi.

    Kullanım:
        svc = TopicNotebookService(db)
        notebook = await svc.get_summary(user_id, subject_code, topic_code)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ctx_builder = TopicContextBuilder(db)

    async def get_summary(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        topic_name: str | None = None,
        subject_name: str | None = None,
    ) -> TopicNotebookSummary:
        """
        Topic Notebook özetini oluştur.
        TopicContextBuilder'dan alınan veriyi sunar.
        """
        ctx = await self.ctx_builder.build(
            user_id,
            subject_code,
            topic_code,
            topic_name=topic_name,
            subject_name=subject_name,
        )

        accuracy_pct = (
            round(ctx.weighted_accuracy * 100, 1)
            if ctx.weighted_accuracy is not None
            else None
        )

        resources = [
            NotebookResourceItem(
                title=r.get("title", ""),
                resource_type=r.get("resource_type", "other"),
                status=r.get("status", "not_started"),
                url=r.get("url"),
                provider=r.get("provider"),
            )
            for r in ctx.resources
        ]

        return TopicNotebookSummary(
            topic_code=topic_code,
            subject_code=subject_code,
            topic_name=topic_name or topic_code,
            confidence_level=ctx.confidence_level,
            belief_pct=round(ctx.belief * 100, 1),
            trend=_trend_label(ctx.trend_direction),
            needs_explain=ctx.needs_explain,
            sample_count=ctx.performance_sample_count,
            accuracy_pct=accuracy_pct,
            effort_minutes=ctx.effort_minutes,
            resource_count=ctx.resource_count,
            resources=resources,
            explain_available=True,
            quiz_available=True,
            quiz_difficulty=ctx.quiz_difficulty,
            knowledge_ready=ctx.knowledge_ready,
            knowledge_summary=ctx.knowledge_summary,
            knowledge_chunk_count=ctx.knowledge_chunk_count,
            knowledge_citation_count=ctx.knowledge_citation_count,
            knowledge_source_count=ctx.resource_count,
            display_title="Kaynak özeti",
            built_at=ctx.built_at,
        )


def _trend_label(trend: float) -> str:
    if trend > 0.15:
        return "rising"
    if trend < -0.15:
        return "falling"
    return "stable"
