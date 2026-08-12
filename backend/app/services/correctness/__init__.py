"""Shared correctness gate (Phase 1)."""

from app.services.correctness.apply import (
    attach_correctness_meta,
    evaluate_item_correctness,
    evaluate_pool_row_correctness,
    pool_row_can_skip_recheck,
    pool_row_is_quarantined,
)
from app.services.correctness.constants import (
    CORRECTNESS_CHECKS,
    CORRECTNESS_VERSION,
    INTEGRITY_CHECKS,
    INTEGRITY_VERSION,
    is_correctness_current,
    is_numeric_subject,
)
from app.services.correctness.gate import run_correctness_gate
from app.services.correctness.integrity_gate import run_integrity_gate
from app.services.correctness.types import (
    CorrectnessErrorCode,
    CorrectnessInput,
    CorrectnessResult,
    CorrectnessVerdict,
)

__all__ = [
    "CORRECTNESS_CHECKS",
    "CORRECTNESS_VERSION",
    "INTEGRITY_CHECKS",
    "INTEGRITY_VERSION",
    "CorrectnessErrorCode",
    "CorrectnessInput",
    "CorrectnessResult",
    "CorrectnessVerdict",
    "attach_correctness_meta",
    "evaluate_item_correctness",
    "evaluate_pool_row_correctness",
    "pool_row_can_skip_recheck",
    "pool_row_is_quarantined",
    "is_correctness_current",
    "is_numeric_subject",
    "run_correctness_gate",
    "run_integrity_gate",
]
