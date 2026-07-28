"""
StudyOS — Planner Pydantic şemaları
Sprint-2.7 (Meeting-025)
"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.planner_draft import PlannerDraftStatus
from app.models.question_record import ExamType
from app.schemas.study_plan import StudyPlanRead


class PlannerGenerateRequest(BaseModel):
    """F1 — alanlar opsiyonel; boşsa Learning Profile default kullanılır."""

    target_exam: ExamType | None = None
    target_net: float | None = Field(default=None, gt=0, le=200)
    available_days: list[int] | None = Field(default=None, max_length=7)
    available_hours: float | None = Field(default=None, gt=0, le=16)

    @field_validator("available_days")
    @classmethod
    def _valid_weekdays(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return v
        # 0=Pazartesi … 6=Pazar (Python weekday)
        cleaned = sorted({d for d in v if 0 <= d <= 6})
        if not cleaned:
            raise ValueError("En az bir geçerli gün (0–6) gerekli")
        return cleaned


class PlannerItemRead(BaseModel):
    study_date: date
    title: str
    subject: str
    topic: str | None = None
    target_question_count: int
    estimated_minutes: int
    start_time: str | None = None
    end_time: str | None = None
    resource_ids: list[str] = Field(default_factory=list)
    resource_titles: list[str] = Field(default_factory=list)
    reason: str


class PlannerDraftRead(BaseModel):
    id: UUID
    user_id: UUID
    status: PlannerDraftStatus
    target_exam: ExamType
    target_net: float
    available_days: list[int]
    available_hours: float
    items: list[PlannerItemRead] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    rationale: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    accepted_at: datetime | None = None


class PlannerAcceptRequest(BaseModel):
    """G3 — force=true çakışmaları yok sayıp mevcut planların yanına ekler."""

    force: bool = False


class PlannerConflictDay(BaseModel):
    study_date: date
    existing_plan_count: int
    existing_titles: list[str] = Field(default_factory=list)


class PlannerAcceptConflict(BaseModel):
    message: str = "Seçilen günlerde mevcut planlar var"
    conflicts: list[PlannerConflictDay]
    draft_id: UUID


class PlannerAcceptResponse(BaseModel):
    draft: PlannerDraftRead
    created_plans: list[StudyPlanRead] = Field(default_factory=list)


class PlannerExplainResponse(BaseModel):
    draft_id: UUID
    explanation: str
    provider: str
    used_fallback: bool = False
    # Saklanan rationale — yeniden üretim yok
    rationale: dict[str, Any] = Field(default_factory=dict)
    item_reasons: list[dict[str, str]] = Field(default_factory=list)


class PlannerSuggestionListResponse(BaseModel):
    """Sprint-9: pending Living Plan suggestions."""

    suggestions: list[PlannerDraftRead] = Field(default_factory=list)
    count: int = 0


class DashboardPlannerSummary(BaseModel):
    draft_id: UUID | None = None
    status: str | None = None
    target_exam: str | None = None
    target_net: float | None = None
    item_count: int = 0
    overview_reason: str | None = None
    created_at: datetime | None = None
