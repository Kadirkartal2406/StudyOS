"""Style similarity between topic contracts (0–1)."""

from __future__ import annotations

from typing import Any


def _vec(contract: dict[str, Any]) -> dict[str, float]:
    reading = contract.get("reading_load") or {}
    reasoning = contract.get("reasoning") or {}
    bloom = contract.get("bloom") or {}
    difficulty = contract.get("difficulty") or {}
    load_map = {"low": 0.2, "medium": 0.5, "high": 0.75, "very_high": 1.0}
    return {
        "para": min(1.0, float(reading.get("paragraph_length") or 0) / 160.0),
        "read": min(1.0, float(reading.get("average_reading_time_sec") or 0) / 60.0),
        "load": load_map.get(str(reading.get("load_band")), 0.5),
        "reason": float(reasoning.get("reasoning_intensity") or 0.0),
        "diff": min(1.0, float(difficulty.get("avg") or 50) / 100.0),
        "analyze": float(bloom.get("analyze") or 0.0),
        "apply": float(bloom.get("apply") or 0.0),
        "understand": float(bloom.get("understand") or 0.0),
        "para_ratio": float(contract.get("paragraph_ratio") or 0.0),
    }


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a or []), set(b or [])
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(len(sa | sb), 1)


def style_similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    """Cosine-ish mix of numeric vectors + intent/trap overlap."""
    va, vb = _vec(a), _vec(b)
    keys = list(va.keys())
    dot = sum(va[k] * vb[k] for k in keys)
    na = sum(va[k] ** 2 for k in keys) ** 0.5
    nb = sum(vb[k] ** 2 for k in keys) ** 0.5
    cosine = (dot / (na * nb)) if na and nb else 0.0

    intent_a = (a.get("intent") or {}).get("intents") or []
    intent_b = (b.get("intent") or {}).get("intents") or []
    trap_a = (a.get("trap") or {}).get("patterns") or []
    trap_b = (b.get("trap") or {}).get("patterns") or []
    reason_a = (a.get("reasoning") or {}).get("patterns") or []
    reason_b = (b.get("reasoning") or {}).get("patterns") or []

    overlap = (
        _jaccard(intent_a, intent_b)
        + _jaccard(trap_a, trap_b)
        + _jaccard(reason_a, reason_b)
    ) / 3.0

    cluster_bonus = 0.05 if a.get("cluster") and a.get("cluster") == b.get("cluster") else 0.0
    score = 0.65 * cosine + 0.30 * overlap + cluster_bonus
    return round(max(0.0, min(1.0, score)), 3)
