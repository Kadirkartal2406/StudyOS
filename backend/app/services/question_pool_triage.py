"""Question pool triage interface (no live mutate / batch API).

Provides KEEP|REVIEW|REJECT|QUARANTINE labels for offline or future tooling.
Does not call pool delete or bulk reclassify.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Protocol


class TriageAction(str, Enum):
    KEEP = "KEEP"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    QUARANTINE = "QUARANTINE"


@dataclass
class TriageResult:
    action: TriageAction
    reason: str
    question_id: str | None = None
    exam_unit: str | None = None
    measurement_status: str | None = None
    quality_status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["action"] = self.action.value
        return d


class PoolTriageProtocol(Protocol):
    """Interface only — implementations must not auto-mutate live pool."""

    def triage(self, item: dict[str, Any]) -> TriageResult: ...


@dataclass
class SoftMeasurementPoolTriage:
    """Maps soft measurement + quality signals → triage label (no DB writes)."""

    def triage(self, item: dict[str, Any]) -> TriageResult:
        q = str(item.get("quality_status") or "").upper()
        m = str(item.get("measurement_status") or "").upper()
        qid = item.get("question_id") or item.get("id")
        exam_unit = item.get("exam_unit")
        stem = str(item.get("stem") or "")

        if item.get("quarantine"):
            return TriageResult(
                action=TriageAction.QUARANTINE,
                reason=str(item.get("quarantine_reason") or "flagged"),
                question_id=str(qid) if qid else None,
                exam_unit=exam_unit,
                measurement_status=m or None,
                quality_status=q or None,
            )

        # Structural: truncated / empty stems from malformed exports
        if len(stem.strip()) < 25:
            return TriageResult(
                action=TriageAction.QUARANTINE,
                reason="stem_too_short_or_empty",
                question_id=str(qid) if qid else None,
                exam_unit=exam_unit,
                measurement_status=m or None,
                quality_status=q or None,
            )
        if not (item.get("exam") or exam_unit):
            return TriageResult(
                action=TriageAction.QUARANTINE,
                reason="missing_exam_identity",
                question_id=str(qid) if qid else None,
                exam_unit=exam_unit,
                measurement_status=m or None,
                quality_status=q or None,
            )

        if q in {"FAIL", "REJECT", "FAILED"}:
            return TriageResult(
                action=TriageAction.REJECT,
                reason="quality_fail",
                question_id=str(qid) if qid else None,
                exam_unit=exam_unit,
                measurement_status=m or None,
                quality_status=q,
            )
        if m == "REVIEW_OR_REGEN":
            return TriageResult(
                action=TriageAction.REVIEW,
                reason="measurement_review_or_regen",
                question_id=str(qid) if qid else None,
                exam_unit=exam_unit,
                measurement_status=m,
                quality_status=q or None,
            )
        if m == "UNSCORED" and item.get("measurement_uncertainty"):
            return TriageResult(
                action=TriageAction.REVIEW,
                reason="measurement_unscored_uncertain",
                question_id=str(qid) if qid else None,
                exam_unit=exam_unit,
                measurement_status=m,
                quality_status=q or None,
                metadata={"note": "do_not_auto_keep_high_uncertainty"},
            )
        return TriageResult(
            action=TriageAction.KEEP,
            reason="ok_or_pass",
            question_id=str(qid) if qid else None,
            exam_unit=exam_unit,
            measurement_status=m or None,
            quality_status=q or None,
        )
