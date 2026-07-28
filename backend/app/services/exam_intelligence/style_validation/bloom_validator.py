"""Bloom distribution validator — sum ≈ 100%."""

from __future__ import annotations

from typing import Any

_BLOOM_KEYS = (
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
)


def validate_bloom(contract: dict[str, Any]) -> dict[str, Any]:
    topic = contract.get("topic_code")
    bloom = contract.get("bloom") or {}
    issues: list[str] = []
    warnings: list[str] = []

    if not isinstance(bloom, dict) or not bloom:
        return {
            "topic_code": topic,
            "passed": False,
            "issues": ["bloom_missing"],
            "warnings": [],
            "sum": 0.0,
        }

    missing = [k for k in _BLOOM_KEYS if k not in bloom]
    if missing:
        issues.append(f"bloom_missing_keys:{','.join(missing)}")

    try:
        total = sum(float(bloom.get(k) or 0) for k in _BLOOM_KEYS)
    except (TypeError, ValueError):
        return {
            "topic_code": topic,
            "passed": False,
            "issues": ["bloom_non_numeric"],
            "warnings": [],
            "sum": 0.0,
        }

    if abs(total - 1.0) > 0.08:
        issues.append(f"bloom_sum_out_of_range:{round(total, 3)}")

    # Abnormal: single level dominates > 85%
    try:
        peak = max(float(bloom.get(k) or 0) for k in _BLOOM_KEYS)
        if peak >= 0.85:
            warnings.append(f"bloom_over_concentrated:{round(peak, 3)}")
        create = float(bloom.get("create") or 0)
        if create >= 0.35:
            warnings.append("bloom_create_unusually_high_for_mcq")
    except (TypeError, ValueError):
        pass

    return {
        "topic_code": topic,
        "exam_code": contract.get("exam_code"),
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "sum": round(total, 3),
    }


def validate_bloom_batch(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [validate_bloom(c) for c in contracts]
    failed = [r for r in rows if not r["passed"]]
    warned = [r for r in rows if r.get("warnings")]
    return {
        "checked": len(rows),
        "failed": len(failed),
        "warned": len(warned),
        "passed": len(failed) == 0,
        "failures": failed[:30],
        "warnings": warned[:40],
        "avg_sum": round(sum(r.get("sum") or 0 for r in rows) / max(len(rows), 1), 3),
    }
