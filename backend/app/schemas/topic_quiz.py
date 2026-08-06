"""Sprint 14 — Topic Quiz Generation schemas + Quality Gate DTOs."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class QuizGenerateRequest(BaseModel):
    count: int = Field(default=5, ge=1, le=15)
    difficulty: str = Field(default="medium")  # easy|medium|hard
    exam_type: str | None = None

    @field_validator("difficulty")
    @classmethod
    def _diff(cls, v: str) -> str:
        allowed = {"easy", "medium", "hard"}
        v = (v or "medium").lower()
        if v not in allowed:
            raise ValueError("difficulty: easy|medium|hard")
        return v


class QuizItemRead(BaseModel):
    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]
    # correct_key submit öncesi istemciye GÖNDERİLMEZ (cheat önleme)
    explanation: str | None = None
    selected_key: str | None = None
    is_correct: bool | None = None

    model_config = {"from_attributes": True}


class QuizItemReview(BaseModel):
    """Submit sonrası inceleme — doğru anahtar açık."""

    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None = None
    selected_key: str | None = None
    is_correct: bool | None = None
    target_asset_id: str | None = None  # DB UUID or studyos:// asset URI
    correct_node_id: str | None = None


class QuizItemPublic(BaseModel):
    """Solve ekranı — doğru cevap gizli."""

    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]
    target_asset_id: str | None = None  # DB UUID or studyos:// asset URI


class QuizGenerationRead(BaseModel):
    id: uuid.UUID
    subject_code: str
    topic_code: str
    subject_name: str | None = None
    topic_name: str | None = None
    requested_count: int
    difficulty: str
    exam_type: str | None = None
    status: str
    provider: str | None = None
    valid_item_count: int = 0
    correct_count: int | None = None
    wrong_count: int | None = None
    blank_count: int | None = None
    error_message: str | None = None
    created_at: datetime
    items: list[QuizItemPublic] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class QuizAnswerItem(BaseModel):
    item_id: uuid.UUID
    selected_key: str | None = None  # None = boş
    selected_node_id: str | None = None  # EAE map selection

    @field_validator("selected_key")
    @classmethod
    def _key(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        v = v.upper()
        if v not in {"A", "B", "C", "D"}:
            raise ValueError("selected_key: A|B|C|D")
        return v


class QuizSubmitRequest(BaseModel):
    answers: list[QuizAnswerItem]


class QuizSubmitResult(BaseModel):
    generation: QuizGenerationRead
    correct_count: int
    wrong_count: int
    blank_count: int
    accuracy_pct: float
    review_items: list[QuizItemReview] = Field(default_factory=list)
