"""Contract field completeness validator (M27.6)."""

from __future__ import annotations

from typing import Any

REQUIRED_FIELDS = (
    "reading_load",
    "reasoning",
    "difficulty",
    "trap",
    "thinking_pattern",
    "expected_time_sec",
    "option_balance",
    "language_style",
    "bloom",
    "intent",
)

# Aliases accepted for expected_time
_TIME_KEYS = ("expected_time_sec", "expected_time")


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    topic = contract.get("topic_code") or "unknown"

    for field in REQUIRED_FIELDS:
        if field == "expected_time_sec":
            if not any(contract.get(k) not in (None, "", [], {}) for k in _TIME_KEYS):
                issues.append("missing_or_empty:expected_time")
            continue
        val = contract.get(field)
        if val in (None, "", [], {}):
            issues.append(f"missing_or_empty:{field}")

    # Nested sanity
    if isinstance(contract.get("reading_load"), dict) and not contract["reading_load"]:
        issues.append("empty:reading_load")
    if isinstance(contract.get("bloom"), dict) and len(contract["bloom"]) < 4:
        issues.append("bloom_incomplete")
    if isinstance(contract.get("thinking_pattern"), list) and len(contract["thinking_pattern"]) < 1:
        issues.append("thinking_pattern_empty")

    # Forbidden content
    blob = str(contract.keys())
    for bad in ("stem", "question_text", "choices", "explanation"):
        if bad in contract:
            issues.append(f"forbidden_field:{bad}")

    return {
        "topic_code": topic,
        "exam_code": contract.get("exam_code"),
        "passed": len(issues) == 0,
        "issues": issues,
    }
