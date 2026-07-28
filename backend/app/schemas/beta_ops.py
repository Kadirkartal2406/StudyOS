"""Sprint 21 RC — Analytics + Beta Feedback schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AnalyticsTrackRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    platform: str | None = None
    app_version: str | None = None
    session_id: str | None = None
    properties: dict = Field(default_factory=dict)


class AnalyticsTrackResult(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime


class AnalyticsBatchRequest(BaseModel):
    events: list[AnalyticsTrackRequest] = Field(default_factory=list, max_length=50)


class AnalyticsBatchResult(BaseModel):
    accepted: int


class AnalyticsMetricCount(BaseModel):
    key: str
    label: str
    value: int


class AnalyticsNamedCount(BaseModel):
    name: str
    count: int


class AnalyticsDashboardRead(BaseModel):
    """RC2 M22.4 — mevcut eventlerden aggregation (yeni event yok)."""

    days: int
    dau: int
    session_count: int
    assessment_completion: int
    quiz_completion: int
    pomodoro_started: int
    next_action_completed: int
    explain_used: int
    knowledge_used: int
    coach_viewed: int
    journey_viewed: int
    exam_distribution: list[AnalyticsNamedCount] = Field(default_factory=list)
    topic_distribution: list[AnalyticsNamedCount] = Field(default_factory=list)
    screen_usage: list[AnalyticsNamedCount] = Field(default_factory=list)
    drop_off: list[AnalyticsNamedCount] = Field(default_factory=list)
    event_totals: list[AnalyticsMetricCount] = Field(default_factory=list)


class BetaFeedbackCreate(BaseModel):
    kind: str = Field(description="bug | suggestion | other")
    message: str = Field(min_length=5, max_length=4000)
    screen_hint: str | None = None
    app_version: str | None = None
    platform: str | None = None
    log_excerpt: str | None = Field(default=None, max_length=8000)


class BetaFeedbackRead(BaseModel):
    id: uuid.UUID
    kind: str
    message: str
    screen_hint: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
