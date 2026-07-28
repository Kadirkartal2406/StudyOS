"""
StudyOS — StudySession Pydantic Şemaları
Sprint-1.5 + Sprint 22 (chronometer / break / today summary)
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.constants import (
    STUDY_SESSION_MAX_BREAK_MINUTES,
    STUDY_SESSION_MAX_DURATION_MINUTES,
    STUDY_SESSION_MIN_BREAK_MINUTES,
    STUDY_SESSION_MIN_DURATION_MINUTES,
)
from app.models.study_session import StudySessionStatus


class StudySessionStartRequest(BaseModel):
    """Yeni oturum: pomodoro (countdown) veya chronometer (count-up)."""

    mode: str = Field(default="pomodoro", description="pomodoro | chronometer")
    planned_duration_minutes: int | None = Field(
        default=None,
        ge=STUDY_SESSION_MIN_DURATION_MINUTES,
        le=STUDY_SESSION_MAX_DURATION_MINUTES,
    )
    break_duration_minutes: int = Field(
        default=0,
        ge=STUDY_SESSION_MIN_BREAK_MINUTES,
        le=STUDY_SESSION_MAX_BREAK_MINUTES,
    )
    study_plan_id: uuid.UUID | None = None
    subject_code: str | None = Field(default=None, max_length=100)
    topic_code: str | None = Field(default=None, max_length=200)


class StudySessionFinishRequest(BaseModel):
    completed_questions: int | None = Field(default=None, ge=0)
    completed_topics: int | None = Field(default=None, ge=0)


class StudySessionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_plan_id: uuid.UUID | None
    started_at: datetime
    ended_at: datetime | None
    planned_duration_minutes: int | None = None
    actual_duration_minutes: int
    break_duration_minutes: int
    actual_break_minutes: int = 0
    mode: str = "pomodoro"
    phase: str = "focus"
    completed_questions: int
    completed_topics: int
    status: StudySessionStatus
    subject_code: str | None = None
    topic_code: str | None = None
    break_started_at: datetime | None = None
    paused_at: datetime | None = None
    paused_seconds: int = 0
    created_at: datetime
    updated_at: datetime
    plan_title: str | None = None
    plan_subject: str | None = None
    # M25 — UI state machine projection (IDLE|STUDYING|BREAK|PAUSED|COMPLETED)
    engine_state: str = "IDLE"

    model_config = {"from_attributes": True}


class StudySessionStatistics(BaseModel):
    total_sessions: int
    completed_sessions: int
    total_focus_minutes: int
    total_questions: int
    total_topics: int
    average_session_minutes: float
    date_from: date | None = None
    date_to: date | None = None


class SubjectMinutesItem(BaseModel):
    subject_code: str
    subject_label: str
    focus_minutes: int
    planned_minutes: int = 0


class StudyTodaySummary(BaseModel):
    """Günlük uyum paneli — ders / plan / hedef / mola."""

    focus_minutes: int = 0
    break_minutes: int = 0
    planned_minutes: int = 0
    goal_minutes: int = 0
    plan_adherence_pct: float = 0.0
    goal_gap_minutes: int = 0
    completed_plan_count: int = 0
    total_plan_count: int = 0
    by_subject: list[SubjectMinutesItem] = Field(default_factory=list)
    hourly_minutes: list[int] = Field(default_factory=lambda: [0] * 24)
