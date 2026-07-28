"""
StudyOS — Revision Pydantic şemaları
Sprint-2.8 (Meeting-026)
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.revision import RevisionGrade, RevisionItemStatus, RevisionSourceType


class RevisionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    subject: str = Field(..., min_length=1, max_length=100)
    topic: str | None = Field(None, max_length=200)
    note: str | None = None
    source_type: RevisionSourceType = RevisionSourceType.MANUAL
    source_id: UUID | None = None
    difficulty: int = Field(3, ge=1, le=5)
    reason: str | None = Field(None, max_length=500)


class RevisionUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    subject: str | None = Field(None, min_length=1, max_length=100)
    topic: str | None = Field(None, max_length=200)
    note: str | None = None
    difficulty: int | None = Field(None, ge=1, le=5)
    status: RevisionItemStatus | None = None
    reason: str | None = Field(None, max_length=500)


class RevisionScheduleRead(BaseModel):
    due_at: datetime
    interval_days: int
    ease_factor: float
    repetition_count: int
    lapse_count: int
    last_reviewed_at: datetime | None = None

    model_config = {"from_attributes": True}


class RevisionItemRead(BaseModel):
    id: UUID
    title: str
    subject: str
    topic: str | None = None
    note: str | None = None
    source_type: RevisionSourceType
    source_id: UUID | None = None
    difficulty: int
    reason: str
    status: RevisionItemStatus
    schedule: RevisionScheduleRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RevisionReviewRequest(BaseModel):
    grade: RevisionGrade
    duration_seconds: int | None = Field(None, ge=0, le=86_400)


class RevisionPostponeRequest(BaseModel):
    days: int = Field(1, ge=1, le=60)


class RevisionSkipRequest(BaseModel):
    """Skip: due'yu +1 gün kaydırır (varsayılan)."""

    days: int = Field(1, ge=1, le=14)


class RevisionGenerateRequest(BaseModel):
    """Rule engine seed — LLM yok."""

    include_questions: bool = True
    include_exams: bool = True
    max_items: int = Field(8, ge=1, le=20)


class RevisionGenerateResponse(BaseModel):
    created: list[RevisionItemRead] = Field(default_factory=list)
    skipped_existing: int = 0
    message: str = ""


class RevisionExplainResponse(BaseModel):
    revision_id: UUID
    explanation: str
    provider: str
    used_fallback: bool = False
    reason: str
    difficulty: int


class RevisionStatisticsResponse(BaseModel):
    total_active: int = 0
    total_mastered: int = 0
    due_today: int = 0
    overdue: int = 0
    due_this_week: int = 0
    reviewed_today: int = 0
    reviewed_this_week: int = 0
    average_difficulty: float = 0.0
    average_ease: float = 0.0


class RevisionHeatmapDay(BaseModel):
    day: date
    review_count: int = 0


class RevisionHeatmapResponse(BaseModel):
    days: list[RevisionHeatmapDay] = Field(default_factory=list)
    start_date: date
    end_date: date


class DashboardRevisionSummary(BaseModel):
    due_today: int = 0
    overdue: int = 0
    due_this_week: int = 0
    next_due_at: datetime | None = None
    next_title: str | None = None
    overview_reason: str | None = None
    # Sprint 7 — en gecikmiş / sıradaki tekrar için gün sayısı
    overdue_days: int | None = None
