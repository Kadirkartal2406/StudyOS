"""Shared dataclasses for M27 parser — never store stem/choice text."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class QuestionMeta:
    """Per-question statistics only (no stem / options / explanation)."""

    number: int
    subject_code: str | None = None
    topic_code: str | None = None
    topic_confidence: float = 0.0
    page: int | None = None
    estimated_reading_length_words: int = 0
    estimated_reading_time_sec: int = 0
    estimated_difficulty: int = 50  # 0–100
    skill_type: str = "general"
    sentence_count: int = 0
    option_length_avg: float = 0.0
    symbol_count: int = 0
    equation_count: int = 0
    has_table: bool = False
    has_visual_hint: bool = False
    multi_step: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LayoutStats:
    paragraph_length_avg: float = 0.0
    sentence_count_avg: float = 0.0
    option_length_avg: float = 0.0
    page_layout: str = "unknown"
    table_usage_ratio: float = 0.0
    visual_usage_ratio: float = 0.0
    multi_step_ratio: float = 0.0
    words_per_page_avg: float = 0.0


@dataclass
class ParseResult:
    exam_code: str
    year: str | None
    language: str
    page_count: int
    question_count: int
    answer_key: dict[str, str] = field(default_factory=dict)
    duration_minutes: int | None = None
    booklet_type: str | None = None
    pack: str | None = None
    session_id: str | None = None
    source_pdf: str = ""
    subject_order: list[str] = field(default_factory=list)
    topic_order: list[str] = field(default_factory=list)
    subject_distribution: dict[str, int] = field(default_factory=dict)
    topic_distribution: dict[str, int] = field(default_factory=dict)
    skill_distribution: dict[str, float] = field(default_factory=dict)
    difficulty_estimation: dict[str, float] = field(default_factory=dict)
    reading_time_sec_avg: float = 0.0
    questions: list[QuestionMeta] = field(default_factory=list)
    layout: LayoutStats = field(default_factory=LayoutStats)
    validation: dict[str, Any] = field(default_factory=dict)
    report_lines: list[str] = field(default_factory=list)
    parser_version: str = "m27_v1"

    def metadata_dict(self) -> dict[str, Any]:
        """Telif-safe metadata JSON — no stems/choices."""
        return {
            "exam_code": self.exam_code,
            "pack": self.pack,
            "session_id": self.session_id or self.year,
            "year": self.year,
            "language": self.language,
            "source_pdf": self.source_pdf,
            "page_count": self.page_count,
            "question_count": self.question_count,
            "answer_key": dict(self.answer_key),
            "exam_duration_minutes": self.duration_minutes,
            "booklet_type": self.booklet_type,
            "subject_order": list(self.subject_order),
            "topic_order": list(self.topic_order),
            "subject_distribution": dict(self.subject_distribution),
            "topic_distribution": dict(self.topic_distribution),
            "skill_distribution": dict(self.skill_distribution),
            "difficulty_estimation": dict(self.difficulty_estimation),
            "reading_time_sec_avg": self.reading_time_sec_avg,
            "layout": asdict(self.layout),
            "questions": [q.to_dict() for q in self.questions],
            "validation": dict(self.validation),
            "parser_version": self.parser_version,
        }
