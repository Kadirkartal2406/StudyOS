"""
StudyOS — Data-driven Achievement Rule Evaluator (U1)
LLM unlock üretmez. criteria JSONB ortak evaluator ile değerlendirilir.
"""

from __future__ import annotations

from typing import Any


def evaluate_criteria(criteria: dict[str, Any], metrics: dict[str, Any], *, event: str | None) -> bool:
    """
    criteria: {metric, op, value, events?}
    op: gte | eq | lte | contains
    """
    if not criteria:
        return False
    events = criteria.get("events")
    if events and event and event not in events:
        return False
    metric = criteria.get("metric")
    if not metric:
        return False
    op = str(criteria.get("op") or "gte")
    expected = criteria.get("value")
    actual = metrics.get(metric)
    if actual is None:
        return False
    if op == "contains":
        if isinstance(actual, (list, set, tuple)):
            return expected in actual
        return str(expected) in str(actual)
    try:
        a = float(actual)
        e = float(expected)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    if op == "gte":
        return a >= e
    if op == "lte":
        return a <= e
    if op == "eq":
        return a == e
    return False


def progress_values(criteria: dict[str, Any], metrics: dict[str, Any]) -> tuple[float, float]:
    """(current, target) for progress UI."""
    metric = criteria.get("metric")
    target = float(criteria.get("value") or 1)
    if not metric:
        return 0.0, target
    raw = metrics.get(metric, 0)
    try:
        current = float(raw)
    except (TypeError, ValueError):
        current = 1.0 if raw else 0.0
    return min(current, target), target


def build_reason(title: str, criteria: dict[str, Any], metrics: dict[str, Any]) -> str:
    metric = criteria.get("metric", "metric")
    value = criteria.get("value")
    actual = metrics.get(metric)
    return (
        f"«{title}» rozeti açıldı: {metric}={actual} "
        f"(hedef {criteria.get('op', 'gte')} {value})."
    )[:500]
