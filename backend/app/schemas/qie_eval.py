"""Sprint 25 — QIE human evaluation schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QieEvalCreate(BaseModel):
    question_ref_type: str = Field(description="assessment_question|topic_quiz_item")
    question_ref_id: uuid.UUID
    exam_feel: int = Field(ge=1, le=5)
    language: int = Field(ge=1, le=5)
    difficulty: int = Field(ge=1, le=5)
    option_quality: int = Field(ge=1, le=5)
    objective_fit: int = Field(ge=1, le=5)
    overall: int = Field(ge=1, le=5)
    notes: str | None = None
    stem_preview: str | None = None


class QieEvalRead(BaseModel):
    id: uuid.UUID
    question_ref_type: str
    question_ref_id: uuid.UUID
    exam_feel: int
    language: int
    difficulty: int
    option_quality: int
    objective_fit: int
    overall: int
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class QieEvalQueueItem(BaseModel):
    question_ref_type: str
    question_ref_id: uuid.UUID
    stem_preview: str
    choices: dict[str, str] = Field(default_factory=dict)
    qie_card: dict = Field(default_factory=dict)
    eae_interaction: dict | None = None
