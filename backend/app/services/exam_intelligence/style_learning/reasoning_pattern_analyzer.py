"""Reasoning pattern analyzer — heuristic from stats + exam DNA."""

from __future__ import annotations

from typing import Any


_REASONING_TYPES = (
    "tek_adim",
    "iki_adim",
    "cok_adim",
    "eleme",
    "karsilastirma",
    "hipotez",
    "neden_sonuc",
    "kosul_zinciri",
    "soyutlama",
    "analojik",
)


def analyze_reasoning(
    *,
    exam_code: str,
    skill_type: str | None = None,
    multi_step_ratio: float = 0.0,
    reasoning_avg: float = 0.0,
    difficulty_avg: float = 50.0,
    topic_slug: str | None = None,
    exam_dna: dict[str, Any] | None = None,
) -> dict[str, Any]:
    exam = (exam_code or "").lower()
    topic = (topic_slug or "").lower()
    dna = exam_dna or {}
    multi = float(multi_step_ratio or dna.get("multi_step_ratio") or 0.0)
    reasoning = float(reasoning_avg if reasoning_avg else dna.get("reasoning_ratio") or 0.0)
    diff = float(difficulty_avg)

    weights: dict[str, float] = {k: 0.05 for k in _REASONING_TYPES}

    if multi >= 0.35 or diff >= 70:
        weights["cok_adim"] += 0.35
        weights["kosul_zinciri"] += 0.15
    elif multi >= 0.15 or diff >= 55:
        weights["iki_adim"] += 0.3
    else:
        weights["tek_adim"] += 0.35

    if skill_type in ("inference", "reading_comprehension") or topic in (
        "paragraf",
        "reading",
    ):
        weights["eleme"] += 0.2
        weights["karsilastirma"] += 0.15
        weights["analojik"] += 0.1
        weights["soyutlama"] += 0.1

    if skill_type == "problem_solving" or topic in ("problemler", "hareket", "mol"):
        weights["neden_sonuc"] += 0.15
        weights["kosul_zinciri"] += 0.15
        weights["hipotez"] += 0.05

    if exam in ("ales", "dgs"):
        weights["karsilastirma"] += 0.1
        weights["soyutlama"] += 0.1
        weights["analojik"] += 0.08

    if exam in ("ydt", "yds", "yokdil"):
        weights["eleme"] += 0.15
        weights["analojik"] += 0.1

    # normalize
    total = sum(weights.values()) or 1.0
    distribution = {k: round(v / total, 3) for k, v in weights.items()}
    dominant = max(distribution.items(), key=lambda x: x[1])[0]
    patterns = [
        k
        for k, v in sorted(distribution.items(), key=lambda x: -x[1])
        if v >= 0.08
    ][:6]

    return {
        "dominant": dominant,
        "patterns": patterns,
        "distribution": distribution,
        "multi_step_ratio": round(multi, 3),
        "reasoning_intensity": round(min(1.0, reasoning + multi * 0.5), 3),
    }
