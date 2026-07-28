"""VSSE reject policy."""

from __future__ import annotations

from typing import Any


def evaluate_rejects(
    *,
    confusion: dict[str, Any],
    reading: dict[str, Any],
    cognitive: dict[str, Any],
    fairness: dict[str, Any],
    distractors: list[Any],
    question: dict[str, Any],
    difficulty: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    flags = set(confusion.get("flags") or [])

    if "two_plausible_answers" in flags or confusion.get("ambiguity_probability", 0) >= 0.65:
        reasons.append("multiple_interpretations")
    if "majority_same_wrong" in flags:
        reasons.append("two_plausible_answers")

    # Distractor imbalance: one wrong dominates attraction
    wrong = [d for d in distractors if getattr(d, "trap_type", "") != "correct"]
    if wrong:
        top = max(wrong, key=lambda d: d.attraction_score)
        if top.attraction_score >= 0.8:
            reasons.append("extremely_misleading_distractor")
        scores = [d.attraction_score for d in wrong]
        if max(scores) - min(scores) >= 0.55:
            reasons.append("distractor_imbalance")

    if reading.get("high_reading_load") or cognitive.get("very_high"):
        reasons.append("very_high_reading_load")

    # Too obvious: almost everyone correct + correct much more attractive
    dist = confusion.get("solve_distribution") or {}
    correct = str(question.get("correct_key") or "A").upper()
    n = sum(dist.values()) or 1
    if dist.get(correct, 0) / n >= 0.9:
        reasons.append("too_obvious_answer")

    if fairness.get("unfair_wording"):
        reasons.append("unfair_wording")

    stem = str(question.get("stem") or "").lower()
    if any(
        x in stem
        for x in (
            "yapay zeka",
            "stub",
            "lorem",
            "bu soruda dikkat edilirse",
            "bloom düzeyi",
            "ölçülen kazanım",
            "kelimelik resmi bir üslup",
        )
    ):
        reasons.append("artificial_sounding_language")

    choice_blob = " ".join(
        str(v) for v in (question.get("choices") or {}).values()
    ).lower()
    if "doğru yanıt" in choice_blob and "çeldirici" in choice_blob:
        reasons.append("artificial_sounding_language")

    # de-dupe
    seen: set[str] = set()
    out: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out
