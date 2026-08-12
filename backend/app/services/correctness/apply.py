"""Single integration helper — all production paths call run_correctness_gate()."""

from __future__ import annotations

import logging
from typing import Any, Literal

from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.correctness.gate import GateMode, run_correctness_gate
from app.services.correctness.types import (
    CorrectnessInput,
    CorrectnessResult,
    CorrectnessVerdict,
)
from app.services.qie.types import QuestionCard, QuestionPlan

logger = logging.getLogger("studyos.correctness")


def evaluate_item_correctness(
    item: ValidatedQuizItem | Any,
    plan: QuestionPlan | None,
    *,
    mode: GateMode = "full",
    exam: str | None = None,
    subject_code: str | None = None,
    log_pass: bool = True,
) -> CorrectnessResult:
    """Run the shared gate. Does not trust LLM verify output."""
    inp = CorrectnessInput(
        stem=str(getattr(item, "stem", "") or ""),
        choices=dict(getattr(item, "choices", None) or {}),
        correct_key=str(getattr(item, "correct_key", "") or "").upper(),
        explanation=getattr(item, "explanation", None),
        subject_code=subject_code or (plan.subject_code if plan else None),
        exam=exam or (plan.exam if plan else None),
        plan=plan,
        eae_interaction=getattr(item, "eae_interaction", None),
    )
    result = run_correctness_gate(inp, mode=mode)
    if result.passed and mode == "full":
        from app.services.correctness.integrity_gate import run_integrity_gate

        integ = run_integrity_gate(inp)
        result = _merge_phase1_phase2(result, integ)
    _log(
        result,
        topic=(plan.topic_code if plan else None) or inp.subject_code,
        log_pass=log_pass,
    )
    return result


def _merge_phase1_phase2(p1: CorrectnessResult, p2: CorrectnessResult) -> CorrectnessResult:
    """Phase 2 FAIL wins. Phase 2 UNSUPPORTED is pass-through (keep Phase 1 verdict)."""
    integrity_meta = {
        "version": p2.correctness_version,
        "verdict": p2.verdict.value,
        "passed": p2.passed,
        "error_code": p2.error_code,
        "reason": p2.reason,
        "checks": [
            {"name": c.name, "status": c.status, "error_code": c.error_code}
            for c in p2.checks
        ],
    }
    evidence = dict(p1.evidence or {})
    evidence["integrity"] = integrity_meta
    for k, v in (p2.evidence or {}).items():
        if k not in evidence:
            evidence[k] = v
    checks = list(p1.checks) + list(p2.checks)
    if not p2.passed:
        return CorrectnessResult(
            verdict=CorrectnessVerdict.FAIL,
            passed=False,
            error_code=p2.error_code,
            reason=p2.reason,
            checks=checks,
            evidence=evidence,
            correctness_version=p1.correctness_version,
        )
    return CorrectnessResult(
        verdict=p1.verdict,
        passed=p1.passed,
        error_code=p1.error_code,
        reason=p1.reason,
        checks=checks,
        evidence=evidence,
        correctness_version=p1.correctness_version,
    )


def evaluate_pool_row_correctness(row: Any, *, mode: Literal["serve"] = "serve") -> CorrectnessResult:
    inp = CorrectnessInput.from_pool_row(row)
    result = run_correctness_gate(inp, mode=mode)
    _log(result, topic=getattr(row, "topic_code", None))
    return result


def attach_correctness_meta(card: QuestionCard, result: CorrectnessResult) -> None:
    meta = result.to_metadata()
    integ = (result.evidence or {}).get("integrity")
    if isinstance(integ, dict):
        meta["integrity"] = integ
    card.correctness_meta = meta


def pool_row_can_skip_recheck(row: Any) -> bool:
    from app.services.correctness.constants import is_correctness_current

    qie = getattr(row, "qie_card", None) or {}
    corr = qie.get("correctness") if isinstance(qie, dict) else None
    if not isinstance(corr, dict):
        return False
    return is_correctness_current(corr.get("version")) and corr.get("verdict") == "pass"


def pool_row_is_quarantined(row: Any) -> bool:
    from app.services.correctness.constants import is_correctness_current

    qie = getattr(row, "qie_card", None) or {}
    corr = qie.get("correctness") if isinstance(qie, dict) else None
    if not isinstance(corr, dict):
        return False
    if corr.get("quarantined"):
        return True
    return is_correctness_current(corr.get("version")) and corr.get("verdict") == "fail"


def _log(
    result: CorrectnessResult, *, topic: str | None, log_pass: bool = True
) -> None:
    topic_s = topic or "-"
    if result.verdict == CorrectnessVerdict.FAIL:
        pairs = result.evidence.get("equivalent_pairs") or []
        keys = ",".join(
            f"{p.get('a')}/{p.get('b')}" for p in pairs if isinstance(p, dict)
        )
        logger.info(
            "[CORRECTNESS] REJECT code=%s topic=%s keys=%s",
            result.error_code,
            topic_s,
            keys or "-",
        )
        return
    if result.verdict == CorrectnessVerdict.UNSUPPORTED:
        logger.info(
            "[CORRECTNESS] UNSUPPORTED topic=%s reason=%s",
            topic_s,
            result.reason or "unsupported",
        )
        return
    if not log_pass:
        return
    logger.info(
        "[CORRECTNESS] PASS topic=%s version=%s",
        topic_s,
        result.correctness_version,
    )
