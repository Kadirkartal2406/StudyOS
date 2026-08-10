"""QIE shared types — Sprint 25."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


PROMPT_VERSION = "qie_v3"
PLAN_VERSION = "qie_plan_v1"
MIN_DIFFICULTY_SCORE = 70
MIN_QUALITY_SCORE = 85
MAX_REGENERATE = 2


@dataclass
class QuestionPlan:
    """Planner output — LLM must not override these fields."""

    exam: str
    subject_code: str
    subject_name: str
    topic_code: str
    topic_name: str
    skill: str
    subskill: str | None = None
    difficulty: int = 70  # 0–100
    bloom: str = "analyze"
    reasoning_type: str = "inference"
    paragraph_length: int = 180  # target words
    reading_time_sec: int = 75
    stem_type: str = "inference"
    option_length: str = "balanced"
    option_balance: str = "tight"
    distractor_pattern: str = "meaning_shift"
    target_time_sec: int = 90
    target_accuracy: float = 0.55
    forbidden_recent_patterns: list[str] = field(default_factory=list)
    choice_count: int = 5
    pack: str | None = None
    index: int = 0
    target_asset_id: str | None = None
    available_nodes: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exam": self.exam,
            "pack": self.pack,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "topic_code": self.topic_code,
            "topic_name": self.topic_name,
            "skill": self.skill,
            "subskill": self.subskill,
            "difficulty": self.difficulty,
            "bloom": self.bloom,
            "reasoning_type": self.reasoning_type,
            "paragraph_length": self.paragraph_length,
            "reading_time_sec": self.reading_time_sec,
            "stem_type": self.stem_type,
            "option_length": self.option_length,
            "option_balance": self.option_balance,
            "distractor_pattern": self.distractor_pattern,
            "target_time_sec": self.target_time_sec,
            "target_accuracy": self.target_accuracy,
            "forbidden_recent_patterns": list(self.forbidden_recent_patterns),
            "choice_count": self.choice_count,
            "index": self.index,
            "plan_version": PLAN_VERSION,
            "target_asset_id": self.target_asset_id,
            "available_nodes": self.available_nodes,
        }


@dataclass
class QualityBreakdown:
    style: int = 0
    difficulty: int = 0
    similarity: int = 0
    grammar: int = 0
    option_balance: int = 0
    distractor_quality: int = 0
    blueprint_match: int = 0
    reading_time: int = 0
    exam_feel: int = 0

    @property
    def total(self) -> int:
        parts = [
            self.style,
            self.difficulty,
            self.similarity,
            self.grammar,
            self.option_balance,
            self.distractor_quality,
            self.blueprint_match,
            self.reading_time,
            self.exam_feel,
        ]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, int]:
        return {
            "style": self.style,
            "difficulty": self.difficulty,
            "similarity": self.similarity,
            "grammar": self.grammar,
            "option_balance": self.option_balance,
            "distractor_quality": self.distractor_quality,
            "blueprint_match": self.blueprint_match,
            "reading_time": self.reading_time,
            "exam_feel": self.exam_feel,
            "total": self.total,
        }


@dataclass
class QuestionCard:
    """Internal explainable metadata — never shown to end users."""

    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None
    plan: QuestionPlan
    difficulty_score: int
    quality: QualityBreakdown
    style_score: int = 0
    prompt_version: str = PROMPT_VERSION
    plan_version: str = PLAN_VERSION
    question_version: str = "1"
    provider: str | None = None
    model: str | None = None
    target_asset_id: str | None = None
    correct_node_id: str | None = None
    eae_interaction: dict[str, Any] | None = None
    measurement_meta: dict[str, Any] | None = None

    def to_persist_dict(self) -> dict[str, Any]:
        return {
            "skill": self.plan.skill,
            "subskill": self.plan.subskill,
            "bloom": self.plan.bloom,
            "difficulty": self.plan.difficulty,
            "difficulty_score": self.difficulty_score,
            "reasoning_type": self.plan.reasoning_type,
            "stem_type": self.plan.stem_type,
            "distractor_pattern": self.plan.distractor_pattern,
            "target_time_sec": self.plan.target_time_sec,
            "target_accuracy": self.plan.target_accuracy,
            "style_score": self.style_score,
            "quality_score": self.quality.total,
            "quality": self.quality.to_dict(),
            "prompt_version": self.prompt_version,
            "plan_version": self.plan_version,
            "question_version": self.question_version,
            "provider": self.provider,
            "model": self.model,
            "target_asset_id": self.target_asset_id,
            "correct_node_id": self.correct_node_id,
            "eae_interaction": self.eae_interaction,
            "measurement_meta": self.measurement_meta,
        }


@dataclass
class GenerateContext:
    exam: str
    subject_code: str
    subject_name: str
    topic_code: str
    topic_name: str
    count: int = 5
    difficulty_band: str = "medium"  # easy|medium|hard
    user_id: Any = None
    preferred_provider: str | None = None
    preferred_model: str | None = None
    existing_stems: list[str] = field(default_factory=list)
    recent_skills: list[str] = field(default_factory=list)
    recent_patterns: list[str] = field(default_factory=list)
    plans: list[QuestionPlan] | None = None  # if pre-planned (calibration)
    choice_count: int | None = None
    style_override: dict[str, Any] | None = None
    early_accuracy: float | None = None  # 0–1 for adaptive
    kind: str = "topic_quiz"  # topic_quiz | daily_booklet | calibration
    pool_type: str = "general"
    api_key_override: str | None = None
    measurement_contract_block: str | None = None
