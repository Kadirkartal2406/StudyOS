"""
Sprint 15 — Learning Intelligence projections.
Okuma/sunum katmanı; Decision / Confidence / Living Plan değiştirmez.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TopicIntelligenceCard(BaseModel):
    """M15.1 — Work Surface üst bilgi kartı."""

    topic_name: str
    headline: str
    stars: int = Field(ge=0, le=5, default=0)
    last_studied_label: str | None = None
    last_quiz_label: str | None = None
    confidence_label: str = "Bilinmiyor"
    confidence_level: str = "unknown"
    weak_spot: str | None = None
    suggestion: str | None = None


class TimelineEvent(BaseModel):
    """M15.2 — Topic öğrenme geçmişi satırı."""

    id: str
    kind: str  # quiz | pomodoro | revision | explain | activity
    title: str
    subtitle: str | None = None
    occurred_at: datetime
    relative_label: str
    deep_link_hint: str | None = None


class InsightCard(BaseModel):
    """M15.3 / M15.4 — Insight (Decision değil)."""

    id: str
    code: str
    message: str
    subject_code: str | None = None
    topic_code: str | None = None
    topic_name: str | None = None
    tone: str = "neutral"  # positive | caution | neutral
    deep_link_hint: str | None = None


class QuizHistoryItem(BaseModel):
    """M15.5 — Topic quiz geçmişi satırı."""

    id: uuid.UUID
    question_count: int
    accuracy_pct: float | None = None
    correct_count: int | None = None
    wrong_count: int | None = None
    blank_count: int | None = None
    status: str
    difficulty: str
    relative_label: str
    created_at: datetime
    submitted_at: datetime | None = None


class ResourceIntelligenceItem(BaseModel):
    """M15.6 — Kaynak + durum etiketi (+ Sprint 19 Knowledge health)."""

    id: uuid.UUID
    title: str
    resource_type: str
    status: str
    intelligence_label: str
    url: str | None = None
    provider: str | None = None
    # Sprint 19 — Source Intelligence
    knowledge_health: str | None = None
    chunk_count: int = 0
    citation_count: int = 0
    quiz_generated_count: int = 0
    used_by_ai: bool = False
    last_explain_at: str | None = None
    last_quiz_at: str | None = None


class FeedCard(BaseModel):
    """M15.4 — Dashboard kişisel feed kartı."""

    id: str
    title: str
    subtitle: str
    kind: str  # confidence | revision | quiz | insight | subject
    subject_code: str | None = None
    topic_code: str | None = None
    deep_link_hint: str | None = None
    tone: str = "neutral"


class ConfidenceTrendItem(BaseModel):
    """M15.7 — Journey confidence trend satırı."""

    subject_code: str
    topic_code: str
    topic_name: str
    confidence_level: str
    trend: str  # rising | falling | stable
    trend_label: str
    belief_pct: float | None = None


class JourneyTrendsProjection(BaseModel):
    rising: list[ConfidenceTrendItem] = Field(default_factory=list)
    falling: list[ConfidenceTrendItem] = Field(default_factory=list)
    stable: list[ConfidenceTrendItem] = Field(default_factory=list)
