"""Topic Test Catalog schemas — published weekly tests."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TopicTestListItem(BaseModel):
    id: uuid.UUID
    week_id: str
    difficulty: str
    ordinal: int
    question_count: int
    status: str
    published_at: datetime | None = None
    title: str
    user_status: str | None = None  # not_started | in_progress | submitted
    accuracy_pct: float | None = None
    attempt_id: uuid.UUID | None = None


class TopicTestCatalogRead(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    subject_name: str | None = None
    topic_name: str | None = None
    tests: list[TopicTestListItem] = Field(default_factory=list)


class TopicTestItemPublic(BaseModel):
    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]


class TopicTestAttemptRead(BaseModel):
    attempt_id: uuid.UUID
    test_id: uuid.UUID
    week_id: str
    difficulty: str
    ordinal: int
    status: str
    question_count: int
    items: list[TopicTestItemPublic] = Field(default_factory=list)


class TopicTestAnswerIn(BaseModel):
    item_id: uuid.UUID
    selected_key: str | None = None

    @field_validator("selected_key")
    @classmethod
    def _key(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        v = v.strip().upper()
        if v not in {"A", "B", "C", "D", "E"}:
            raise ValueError("selected_key: A|B|C|D|E")
        return v


class TopicTestSubmitRequest(BaseModel):
    answers: list[TopicTestAnswerIn] = Field(default_factory=list)


class TopicTestReviewItem(BaseModel):
    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None = None
    selected_key: str | None = None
    is_correct: bool | None = None


class TopicTestSubmitResult(BaseModel):
    attempt_id: uuid.UUID
    test_id: uuid.UUID
    correct_count: int
    wrong_count: int
    blank_count: int
    accuracy_pct: float
    review_items: list[TopicTestReviewItem] = Field(default_factory=list)


class TopicTestReleaseRequest(BaseModel):
    exam: str
    subject_code: str
    topic_code: str
    week_id: str | None = None
    subject_name: str | None = None
    topic_name: str | None = None
    dry_run: bool = False
    fill_pool_if_short: bool = True
    assemble_only: bool = False


class TopicTestReleaseResult(BaseModel):
    week_id: str
    exam: str
    subject_code: str
    topic_code: str
    created: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)
    dry_run: bool = False
