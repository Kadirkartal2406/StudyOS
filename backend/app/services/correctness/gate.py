"""Shared correctness gate — deterministic FAIL or pass-through UNSUPPORTED."""

from __future__ import annotations

from typing import Any, Literal

from app.services.correctness.answer_verification import verify_answer_key
from app.services.correctness.constants import (
    CORRECTNESS_CHECKS,
    CORRECTNESS_VERSION,
    is_numeric_subject,
)
from app.services.correctness.explanation_consistency import check_explanation_consistency
from app.services.correctness.option_equivalence import find_equivalent_option_pairs
from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
    CorrectnessResult,
    CorrectnessVerdict,
)

GateMode = Literal["full", "serve", "equivalence_only"]


def _base_evidence() -> dict[str, Any]:
    return {
        "claimed_key": None,
        "solved_value": None,
        "matching_keys": [],
        "equivalent_pairs": [],
    }


def _check_option_equivalence(inp: CorrectnessInput) -> CorrectnessCheck:
    pairs = find_equivalent_option_pairs(inp.choices)
    evidence = _base_evidence()
    evidence["claimed_key"] = str(inp.correct_key or "").upper()
    evidence["equivalent_pairs"] = [
        {"a": a, "b": b, "layer": layer} for a, b, layer in pairs
    ]
    if pairs:
        detail = ",".join(f"{a}={b}" for a, b, _ in pairs)
        return CorrectnessCheck(
            name="option_equivalence",
            status="fail",
            error_code=CorrectnessErrorCode.EQUIVALENT_OPTIONS.value,
            message=f"equivalent_options:{detail}",
            evidence=evidence,
        )
    return CorrectnessCheck(
        name="option_equivalence",
        status="pass",
        evidence=evidence,
    )


def _check_answer_key(inp: CorrectnessInput) -> CorrectnessCheck:
    raw = verify_answer_key(inp)
    return CorrectnessCheck(
        name="answer_key",
        status=raw["status"],
        error_code=raw.get("error_code"),
        message=raw.get("message"),
        evidence=raw.get("evidence") or _base_evidence(),
    )


def run_correctness_gate(
    inp: CorrectnessInput,
    *,
    mode: GateMode = "full",
) -> CorrectnessResult:
    """Run Phase 1 correctness checks.

    FAIL → HARD REJECT.
    UNSUPPORTED (no FAIL) → PASS-THROUGH with verdict=unsupported.
    """
    checks: list[CorrectnessCheck] = []

    eq = _check_option_equivalence(inp)
    checks.append(eq)

    run_answer = mode in {"full", "serve"} and is_numeric_subject(
        inp.subject_code, inp.exam
    )
    if mode == "equivalence_only":
        run_answer = False

    if run_answer:
        checks.append(_check_answer_key(inp))
        checks.append(check_explanation_consistency(inp))
    elif "answer_key" in CORRECTNESS_CHECKS and mode != "equivalence_only":
        checks.append(
            CorrectnessCheck(
                name="answer_key",
                status="unsupported",
                error_code=CorrectnessErrorCode.UNSUPPORTED_CORRECTNESS.value,
                message="non_numeric_subject",
                evidence=_base_evidence(),
            )
        )
        if "explanation_consistency" in CORRECTNESS_CHECKS:
            checks.append(
                CorrectnessCheck(
                    name="explanation_consistency",
                    status="unsupported",
                    error_code=CorrectnessErrorCode.UNSUPPORTED_CORRECTNESS.value,
                    message="non_numeric_subject",
                    evidence={},
                )
            )

    fail = next((c for c in checks if c.status == "fail"), None)
    unsupported_only = fail is None and any(c.status == "unsupported" for c in checks)

    evidence = _base_evidence()
    evidence["claimed_key"] = str(inp.correct_key or "").upper()
    for c in checks:
        ev = c.evidence or {}
        if ev.get("equivalent_pairs"):
            evidence["equivalent_pairs"] = ev["equivalent_pairs"]
        if ev.get("solved_value") is not None:
            evidence["solved_value"] = ev["solved_value"]
        if ev.get("matching_keys"):
            evidence["matching_keys"] = ev["matching_keys"]

    if fail is not None:
        return CorrectnessResult(
            verdict=CorrectnessVerdict.FAIL,
            passed=False,
            error_code=fail.error_code,
            reason=fail.message or fail.error_code,
            checks=checks,
            evidence=evidence,
            correctness_version=CORRECTNESS_VERSION,
        )

    if unsupported_only:
        return CorrectnessResult(
            verdict=CorrectnessVerdict.UNSUPPORTED,
            passed=True,
            error_code=CorrectnessErrorCode.UNSUPPORTED_CORRECTNESS.value,
            reason="unsupported_correctness:pass_through",
            checks=checks,
            evidence=evidence,
            correctness_version=CORRECTNESS_VERSION,
        )

    return CorrectnessResult(
        verdict=CorrectnessVerdict.PASS,
        passed=True,
        error_code=None,
        reason=None,
        checks=checks,
        evidence=evidence,
        correctness_version=CORRECTNESS_VERSION,
    )
