"""Bloom taxonomy distribution heuristics."""

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


def build_bloom_distribution(
    *,
    difficulty_avg: float = 50.0,
    skill_type: str | None = None,
    reasoning_avg: float = 0.0,
    multi_step_ratio: float = 0.0,
    exam_dna: dict[str, Any] | None = None,
) -> dict[str, float]:
    dna = exam_dna or {}
    if isinstance(dna.get("bloom_distribution"), dict) and all(
        k in dna["bloom_distribution"] for k in ("understand", "apply", "analyze")
    ):
        # Expand M27 DNA (4-ish) into full 6-level map
        base = dna["bloom_distribution"]
        raw = {
            "remember": 0.08,
            "understand": float(base.get("understand", 0.2)),
            "apply": float(base.get("apply", 0.3)),
            "analyze": float(base.get("analyze", 0.3)),
            "evaluate": float(base.get("evaluate", 0.1)),
            "create": 0.02,
        }
    else:
        diff = float(difficulty_avg)
        reasoning = float(reasoning_avg)
        multi = float(multi_step_ratio)
        raw = {
            "remember": 0.18 if (skill_type == "recall" or diff < 40) else 0.08,
            "understand": 0.28 if diff < 55 else 0.18,
            "apply": 0.32 if (skill_type == "problem_solving" or 45 <= diff < 70) else 0.22,
            "analyze": 0.22 + reasoning * 0.2 + multi * 0.15,
            "evaluate": 0.08 + (0.12 if diff >= 70 else 0.0),
            "create": 0.02 + (0.05 if multi >= 0.4 else 0.0),
        }

    if skill_type == "inference":
        raw["analyze"] += 0.08
        raw["understand"] += 0.05
        raw["remember"] *= 0.7
    if skill_type == "reading_comprehension":
        raw["understand"] += 0.1
        raw["analyze"] += 0.08

    total = sum(raw.values()) or 1.0
    return {k: round(raw.get(k, 0.0) / total, 3) for k in _BLOOM_KEYS}
