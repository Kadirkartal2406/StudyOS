"""Confusion / ambiguity signals from virtual attempts."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.services.question_virtual_student.types import StudentAttempt


def analyze_confusion(
    attempts: list[StudentAttempt],
    *,
    correct_key: str,
    question: dict[str, Any] | None = None,
) -> dict[str, Any]:
    correct = str(correct_key).upper()
    dist = Counter(a.chosen_option.upper() for a in attempts)
    n = max(len(attempts), 1)
    correct_n = dist.get(correct, 0)
    # Most common wrong
    wrong_counts = {k: v for k, v in dist.items() if k != correct}
    top_wrong = max(wrong_counts.items(), key=lambda x: x[1]) if wrong_counts else (None, 0)
    top_wrong_key, top_wrong_n = top_wrong if top_wrong else (None, 0)

    confusion = 0.0
    if top_wrong_n >= max(2, int(0.4 * n)) and correct_n <= int(0.35 * n):
        confusion = 0.75 + 0.05 * (top_wrong_n / n)
    elif top_wrong_n >= 3:
        confusion = 0.45 + 0.2 * (top_wrong_n / n)
    else:
        confused = sum(1 for a in attempts if a.confused_at)
        confusion = confused / n

    # Pairwise option closeness heuristic
    ambiguity = 0.0
    choices = (question or {}).get("choices") or {}
    texts = [str(v).lower().split() for v in choices.values()]
    close_pairs = 0
    for i, a in enumerate(texts):
        sa = set(a)
        for b in texts[i + 1 :]:
            sb = set(b)
            if sa and sb and len(sa & sb) / max(len(sa | sb), 1) >= 0.5:
                close_pairs += 1
    if close_pairs:
        ambiguity = min(0.9, 0.25 * close_pairs)
    if top_wrong_n >= 4 and correct_n <= 2:
        ambiguity = max(ambiguity, 0.7)

    flags: list[str] = []
    if top_wrong_n >= 4 and correct_n <= max(1, n // 5):
        flags.append("majority_same_wrong")
    if ambiguity >= 0.55:
        flags.append("two_plausible_answers")

    return {
        "confusion_score": round(min(1.0, confusion), 3),
        "ambiguity_probability": round(min(1.0, ambiguity), 3),
        "solve_distribution": dict(dist),
        "top_wrong": top_wrong_key,
        "correct_count": correct_n,
        "flags": flags,
    }
