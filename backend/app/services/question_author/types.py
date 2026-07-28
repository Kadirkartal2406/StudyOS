"""M29 Question Author AI — internal types (not shown to end users)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

AUTHOR_VERSION = "m29_v1"
MAX_REWRITE = 2
MIN_STYLE = 85
MIN_DIFFICULTY = 70
MIN_DISTRACTOR = 80
MIN_EXAMINER = 85


@dataclass
class AuthorPlan:
    """M29.1 — plan only; no question text yet."""

    measured_outcome: str
    reasoning_type: str
    distractor_type: str
    paragraph_length: int
    option_strategy: str
    bloom_level: str
    difficulty_target: int
    reading_duration_sec: int
    trap_type: str
    exam: str = ""
    subject_code: str = ""
    topic_code: str = ""
    topic_name: str = ""
    choice_count: int = 5
    style_contract: dict[str, Any] = field(default_factory=dict)
    qie_plan_index: int = 0
    calibration: bool = False
    forbidden_patterns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CriticScores:
    style: int = 0
    difficulty: int = 0
    option_quality: int = 0
    distractors: int = 0
    language: int = 0
    naturalness: int = 0
    exam_feeling: int = 0
    reasoning: int = 0

    @property
    def average(self) -> int:
        parts = [
            self.style,
            self.difficulty,
            self.option_quality,
            self.distractors,
            self.language,
            self.naturalness,
            self.exam_feeling,
            self.reasoning,
        ]
        return int(round(sum(parts) / max(len(parts), 1)))

    def needs_rewrite(self) -> bool:
        return (
            self.style < MIN_STYLE
            or self.difficulty < MIN_DIFFICULTY
            or self.distractors < MIN_DISTRACTOR
        )

    def to_dict(self) -> dict[str, int]:
        d = asdict(self)
        d["average"] = self.average
        return d


@dataclass
class ExaminerVerdict:
    exam_ready: int = 0
    paragraph_natural: int = 0
    options_balanced: int = 0
    answer_not_guessable: int = 0
    distractors_strong: int = 0
    osym_feel: int = 0
    accepted: bool = False
    notes: str = ""

    @property
    def score(self) -> int:
        parts = [
            self.exam_ready,
            self.paragraph_natural,
            self.options_balanced,
            self.answer_not_guessable,
            self.distractors_strong,
            self.osym_feel,
        ]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, Any]:
        return {
            **{k: v for k, v in asdict(self).items()},
            "score": self.score,
        }


@dataclass
class AuthoredQuestion:
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None
    author_plan: AuthorPlan
    author_score: int = 0
    critic_score: int = 0
    critic: CriticScores = field(default_factory=CriticScores)
    rewrite_count: int = 0
    exam_feeling: int = 0
    style_score: int = 0
    difficulty_score: int = 0
    naturalness: int = 0
    reasoning_score: int = 0
    distractor_score: int = 0
    reading_time: int = 0
    ai_confidence: float = 0.0
    examiner: ExaminerVerdict = field(default_factory=ExaminerVerdict)
    provider: str | None = None
    model: str | None = None
    author_version: str = AUTHOR_VERSION
    rejected: bool = False
    reject_reason: str | None = None

    def internal_metadata(self) -> dict[str, Any]:
        """User-facing APIs must not expose this blob."""
        return {
            "author_score": self.author_score,
            "critic_score": self.critic_score,
            "critic": self.critic.to_dict(),
            "rewrite_count": self.rewrite_count,
            "exam_feeling": self.exam_feeling,
            "style_score": self.style_score,
            "difficulty_score": self.difficulty_score,
            "naturalness": self.naturalness,
            "reasoning_score": self.reasoning_score,
            "distractor_score": self.distractor_score,
            "reading_time": self.reading_time,
            "ai_confidence": self.ai_confidence,
            "examiner": self.examiner.to_dict(),
            "author_version": self.author_version,
            "rejected": self.rejected,
            "reject_reason": self.reject_reason,
            "author_plan": self.author_plan.to_dict(),
        }
