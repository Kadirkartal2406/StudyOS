"""Exam style contract: expected choice count from existing style seed."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
)


@lru_cache(maxsize=1)
def _seed_choice_counts() -> dict[str, int]:
    from app.services.exam_style.seed import build_exam_style_seed

    out: dict[str, int] = {}
    for row in build_exam_style_seed():
        code = str(row.get("exam_code") or "").strip().lower()
        try:
            n = int(row.get("choice_count") or 0)
        except (TypeError, ValueError):
            continue
        if code and n:
            out[code] = n
    return out


def expected_choice_count(exam: str | None) -> int | None:
    """Return the style-DNA choice count for an exam, or None if unknown."""
    code = (exam or "").strip().lower()
    if not code:
        return None
    mapping = _seed_choice_counts()
    if code in mapping:
        return mapping[code]
    for prefix in (
        "lgs",
        "tyt",
        "ayt",
        "kpss",
        "dgs",
        "ales",
        "yds",
        "yokdil",
        "yökdil",
        "ydt",
        "ags",
    ):
        if code == prefix or code.startswith(prefix + "_") or code.startswith(prefix):
            key = "yokdil" if prefix in {"yokdil", "yökdil"} else prefix
            if key in mapping:
                return mapping[key]
    return None


def check_choice_count(inp: CorrectnessInput) -> CorrectnessCheck:
    actual = len(inp.choices or {})
    expected = expected_choice_count(inp.exam)
    evidence: dict[str, Any] = {
        "actual": actual,
        "expected": expected,
        "exam": inp.exam,
    }
    if expected is None:
        return CorrectnessCheck(
            name="choice_count",
            status="unsupported",
            error_code=CorrectnessErrorCode.INVALID_CHOICE_COUNT.value,
            message="choice_count:unknown_exam",
            evidence=evidence,
        )
    if actual == expected:
        return CorrectnessCheck(name="choice_count", status="pass", evidence=evidence)
    return CorrectnessCheck(
        name="choice_count",
        status="fail",
        error_code=CorrectnessErrorCode.INVALID_CHOICE_COUNT.value,
        message=f"invalid_choice_count:expected_{expected}_got_{actual}",
        evidence=evidence,
    )
