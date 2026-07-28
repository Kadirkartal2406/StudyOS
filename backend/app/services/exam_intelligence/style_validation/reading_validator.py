"""Reading profile internal consistency checks."""

from __future__ import annotations

from typing import Any

_LOAD_RANK = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
_COMPLEX_RANK = {"low": 1, "medium": 2, "high": 3}


def validate_reading(contract: dict[str, Any]) -> dict[str, Any]:
    topic = contract.get("topic_code")
    reading = contract.get("reading_load") or {}
    issues: list[str] = []
    warnings: list[str] = []

    required = (
        "paragraph_length",
        "sentence_count",
        "average_reading_time_sec",
        "information_density",
        "text_complexity",
    )
    for key in required:
        if key not in reading or reading.get(key) in (None, ""):
            issues.append(f"missing_reading_field:{key}")

    try:
        para = float(reading.get("paragraph_length") or 0)
        sent = float(reading.get("sentence_count") or 0)
        time_s = float(reading.get("average_reading_time_sec") or 0)
        density = float(reading.get("information_density") or 0)
    except (TypeError, ValueError):
        return {
            "topic_code": topic,
            "passed": False,
            "issues": ["non_numeric_reading_fields"],
            "warnings": [],
        }

    load = str(reading.get("load_band") or "medium")
    complexity = str(reading.get("text_complexity") or "medium")

    # Consistency: long paragraphs should not be labeled low complexity/load
    if para >= 100 and _LOAD_RANK.get(load, 2) <= 1:
        warnings.append("long_paragraph_but_low_load_band")
    if para >= 100 and _COMPLEX_RANK.get(complexity, 2) <= 1:
        warnings.append("long_paragraph_but_low_complexity")
    if para >= 80 and time_s > 0 and time_s < 10:
        warnings.append("long_text_but_very_short_reading_time")
    if para <= 15 and time_s >= 50:
        warnings.append("short_text_but_very_long_reading_time")
    if density > 0.7 and para < 20 and sent < 2:
        warnings.append("high_density_with_sparse_text")
    if density < 0.05 and para >= 120:
        warnings.append("low_density_with_long_paragraph")

    return {
        "topic_code": topic,
        "exam_code": contract.get("exam_code"),
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


def validate_reading_batch(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [validate_reading(c) for c in contracts]
    failed = [r for r in rows if not r["passed"]]
    warned = [r for r in rows if r.get("warnings")]
    return {
        "checked": len(rows),
        "failed": len(failed),
        "warned": len(warned),
        "passed": len(failed) == 0,
        "failures": failed[:30],
        "warnings": warned[:40],
    }
