"""Correctness gate public types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from app.services.correctness.constants import CORRECTNESS_VERSION
from app.services.qie.types import QuestionCard, QuestionPlan


class CorrectnessVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNSUPPORTED = "unsupported"


class CorrectnessErrorCode(str, Enum):
    EQUIVALENT_OPTIONS = "equivalent_options"
    NO_CORRECT_OPTION = "no_correct_option"
    MULTIPLE_CORRECT_OPTIONS = "multiple_correct_options"
    ANSWER_KEY_MISMATCH = "answer_key_mismatch"
    UNSOLVABLE = "unsolvable"
    MISSING_REQUIRED_ASSET = "missing_required_asset"
    SOLUTION_STEM_MISMATCH = "solution_stem_mismatch"
    AMBIGUOUS_ORDERING = "ambiguous_ordering"
    INVALID_CHOICE_COUNT = "invalid_choice_count"
    UNSUPPORTED_SOLUTION_CONSISTENCY = "unsupported_solution_consistency"
    UNSUPPORTED_CORRECTNESS = "unsupported_correctness"


CheckStatus = Literal["pass", "fail", "unsupported"]


@dataclass
class CorrectnessCheck:
    name: str
    status: CheckStatus
    error_code: str | None = None
    message: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class CorrectnessResult:
    verdict: CorrectnessVerdict
    passed: bool
    error_code: str | None
    reason: str | None
    checks: list[CorrectnessCheck]
    evidence: dict[str, Any]
    correctness_version: str = CORRECTNESS_VERSION

    def to_metadata(self) -> dict[str, Any]:
        """Persist under qie_card['correctness'] — no ORM column required."""
        from datetime import UTC, datetime

        return {
            "version": self.correctness_version,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "error_code": self.error_code,
            "reason": self.reason,
            "checked_at": datetime.now(UTC).isoformat(),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "error_code": c.error_code,
                }
                for c in self.checks
            ],
        }


@dataclass(frozen=True)
class CorrectnessInput:
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None = None
    subject_code: str | None = None
    exam: str | None = None
    plan: QuestionPlan | None = None
    eae_interaction: dict[str, Any] | None = None

    @classmethod
    def from_validated_item(cls, item: Any, plan: QuestionPlan | None = None) -> CorrectnessInput:
        return cls(
            stem=str(getattr(item, "stem", "") or ""),
            choices=dict(getattr(item, "choices", None) or {}),
            correct_key=str(getattr(item, "correct_key", "") or "").upper(),
            explanation=getattr(item, "explanation", None),
            subject_code=plan.subject_code if plan else None,
            exam=plan.exam if plan else None,
            plan=plan,
            eae_interaction=getattr(item, "eae_interaction", None),
        )

    @classmethod
    def from_question_card(cls, card: QuestionCard) -> CorrectnessInput:
        return cls(
            stem=card.stem,
            choices=dict(card.choices or {}),
            correct_key=str(card.correct_key or "").upper(),
            explanation=card.explanation,
            subject_code=card.plan.subject_code,
            exam=card.plan.exam,
            plan=card.plan,
            eae_interaction=card.eae_interaction,
        )

    @classmethod
    def from_pool_row(cls, row: Any) -> CorrectnessInput:
        qie = dict(getattr(row, "qie_card", None) or {})
        return cls(
            stem=str(getattr(row, "stem", "") or ""),
            choices=dict(getattr(row, "choices", None) or {}),
            correct_key=str(getattr(row, "correct_key", "") or "").upper(),
            explanation=getattr(row, "explanation", None),
            subject_code=str(getattr(row, "subject_code", "") or "") or None,
            exam=str(getattr(row, "exam", "") or "") or qie.get("exam"),
            eae_interaction=qie.get("eae_interaction") if isinstance(qie.get("eae_interaction"), dict) else None,
        )

    @classmethod
    def from_dict(
        cls,
        q: dict[str, Any],
        *,
        plan: QuestionPlan | dict[str, Any] | None = None,
        subject_code: str | None = None,
        exam: str | None = None,
    ) -> CorrectnessInput:
        plan_obj = plan if isinstance(plan, QuestionPlan) else None
        plan_d = plan if isinstance(plan, dict) else {}
        return cls(
            stem=str(q.get("stem") or ""),
            choices=dict(q.get("choices") or {}),
            correct_key=str(q.get("correct_key") or "").upper(),
            explanation=q.get("explanation"),
            subject_code=subject_code
            or (plan_obj.subject_code if plan_obj else None)
            or plan_d.get("subject_code"),
            exam=exam or (plan_obj.exam if plan_obj else None) or plan_d.get("exam"),
            plan=plan_obj,
            eae_interaction=q.get("eae_interaction") if isinstance(q.get("eae_interaction"), dict) else None,
        )
