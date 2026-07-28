"""Style Contract model, assembly helpers, and validation."""

from __future__ import annotations

from typing import Any

from app.services.exam_intelligence.style_learning.types import (
    FORBIDDEN_FIELDS,
    StyleContract,
)

REQUIRED_TOP_FIELDS = (
    "exam_code",
    "subject_code",
    "topic_code",
    "reading_load",
    "difficulty",
    "trap",
    "intent",
    "reasoning",
    "bloom",
    "thinking_pattern",
    "language_style",
    "expected_time_sec",
    "option_balance",
)


def validate_contract(data: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    for key in REQUIRED_TOP_FIELDS:
        if key not in data or data[key] in (None, "", [], {}):
            issues.append(f"missing_or_empty:{key}")

    bloom = data.get("bloom") or {}
    if isinstance(bloom, dict) and bloom:
        total = sum(float(v) for v in bloom.values())
        if abs(total - 1.0) > 0.08:
            issues.append(f"bloom_sum_out_of_range:{round(total, 3)}")

    para_ratio = data.get("paragraph_ratio")
    if para_ratio is not None:
        try:
            pr = float(para_ratio)
            if pr < 0 or pr > 1.2:
                issues.append("paragraph_ratio_invalid")
        except (TypeError, ValueError):
            issues.append("paragraph_ratio_invalid")

    def _scan(obj: Any, path: str = "$") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).lower()
                if lk in FORBIDDEN_FIELDS or "stem" in lk:
                    issues.append(f"forbidden_field:{path}.{k}")
                _scan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _scan(v, f"{path}[{i}]")

    _scan(data)
    return {"passed": len(issues) == 0, "issues": issues}


def contract_to_safe_dict(contract: StyleContract) -> dict[str, Any]:
    data = contract.to_dict()
    data["validation"] = validate_contract(data)
    return data


def build_thinking_pattern(
    *,
    intent: dict[str, Any],
    reasoning: dict[str, Any],
    trap: dict[str, Any],
) -> list[str]:
    pattern: list[str] = []
    primary = intent.get("primary")
    if primary:
        pattern.append(f"intent:{primary}")
    dominant = reasoning.get("dominant")
    if dominant:
        pattern.append(f"reasoning:{dominant}")
    for t in (trap.get("primary") or [])[:2]:
        pattern.append(f"trap:{t}")
    for p in (reasoning.get("patterns") or [])[:2]:
        key = f"reasoning:{p}"
        if key not in pattern:
            pattern.append(key)
    return pattern


__all__ = [
    "StyleContract",
    "REQUIRED_TOP_FIELDS",
    "validate_contract",
    "contract_to_safe_dict",
    "build_thinking_pattern",
]
