"""Phase 2 integrity gate — does not modify Phase 1 run_correctness_gate."""

from __future__ import annotations

from typing import Any

from app.services.correctness.asset_validation import check_required_asset
from app.services.correctness.choice_count import check_choice_count
from app.services.correctness.constants import INTEGRITY_VERSION
from app.services.correctness.ordering import check_ordering
from app.services.correctness.solution_consistency import check_solution_consistency
from app.services.correctness.solvability import check_solvability
from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
    CorrectnessResult,
    CorrectnessVerdict,
)


def run_integrity_gate(inp: CorrectnessInput) -> CorrectnessResult:
    """Phase 2 checks. FAIL → HARD REJECT. UNSUPPORTED → pass-through."""
    checks: list[CorrectnessCheck] = [
        check_solution_consistency(inp),
        check_solvability(inp),
        check_required_asset(inp),
        check_choice_count(inp),
        check_ordering(inp),
    ]
    fail = next((c for c in checks if c.status == "fail"), None)
    unsupported_only = fail is None and any(c.status == "unsupported" for c in checks)
    evidence: dict[str, Any] = {}
    for c in checks:
        if c.evidence:
            evidence[c.name] = c.evidence

    if fail is not None:
        return CorrectnessResult(
            verdict=CorrectnessVerdict.FAIL,
            passed=False,
            error_code=fail.error_code,
            reason=fail.message or fail.error_code,
            checks=checks,
            evidence=evidence,
            correctness_version=INTEGRITY_VERSION,
        )
    if unsupported_only:
        return CorrectnessResult(
            verdict=CorrectnessVerdict.UNSUPPORTED,
            passed=True,
            error_code=CorrectnessErrorCode.UNSUPPORTED_CORRECTNESS.value,
            reason="integrity:pass_through",
            checks=checks,
            evidence=evidence,
            correctness_version=INTEGRITY_VERSION,
        )
    return CorrectnessResult(
        verdict=CorrectnessVerdict.PASS,
        passed=True,
        error_code=None,
        reason=None,
        checks=checks,
        evidence=evidence,
        correctness_version=INTEGRITY_VERSION,
    )
