"""
StudyOS — QuestionRecord Şemaları
Sprint-1.9 — CRUD + istatistik yanıtları
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.question_record import ExamType, QuestionDifficulty, QuestionSource


class QuestionRecordCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=100)
    topic: str | None = Field(default=None, max_length=200)
    question_count: int = Field(gt=0)
    correct_count: int = Field(default=0, ge=0)
    wrong_count: int = Field(default=0, ge=0)
    blank_count: int = Field(default=0, ge=0)
    duration_minutes: int = Field(default=0, ge=0)
    difficulty: QuestionDifficulty | None = None
    source: QuestionSource | None = None
    exam_type: ExamType | None = None
    note: str | None = Field(default=None, max_length=2000)
    study_plan_id: uuid.UUID | None = None
    study_session_id: uuid.UUID | None = None
    subject_code: str | None = Field(default=None, max_length=100)
    topic_code: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def _counts_match(self) -> "QuestionRecordCreate":
        total = self.correct_count + self.wrong_count + self.blank_count
        if total != self.question_count:
            raise ValueError(
                "correct_count + wrong_count + blank_count, question_count ile eşit olmalıdır"
            )
        return self


class QuestionRecordUpdate(BaseModel):
    subject: str | None = Field(default=None, min_length=1, max_length=100)
    topic: str | None = Field(default=None, max_length=200)
    question_count: int | None = Field(default=None, gt=0)
    correct_count: int | None = Field(default=None, ge=0)
    wrong_count: int | None = Field(default=None, ge=0)
    blank_count: int | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, ge=0)
    difficulty: QuestionDifficulty | None = None
    source: QuestionSource | None = None
    exam_type: ExamType | None = None
    note: str | None = Field(default=None, max_length=2000)
    study_plan_id: uuid.UUID | None = None
    study_session_id: uuid.UUID | None = None


class QuestionRecordRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_plan_id: uuid.UUID | None
    study_session_id: uuid.UUID | None
    subject: str
    topic: str | None
    subject_code: str | None = None
    topic_code: str | None = None
    question_count: int
    correct_count: int
    wrong_count: int
    blank_count: int
    duration_minutes: int
    difficulty: QuestionDifficulty | None
    source: QuestionSource | None
    exam_type: ExamType | None
    note: str | None
    net_score: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionStatisticsOverview(BaseModel):
    total_questions: int = 0
    today_questions: int = 0
    week_questions: int = 0
    month_questions: int = 0
    total_correct: int = 0
    total_wrong: int = 0
    total_blank: int = 0
    correct_rate: float = 0.0
    wrong_rate: float = 0.0
    total_net: float = 0.0
    total_duration_minutes: int = 0
    record_count: int = 0


class QuestionDailyBucket(BaseModel):
    date: str
    question_count: int
    correct_count: int
    wrong_count: int
    blank_count: int
    net_score: float
    duration_minutes: int


class QuestionDailyResponse(BaseModel):
    buckets: list[QuestionDailyBucket]
    total_questions: int = 0


class QuestionDistributionItem(BaseModel):
    name: str
    question_count: int
    correct_count: int
    wrong_count: int
    blank_count: int
    net_score: float
    duration_minutes: int
    correct_rate: float = 0.0


class QuestionDistributionResponse(BaseModel):
    items: list[QuestionDistributionItem]
    total_questions: int = 0
