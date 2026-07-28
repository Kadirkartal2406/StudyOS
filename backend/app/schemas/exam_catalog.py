"""Exam Intelligence Catalog schemas (Sprint X)."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EiTopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exam_code: str
    pack_code: str
    subject_code: str
    code: str
    name: str
    display_order: int
    is_active: bool = True
    importance_score: float
    average_question_count: float
    question_range_min: int
    question_range_max: int
    difficulty_score: float
    estimated_study_minutes: int
    revision_cost: float
    assessment_weight: float
    knowledge_tags: list[Any] = Field(default_factory=list)
    aliases: list[Any] = Field(default_factory=list)
    source: str
    legacy_topic_code: str | None = None


class EiSubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exam_code: str
    pack_code: str
    code: str
    name: str
    display_order: int
    is_active: bool = True
    legacy_subject_code: str | None = None
    topics: list[EiTopicRead] = Field(default_factory=list)


class EiPackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    display_order: int
    is_active: bool = True
    branch_key: str | None = None
    parent_pack_id: uuid.UUID | None = None
    subjects: list[EiSubjectRead] = Field(default_factory=list)
    children: list[EiPackRead] = Field(default_factory=list)


class EiExamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    display_order: int
    is_active: bool = True
    source: str = "official"
    packs: list[EiPackRead] = Field(default_factory=list)


class EiExamSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    display_order: int
    is_active: bool = True
    source: str = "official"
    pack_count: int = 0


class EiImportanceItem(BaseModel):
    topic_code: str
    name: str
    subject_code: str
    pack_code: str
    importance_score: float
    average_question_count: float
    assessment_weight: float
    source: str


EiPackRead.model_rebuild()
