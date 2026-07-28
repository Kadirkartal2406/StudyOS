"""M31 Virtual Student Simulation Engine — types (internal only)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

VSSE_VERSION = "m31_v1"
MIN_VSSE_SCORE = 70
MAX_REVIEW_BOUNCE = 1


@dataclass
class StudentAttempt:
    profile: str
    chosen_option: str
    confidence: float
    reasoning: str
    reading_time_sec: float
    thinking_time_sec: float
    confused_at: str | None = None
    attractive_distractor: str | None = None
    correct: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DistractorAttraction:
    option: str
    attraction_score: float
    reason: str
    similarity_to_correct: float
    trap_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VSSEResult:
    passed: bool
    virtual_student_score: int
    attempts: list[StudentAttempt] = field(default_factory=list)
    solve_distribution: dict[str, int] = field(default_factory=dict)
    confusion_score: float = 0.0
    ambiguity_probability: float = 0.0
    reading_time_prediction: float = 0.0
    thinking_time_prediction: float = 0.0
    distractor_attraction: list[DistractorAttraction] = field(default_factory=list)
    cognitive_load: dict[str, Any] = field(default_factory=dict)
    fairness: dict[str, Any] = field(default_factory=dict)
    difficulty_reality: dict[str, Any] = field(default_factory=dict)
    reject_reasons: list[str] = field(default_factory=list)
    review_bounce_used: int = 0
    vsse_version: str = VSSE_VERSION

    def internal_metadata(self) -> dict[str, Any]:
        return {
            "student_profiles": [a.to_dict() for a in self.attempts],
            "confusion_score": self.confusion_score,
            "ambiguity_probability": self.ambiguity_probability,
            "reading_time_prediction": self.reading_time_prediction,
            "thinking_time_prediction": self.thinking_time_prediction,
            "distractor_attraction": [d.to_dict() for d in self.distractor_attraction],
            "solve_distribution": dict(self.solve_distribution),
            "virtual_student_score": self.virtual_student_score,
            "cognitive_load": dict(self.cognitive_load),
            "fairness": dict(self.fairness),
            "difficulty_reality": dict(self.difficulty_reality),
            "reject_reasons": list(self.reject_reasons),
            "passed": self.passed,
            "review_bounce_used": self.review_bounce_used,
            "vsse_version": self.vsse_version,
        }
