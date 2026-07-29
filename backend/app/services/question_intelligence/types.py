"""M34 internal types."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

M34_VERSION = "m34_v1"
MIN_BLUEPRINT_SCORE = 85
MIN_SCORECARD_OVERALL = 80


@dataclass
class BlueprintMatchResult:
    """P0 — Real Exam Blueprint Match scoring."""
    paragraph_length: int = 0
    sentence_length: int = 0
    option_length: int = 0
    punctuation_style: int = 0
    reasoning_type: int = 0
    stem_style: int = 0
    distractor_family: int = 0
    cognitive_load: int = 0
    reading_duration: int = 0

    @property
    def score(self) -> int:
        parts = [self.paragraph_length, self.sentence_length, self.option_length,
                 self.punctuation_style, self.reasoning_type, self.stem_style,
                 self.distractor_family, self.cognitive_load, self.reading_duration]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["score"] = self.score
        return d


@dataclass
class ExamFeelV2Result:
    """P1 — AI language detector V2."""
    score: int = 100
    detected_phrases: list[str] = field(default_factory=list)
    passed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OptionBalanceResult:
    """P2 — Real Option Balance analysis."""
    length_balance: int = 0
    language_balance: int = 0
    obvious_correct: int = 0  # penalty score — high is good (no obvious)
    obvious_short: int = 0  # penalty score — high is good (no obvious short)
    structural_variety: int = 0
    repetition_score: int = 0  # high is good (no repetition)

    @property
    def score(self) -> int:
        parts = [self.length_balance, self.language_balance, self.obvious_correct,
                 self.obvious_short, self.structural_variety, self.repetition_score]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["score"] = self.score
        return d


@dataclass
class DistractorQualityV2Result:
    """P3 — Distractor quality with type classification."""
    types_detected: dict[str, str] = field(default_factory=dict)  # key -> type
    type_variety: int = 0
    plausibility: int = 0
    trap_effectiveness: int = 0

    @property
    def score(self) -> int:
        parts = [self.type_variety, self.plausibility, self.trap_effectiveness]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["score"] = self.score
        return d


DISTRACTOR_TYPES = [
    "yakin_anlam",          # close meaning
    "eksik_cikarim",        # incomplete inference
    "asiri_genelleme",      # overgeneralization
    "sebep_sonuc_hatasi",   # cause-effect error
    "kapsam_kaymasi",       # scope shift
    "kavram_karisikligi",   # concept confusion
]


@dataclass
class UniquenessResult:
    """P4 — Question uniqueness check."""
    is_unique: bool = True
    most_similar_stem: str | None = None
    similarity_score: float = 0.0  # 0-1, lower is more unique
    checked_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"is_unique": self.is_unique, "similarity_score": self.similarity_score,
                "checked_count": self.checked_count}


@dataclass
class MultiStageReviewResult:
    """P5 — Multi-stage exam review."""
    language: int = 0
    exam_feeling: int = 0
    difficulty: int = 0
    distractor: int = 0
    fairness: int = 0
    human_examiner: int = 0
    passed: bool = False
    failed_stage: str | None = None

    @property
    def score(self) -> int:
        parts = [self.language, self.exam_feeling, self.difficulty,
                 self.distractor, self.fairness, self.human_examiner]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["score"] = self.score
        return d


@dataclass
class QuestionScorecard:
    """P6 — Complete internal scorecard for a question."""
    style: int = 0
    difficulty: int = 0
    exam_feel: int = 0
    naturalness: int = 0
    reasoning: int = 0
    distractors: int = 0
    blueprint: int = 0
    language: int = 0
    fairness: int = 0
    virtual_student: int = 0

    @property
    def overall(self) -> int:
        parts = [self.style, self.difficulty, self.exam_feel, self.naturalness,
                 self.reasoning, self.distractors, self.blueprint, self.language,
                 self.fairness, self.virtual_student]
        return int(round(sum(parts) / max(len(parts), 1)))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["overall"] = self.overall
        return d


@dataclass
class BatchQualityReport:
    """P8 — Batch generation quality report."""
    total: int = 0
    rejected: int = 0
    rewritten: int = 0
    accepted: int = 0
    average_quality: float = 0.0
    average_blueprint_match: float = 0.0
    average_exam_feel: float = 0.0
    average_difficulty: float = 0.0
    gemini_cost: float = 0.0
    reject_reasons: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AutoRepairResult:
    """P9 — Auto repair result."""
    repaired: bool = False
    fields_fixed: list[str] = field(default_factory=list)
    original_scores: dict[str, int] = field(default_factory=dict)
    new_scores: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
