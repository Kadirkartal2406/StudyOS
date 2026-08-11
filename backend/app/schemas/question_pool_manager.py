"""M33 — Admin API schemas for question pool manager."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class QuestionPoolFillRequest(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str = Field(default="medium", min_length=1, max_length=16)
    count: int = Field(ge=1, le=2000)
    dry_run: bool = False


class QuestionPoolFillMissingRequest(BaseModel):
    dry_run: bool = False


class QuestionPoolDeleteRequest(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str = Field(default="medium", min_length=1, max_length=16)
    dry_run: bool = False


class QuestionPoolRegenerateRequest(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str = Field(default="medium", min_length=1, max_length=16)
    count: int = Field(ge=1, le=2000)
    dry_run: bool = False


class QuestionPoolInventoryRow(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str

    current: int
    minimum: int
    target: int
    status: str

    quality: float | None = None
    average_difficulty: float | None = None
    last_generated: datetime | None = None

    # Display helpers (optional; backward compatible)
    exam_label: str | None = None
    subject_name: str | None = None
    topic_name: str | None = None


class QuestionPoolMetrics(BaseModel):
    total_questions: int
    healthy_topics: int
    low_topics: int
    empty_topics: int

    today_generated: int
    yesterday_generated: int
    weekly_generated: int

    gemini_calls_today: int
    cache_hit_pct: float | None = None
    average_quality: float | None = None
    average_difficulty: float | None = None
    estimated_ai_cost_today: float | None = None


# ── M34.5 Production Validation schemas ──────────────────────


class ProductionValidateRequest(BaseModel):
    """P10 — Generate 5 questions, do not save to pool."""

    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str = Field(default="medium", min_length=1, max_length=16)
    subject_name: str = ""
    topic_name: str = ""
    count: int = Field(default=5, ge=1, le=5)


class ProductionRunMissingRequest(BaseModel):
    """P2 — Only generate topics where current < minimum."""

    approval_mode: str = Field(default="auto", pattern="^(auto|manual)$")
    max_topics: int | None = Field(default=None, ge=1, le=100)


class ProductionGenerateTopicRequest(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str = Field(default="medium", min_length=1, max_length=16)
    count: int = Field(ge=1, le=200)
    approval_mode: str = Field(default="auto", pattern="^(auto|manual)$")
    save: bool = True
    subject_name: str = ""
    topic_name: str = ""


class ProductionApproveRequest(BaseModel):
    pending_id: str

