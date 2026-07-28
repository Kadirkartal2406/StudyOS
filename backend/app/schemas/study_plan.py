"""
StudyOS — StudyPlan Pydantic Şemaları
Bkz. docs/architecture/api-design.md §2.6
"""

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator

from app.models.study_plan import StudyPlanStatus


class _TimeRangeValidatorMixin(BaseModel):
    """Bitiş saati başlangıçtan büyük olmalı; ikisi de birlikte verilmeli veya hiç verilmemeli."""

    planned_start_time: time | None = None
    planned_end_time: time | None = None

    @model_validator(mode="after")
    def _validate_time_range(self) -> "_TimeRangeValidatorMixin":
        start, end = self.planned_start_time, self.planned_end_time
        if (start is None) != (end is None):
            raise ValueError(
                "planned_start_time ve planned_end_time birlikte verilmeli veya ikisi de boş olmalı"
            )
        if start is not None and end is not None and end <= start:
            raise ValueError("planned_end_time, planned_start_time'dan büyük olmalıdır")
        return self


class StudyPlanCreate(_TimeRangeValidatorMixin):
    title: str = Field(min_length=1, max_length=200)
    subject: str = Field(min_length=1, max_length=100)
    topic: str | None = Field(default=None, max_length=200)
    target_question_count: int = Field(gt=0)
    estimated_minutes: int = Field(gt=0)
    study_date: date
    order_index: int | None = Field(default=None, ge=0)


class StudyPlanUpdate(_TimeRangeValidatorMixin):
    title: str = Field(min_length=1, max_length=200)
    subject: str = Field(min_length=1, max_length=100)
    topic: str | None = Field(default=None, max_length=200)
    target_question_count: int = Field(gt=0)
    estimated_minutes: int = Field(gt=0)
    study_date: date
    order_index: int | None = Field(default=None, ge=0)


class StudyPlanCompleteRequest(BaseModel):
    """Plan tamamlanırken gerçekleşen ilerleme bilgisi; verilmezse hedefle aynı sayılır."""

    completed_question_count: int | None = Field(default=None, ge=0)
    completed_minutes: int | None = Field(default=None, ge=0)


class StudyPlanRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    subject: str
    topic: str | None
    target_question_count: int
    estimated_minutes: int
    planned_start_time: time | None
    planned_end_time: time | None
    status: StudyPlanStatus
    completed_question_count: int
    completed_minutes: int
    order_index: int
    study_date: date
    created_at: datetime
    updated_at: datetime
    source: str = "manual"
    planner_draft_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}
