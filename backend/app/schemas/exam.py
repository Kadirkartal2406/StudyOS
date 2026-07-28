"""
StudyOS — Exam Pydantic şemaları
Sprint-2.6 (Meeting-024)
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator

from app.models.question_record import ExamType


class ExamResultCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    blank_count: int = Field(..., ge=0)
    question_count: int = Field(..., ge=1)
    duration_minutes: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _counts_match(self) -> "ExamResultCreate":
        total = self.correct_count + self.wrong_count + self.blank_count
        if total != self.question_count:
            raise ValueError("correct + wrong + blank == question_count olmalı")
        return self


class ExamResultRead(BaseModel):
    id: UUID
    exam_id: UUID
    subject: str
    correct_count: int
    wrong_count: int
    blank_count: int
    question_count: int
    net_score: Decimal
    duration_minutes: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("net_score")
    def _net(self, v: Decimal) -> float:
        return float(v)


class ExamCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    exam_type: ExamType
    exam_date: date
    duration_minutes: int = Field(default=0, ge=0)
    notes: str | None = None
    results: list[ExamResultCreate] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str) -> str:
        return v.strip()


class ExamUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    exam_type: ExamType | None = None
    exam_date: date | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class ExamResultsReplace(BaseModel):
    """D1 — sonuçları toplu yenile."""

    results: list[ExamResultCreate] = Field(..., min_length=1)


class ExamRead(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    exam_type: ExamType
    exam_date: date
    duration_minutes: int
    notes: str | None
    total_net: Decimal = Decimal("0")
    total_questions: int = 0
    result_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("total_net")
    def _total_net(self, v: Decimal) -> float:
        return float(v)


class ExamDetailRead(ExamRead):
    results: list[ExamResultRead] = Field(default_factory=list)


class ExamListResponse(BaseModel):
    items: list[ExamRead]


class ExamWriteResponse(BaseModel):
    """Create/update yanıtı + J1 milestone kodları."""

    exam: ExamDetailRead
    milestones: list[str] = Field(default_factory=list)


class ExamStatistics(BaseModel):
    total_exams: int = 0
    last_exam_title: str | None = None
    last_exam_date: date | None = None
    last_exam_net: float = 0.0
    highest_net: float = 0.0
    lowest_net: float = 0.0
    average_net: float = 0.0
    week_exams: int = 0
    week_average_net: float = 0.0
    month_exams: int = 0
    month_average_net: float = 0.0
    by_subject: dict[str, float] = Field(default_factory=dict)


class ExamTrendPoint(BaseModel):
    exam_id: UUID
    title: str
    exam_date: date
    total_net: float
    exam_type: ExamType


class ExamSubjectTrend(BaseModel):
    subject: str
    average_net: float
    exam_count: int
    total_correct: int
    total_wrong: int
    total_blank: int
    # Sprint 22 — subject capacity (correct+wrong+blank); max theoretical net ≈ question_count
    question_count: int = 0
    max_net: float = 0.0
    net_ratio: float = 0.0


class ExamTrends(BaseModel):
    net_over_time: list[ExamTrendPoint] = Field(default_factory=list)
    by_subject: list[ExamSubjectTrend] = Field(default_factory=list)
    correct_wrong_blank: dict[str, int] = Field(default_factory=dict)


class DashboardExamSummary(BaseModel):
    last_exam_title: str | None = None
    last_exam_net: float | None = None
    last_exam_delta_net: float | None = None
    last_exam_date: date | None = None
    today_ai_exam_summary: str | None = None
