"""
Alignment Sprint-3 — Topic Work Surface projection schemas.
Karar üretmez; Decision Engine Projection'ı taşır.
Sprint 15 — Intelligence / Timeline / Insights / Quiz History / Resources.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.dashboard import NextActionProjection
from app.schemas.learning_intelligence import (
    InsightCard,
    QuizHistoryItem,
    ResourceIntelligenceItem,
    TimelineEvent,
    TopicIntelligenceCard,
)


class TopicLearningState(BaseModel):
    """Learning State — durum özeti (karar değil)."""

    subject_code: str
    topic_code: str
    topic_name: str
    subject_name: str | None = None
    summary_line: str | None = None
    revision_due: bool = False
    study_minutes: int = 0
    session_count: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    blank_count: int = 0
    question_count: int = 0
    accuracy_pct: float = 0.0


class TopicSecondaryTool(BaseModel):
    """Secondary tool — asla Primary Action değildir."""

    id: str
    label: str
    deep_link_hint: str


class TopicWorkSurfaceProjection(BaseModel):
    """
    Topic Work Surface SSOT.
    Work Surface karar üretmez; primary_action Decision Engine'den gelir.
    """

    learning_state: TopicLearningState
    primary_action: NextActionProjection
    secondary_tools: list[TopicSecondaryTool] = Field(default_factory=list)
    # Sprint 15 — Learning Intelligence (read-only projections)
    intelligence: TopicIntelligenceCard | None = None
    timeline: list[TimelineEvent] = Field(default_factory=list)
    insights: list[InsightCard] = Field(default_factory=list)
    quiz_history: list[QuizHistoryItem] = Field(default_factory=list)
    resources: list[ResourceIntelligenceItem] = Field(default_factory=list)
    # Sprint 20 — Coach recommendation (Experience)
    coach_headline: str | None = None
    coach_body: str | None = None
    coach_cta_label: str | None = None
    coach_deep_link_hint: str | None = None
