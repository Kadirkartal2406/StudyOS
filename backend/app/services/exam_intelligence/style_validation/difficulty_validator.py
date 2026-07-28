"""Difficulty curve sanity — detect absurd jumps."""

from __future__ import annotations

from typing import Any

_BAND_RANK = {
    "easy": 1,
    "medium_easy": 2,
    "medium": 3,
    "hard": 4,
    "very_hard": 5,
}


def validate_difficulty_curve(contract: dict[str, Any]) -> dict[str, Any]:
    topic = contract.get("topic_code")
    curve = contract.get("difficulty_curve") or []
    issues: list[str] = []

    if not curve:
        # Aggregate-only contracts may lack curve; soft warn
        return {
            "topic_code": topic,
            "passed": True,
            "issues": [],
            "warnings": ["empty_difficulty_curve"],
            "max_jump": 0,
        }

    ranks: list[int] = []
    avgs: list[float] = []
    for seg in curve:
        if not isinstance(seg, dict):
            continue
        band = str(seg.get("band") or "")
        if band in _BAND_RANK:
            ranks.append(_BAND_RANK[band])
        if seg.get("difficulty_avg") is not None:
            try:
                avgs.append(float(seg["difficulty_avg"]))
            except (TypeError, ValueError):
                issues.append("non_numeric_difficulty_avg")

    max_jump = 0
    for i in range(1, len(ranks)):
        jump = abs(ranks[i] - ranks[i - 1])
        max_jump = max(max_jump, jump)
        # Jump of 4 bands (easy→very_hard) in one step is suspicious
        if jump >= 4:
            issues.append(f"abrupt_band_jump_segment_{i}:{ranks[i-1]}->{ranks[i]}")

    for i in range(1, len(avgs)):
        delta = abs(avgs[i] - avgs[i - 1])
        if delta >= 45:
            issues.append(f"abrupt_score_jump_segment_{i}:{round(delta,1)}")

    return {
        "topic_code": topic,
        "exam_code": contract.get("exam_code"),
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": [],
        "max_jump": max_jump,
        "segments": len(curve),
    }


def validate_difficulty_batch(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [validate_difficulty_curve(c) for c in contracts]
    failed = [r for r in rows if not r["passed"]]
    return {
        "checked": len(rows),
        "failed": len(failed),
        "passed": len(failed) == 0,
        "failures": failed[:40],
        "avg_max_jump": round(
            sum(r.get("max_jump") or 0 for r in rows) / max(len(rows), 1), 2
        ),
    }
