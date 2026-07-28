"""M27.5 Exam Style Learning — shared types (no question text)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


FORBIDDEN_FIELDS = frozenset(
    {
        "stem",
        "question_text",
        "choices",
        "options",
        "explanation",
        "answer_text",
        "passage",
        "transient_text",
        "_transient_text",
    }
)


@dataclass
class StyleContract:
    """Per-topic thinking contract for future Prompt Builder / QIE (codes only)."""

    exam_code: str
    subject_code: str
    topic_code: str
    subject_slug: str
    topic_slug: str
    sample_size: int = 0
    reading_load: dict[str, Any] = field(default_factory=dict)
    difficulty: dict[str, Any] = field(default_factory=dict)
    trap: dict[str, Any] = field(default_factory=dict)
    intent: dict[str, Any] = field(default_factory=dict)
    reasoning: dict[str, Any] = field(default_factory=dict)
    bloom: dict[str, float] = field(default_factory=dict)
    thinking_pattern: list[str] = field(default_factory=list)
    language_style: dict[str, Any] = field(default_factory=dict)
    expected_time_sec: float = 0.0
    option_balance: str = "unknown"
    vocabulary: dict[str, Any] = field(default_factory=dict)
    paragraph_ratio: float = 0.0
    expected_thinking: str = ""
    cluster: str | None = None
    difficulty_curve: list[dict[str, Any]] = field(default_factory=list)
    style_version: str = "m27_5_v1"
    source: str = "m27_5_style_learning"
    validation: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExamStyleProfile:
    """Exam-level aggregated learning profile."""

    exam_code: str
    reading_profile: dict[str, Any] = field(default_factory=dict)
    reasoning: dict[str, Any] = field(default_factory=dict)
    trap_patterns: dict[str, Any] = field(default_factory=dict)
    bloom: dict[str, float] = field(default_factory=dict)
    difficulty_curve: list[dict[str, Any]] = field(default_factory=list)
    intents: dict[str, Any] = field(default_factory=dict)
    clusters: list[dict[str, Any]] = field(default_factory=list)
    topic_count: int = 0
    style_version: str = "m27_5_v1"
    source: str = "m27_5_style_learning"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
