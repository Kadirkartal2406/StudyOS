"""
StudyOS — Goal Pydantic Şemaları
Sprint-2.1 (Meeting-019) + Sprint-3.0.2 product types / explain
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.goal import GoalPeriod, GoalPriority, GoalStatus, GoalType
from app.models.question_record import ExamType
from app.services.goal_product_types import PRODUCT_GOAL_SPECS, ProductGoalType


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    # Teknik tip — product_goal_type verilirse sunucu eşler (geriye uyumluluk)
    goal_type: GoalType | None = None
    product_goal_type: ProductGoalType | None = None
    target_value: float = Field(gt=0)
    priority: GoalPriority = GoalPriority.MEDIUM
    period: GoalPeriod | None = None
    subject: str | None = Field(default=None, max_length=100)
    topic: str | None = Field(default=None, max_length=200)
    exam_type: ExamType | None = None
    start_date: date
    end_date: date
    metadata: dict | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title boş olamaz")
        return cleaned

    @model_validator(mode="after")
    def validate_dates_and_type(self) -> "GoalCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date, start_date'den önce olamaz")
        if self.product_goal_type is None and (self.goal_type is None or self.period is None):
            raise ValueError("goal_type + period veya product_goal_type zorunlu")
        if self.product_goal_type is not None:
            spec = PRODUCT_GOAL_SPECS[self.product_goal_type]
            if spec.requires_subject and not (self.subject and self.subject.strip()):
                raise ValueError("branş neti için subject zorunlu")
        elif self.goal_type == GoalType.SUBJECT and not (self.subject and self.subject.strip()):
            raise ValueError("subject goal için subject zorunlu")
        elif self.goal_type == GoalType.TOPIC and not (self.topic and self.topic.strip()):
            raise ValueError("topic goal için topic zorunlu")
        return self


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    target_value: float | None = Field(default=None, gt=0)
    priority: GoalPriority | None = None
    status: GoalStatus | None = None
    subject: str | None = Field(default=None, max_length=100)
    topic: str | None = Field(default=None, max_length=200)
    exam_type: ExamType | None = None
    start_date: date | None = None
    end_date: date | None = None
    current_value: float | None = Field(default=None, ge=0)
    metadata: dict | None = None
    product_goal_type: ProductGoalType | None = None


class GoalProgressLogEntry(BaseModel):
    at: str
    source: str
    note: str | None = None
    delta: float | None = None
    value: float | None = None


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    goal_type: GoalType
    product_goal_type: ProductGoalType | None = None
    target_value: float
    current_value: float
    progress: float
    priority: GoalPriority
    period: GoalPeriod
    status: GoalStatus
    subject: str | None
    topic: str | None
    exam_type: ExamType | None = None
    start_date: date
    end_date: date
    completed_at: datetime | None
    metadata: dict = Field(default_factory=dict)
    milestones_reached: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    remaining: float = 0.0
    eta_days: float | None = None
    estimated_completion: str | None = None
    progress_sources: list[str] = Field(default_factory=list)
    progress_log: list[GoalProgressLogEntry] = Field(default_factory=list)
    why_created: str | None = None


class GoalProgressItem(BaseModel):
    id: UUID
    title: str
    goal_type: GoalType
    product_goal_type: ProductGoalType | None = None
    period: GoalPeriod
    progress: float
    current_value: float
    target_value: float
    remaining: float
    eta_days: float | None = None
    estimated_completion: str | None = None
    status: GoalStatus
    milestones_reached: list[str] = Field(default_factory=list)


class GoalProgressResponse(BaseModel):
    items: list[GoalProgressItem]
    active_count: int = 0
    completed_count: int = 0
    average_progress: float = 0.0


class WeeklyGoalSummaryItem(BaseModel):
    id: UUID
    title: str
    progress: float
    current_value: float = 0.0
    target_value: float = 0.0
    remaining: float
    eta_hint: str | None = None
    estimated_completion: str | None = None
    goal_type: GoalType
    product_goal_type: ProductGoalType | None = None
    status: GoalStatus


class GoalListResponse(BaseModel):
    items: list[GoalRead]


class GoalExplainResponse(BaseModel):
    goal_id: UUID
    explanation: str
    provider: str | None = None
    used_fallback: bool = False
    why_progressed: str
    why_stalled: str
    how_to_complete: str
    title: str
    progress: float
