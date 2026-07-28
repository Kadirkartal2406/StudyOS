"""M30 Question Review AI — types (internal only)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

REVIEW_VERSION = "m30_v1"
MIN_REVIEW_SCORE = 90
MAX_REVIEW_REWRITE = 1


@dataclass
class ReviewBreakdown:
    clarity: int = 0
    fairness: int = 0
    language: int = 0
    exam_feeling: int = 0
    distractors: int = 0
    uniqueness: int = 0
    cognitive_load: int = 0
    answer_validity: int = 0

    @property
    def review_score(self) -> int:
        parts = [
            self.clarity,
            self.fairness,
            self.language,
            self.exam_feeling,
            self.distractors,
            self.uniqueness,
            self.cognitive_load,
            self.answer_validity,
        ]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, int]:
        d = asdict(self)
        d["review_score"] = self.review_score
        return d


@dataclass
class ReviewResult:
    passed: bool
    breakdown: ReviewBreakdown
    comments: list[str] = field(default_factory=list)
    rewrite_used: int = 0
    review_version: str = REVIEW_VERSION

    def internal_metadata(self) -> dict[str, Any]:
        b = self.breakdown
        return {
            "review_score": b.review_score,
            "clarity_score": b.clarity,
            "language_score": b.language,
            "fairness_score": b.fairness,
            "exam_feeling_score": b.exam_feeling,
            "answer_validity": b.answer_validity,
            "distractors_score": b.distractors,
            "uniqueness_score": b.uniqueness,
            "cognitive_load_score": b.cognitive_load,
            "review_comments": list(self.comments),
            "passed": self.passed,
            "rewrite_used": self.rewrite_used,
            "review_version": self.review_version,
        }
