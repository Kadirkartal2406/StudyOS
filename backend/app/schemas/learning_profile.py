"""
StudyOS — Learning Profile / Onboarding şemaları (Sprint-3.0)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field, field_validator, model_validator

from app.core.exam_identity import canonicalize_exam_type, coerce_exam_payload
from app.models.learning_profile import BaselineLevel, JourneyStage
from app.models.question_record import ExamType


def _coerce_exam_type(v: Any) -> Any:
    if isinstance(v, ExamType):
        return v
    if isinstance(v, str):
        return canonicalize_exam_type(v, None)
    return v


CoercedExamType = Annotated[ExamType, BeforeValidator(_coerce_exam_type)]


class ExamTargetCreate(BaseModel):
    exam_type: CoercedExamType
    is_primary: bool = False
    weight: float = Field(default=1.0, gt=0, le=10)
    target_net: float | None = Field(default=None, gt=0, le=200)
    target_score: float | None = None
    target_rank: int | None = Field(default=None, gt=0)
    target_university: str | None = Field(default=None, max_length=200)
    target_department: str | None = Field(default=None, max_length=200)
    branch: str | None = Field(default=None, max_length=100)
    exam_date: date | None = None

    @model_validator(mode="before")
    @classmethod
    def _fold_parent_branch(cls, data: Any) -> Any:
        return coerce_exam_payload(data)

class ExamTargetUpdate(BaseModel):
    is_primary: bool | None = None
    weight: float | None = Field(default=None, gt=0, le=10)
    target_net: float | None = Field(default=None, gt=0, le=200)
    target_score: float | None = None
    target_rank: int | None = Field(default=None, gt=0)
    target_university: str | None = Field(default=None, max_length=200)
    target_department: str | None = Field(default=None, max_length=200)
    branch: str | None = Field(default=None, max_length=100)
    exam_date: date | None = None


class ExamTargetRead(BaseModel):
    id: UUID
    user_id: UUID
    exam_type: ExamType
    is_primary: bool
    weight: float
    target_net: float | None = None
    target_score: float | None = None
    target_rank: int | None = None
    target_university: str | None = None
    target_department: str | None = None
    branch: str | None = None
    exam_date: date | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_stored(cls, data: Any) -> Any:
        # Legacy DB rows may still store parent codes (kpss, yds, …)
        if hasattr(data, "exam_type"):
            return data
        return coerce_exam_payload(data) if isinstance(data, dict) else data


class SubjectCatalogRead(BaseModel):
    id: UUID
    code: str
    name: str
    exam_types: list[str]
    sort_order: int
    section: str | None = None

    model_config = {"from_attributes": True}


class TopicCatalogRead(BaseModel):
    """Sprint-3.2.A — topic_code identity; name = display."""

    id: UUID
    code: str
    name: str
    subject_code: str
    sort_order: int
    difficulty: int | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class UserSubjectRead(BaseModel):
    id: UUID
    subject_code: str
    subject_name: str
    is_active: bool
    source: str
    section: str | None = None
    # Sprint-3.0.1 — additive metrics (computed, nullable)
    total_questions: int = 0
    study_minutes: int = 0
    accuracy: float = 0.0
    last_studied_at: datetime | None = None
    last_revision_at: datetime | None = None
    progress_pct: float = 0.0

    model_config = {"from_attributes": True}


class DashboardSubjectsSummary(BaseModel):
    """Dashboard Derslerim insight (Sprint-3.0.1)."""

    most_studied_subject: str | None = None
    weakest_subject: str | None = None
    longest_idle_subject: str | None = None
    today_studied_count: int = 0
    primary_exam_type: str | None = None
    subject_count: int = 0



class LearningProfileRead(BaseModel):
    user_id: UUID
    journey_stage: JourneyStage
    onboarding_completed: bool
    onboarding_skipped: bool
    onboarding_required: bool
    daily_study_minutes: int
    available_days: list[int]
    available_hours: float
    baseline_level: BaselineLevel
    baseline_reason: str | None = None
    exam_targets: list[ExamTargetRead] = Field(default_factory=list)
    subjects: list[UserSubjectRead] = Field(default_factory=list)
    # Sprint-3.1.A — Primary / Active Exam SSOT
    primary_exam_type: str | None = None
    active_exam_type: str | None = None


class ActiveExamUpdate(BaseModel):
    """Sprint-3.1.A — Active Exam değiştir (Primary'ye dokunmaz)."""

    exam_type: CoercedExamType

    @model_validator(mode="before")
    @classmethod
    def _fold_parent_branch(cls, data: Any) -> Any:
        return coerce_exam_payload(data)

class LearningProfileUpdate(BaseModel):
    daily_study_minutes: int | None = Field(default=None, ge=15, le=720)
    available_days: list[int] | None = None
    available_hours: float | None = Field(default=None, gt=0, le=16)
    baseline_level: BaselineLevel | None = None
    baseline_reason: str | None = Field(default=None, max_length=500)

    @field_validator("available_days")
    @classmethod
    def _days(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return v
        cleaned = sorted({d for d in v if 0 <= d <= 6})
        if not cleaned:
            raise ValueError("En az bir geçerli gün (0–6) gerekli")
        return cleaned


class OnboardingExamTargetInput(BaseModel):
    exam_type: CoercedExamType
    is_primary: bool = False
    target_net: float | None = Field(default=None, gt=0, le=200)
    target_score: float | None = None
    target_rank: int | None = None
    target_university: str | None = None
    target_department: str | None = None
    branch: str | None = None
    exam_date: date | None = None
    weight: float = 1.0

    @model_validator(mode="before")
    @classmethod
    def _fold_parent_branch(cls, data: Any) -> Any:
        return coerce_exam_payload(data)

class OnboardingCompleteRequest(BaseModel):
    """D1 — tek complete payload (wizard adımları istemci tarafında)."""

    exam_targets: list[OnboardingExamTargetInput] = Field(..., min_length=1)
    available_days: list[int] = Field(..., min_length=1, max_length=7)
    available_hours: float = Field(..., gt=0, le=16)
    daily_study_minutes: int = Field(..., ge=15, le=720)
    baseline_level: BaselineLevel = BaselineLevel.UNKNOWN
    baseline_reason: str | None = Field(default=None, max_length=500)

    @field_validator("available_days")
    @classmethod
    def _days(cls, v: list[int]) -> list[int]:
        cleaned = sorted({d for d in v if 0 <= d <= 6})
        if not cleaned:
            raise ValueError("En az bir geçerli gün (0–6) gerekli")
        return cleaned


class OnboardingStatusRead(BaseModel):
    onboarding_required: bool
    onboarding_completed: bool
    onboarding_skipped: bool
    journey_stage: JourneyStage
    can_skip: bool = False  # Sprint-3.1.A — hard gate; skip UI kaldırıldı


class JourneyProgressSummary(BaseModel):
    """K1 — Dashboard additive progress."""

    today_pct: float = 0.0
    week_pct: float = 0.0
    month_pct: float = 0.0
    overall_pct: float = 0.0
    journey_stage: JourneyStage = JourneyStage.NEW_USER
    onboarding_required: bool = True
    primary_exam_type: str | None = None
    days_remaining: int | None = None
    exam_date: date | None = None
    baseline_level: BaselineLevel = BaselineLevel.UNKNOWN
    # Sprint 18 — Assessment Progress (LOS §11)
    assessment_progress_pct: float = 0.0
    assessment_message: str | None = None


# ── Sprint-3.1.C — Subject Hub detail (sectioned, subject_code identity) ──


class SubjectHubIdentity(BaseModel):
    subject_code: str
    subject_name: str
    section: str | None = None
    exam_types: list[str] = Field(default_factory=list)
    is_active: bool = True
    source: str = "onboarding"


class SubjectHubProgress(BaseModel):
    progress_pct: float = 0.0
    accuracy: float = 0.0
    total_questions: int = 0
    study_minutes: int = 0
    last_studied_at: datetime | None = None
    last_revision_at: datetime | None = None


class SubjectHubToday(BaseModel):
    study_minutes: int = 0
    questions_solved: int = 0
    plan_count: int = 0
    completed_plan_count: int = 0


class SubjectHubRevision(BaseModel):
    due_today: int = 0
    overdue: int = 0
    due_this_week: int = 0
    next_title: str | None = None
    overview_reason: str | None = None
    available: bool = True


class SubjectHubPlans(BaseModel):
    today_count: int = 0
    completed_count: int = 0
    next_title: str | None = None
    overview_reason: str | None = None
    available: bool = True


class SubjectHubExamSummary(BaseModel):
    average_net: float | None = None
    exam_count: int = 0
    last_net: float | None = None
    available: bool = False
    placeholder: bool = True


class SubjectHubResources(BaseModel):
    count: int = 0
    recent_titles: list[str] = Field(default_factory=list)
    available: bool = False
    placeholder: bool = True


class SubjectHubFlashcards(BaseModel):
    enabled: bool = False
    placeholder: bool = True
    message: str = "Flashcards yakında"


class SubjectHubTopics(BaseModel):
    """Sprint-3.2.A — Topic list under Subject Hub (no detail yet)."""

    items: list[TopicCatalogRead] = Field(default_factory=list)
    count: int = 0
    available: bool = True


class SubjectHubAi(BaseModel):
    recommendation: str | None = None
    reason: str | None = None
    code: str | None = None
    explain_available: bool = False
    explain_placeholder: str = "Explain yakında (Sprint-3.1.D)"


class SubjectHubDetail(BaseModel):
    """Subject Hub SSOT response — future-proof sections."""

    subject: SubjectHubIdentity
    progress: SubjectHubProgress
    today: SubjectHubToday
    revision: SubjectHubRevision
    plans: SubjectHubPlans
    exam_summary: SubjectHubExamSummary
    resources: SubjectHubResources
    flashcards: SubjectHubFlashcards
    topics: SubjectHubTopics = Field(default_factory=SubjectHubTopics)
    ai: SubjectHubAi
    active_exam_type: str | None = None
    primary_exam_type: str | None = None
