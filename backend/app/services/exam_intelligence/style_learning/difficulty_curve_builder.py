"""Difficulty curve from ordered question metadata (no stems)."""

from __future__ import annotations

from typing import Any


def _band(score: float) -> str:
    if score < 40:
        return "easy"
    if score < 55:
        return "medium_easy"
    if score < 70:
        return "medium"
    if score < 85:
        return "hard"
    return "very_hard"


def build_difficulty_curve(
    questions: list[dict[str, Any]] | None = None,
    *,
    difficulty_estimation: dict[str, float] | None = None,
    buckets: int = 5,
) -> list[dict[str, Any]]:
    """
    Return ordered curve segments.
    Prefer per-question estimated_difficulty ordered by number.
    """
    qs = list(questions or [])
    qs = [q for q in qs if isinstance(q, dict)]
    qs.sort(key=lambda q: int(q.get("number") or 0))

    if qs:
        scores = [float(q.get("estimated_difficulty") or 50) for q in qs]
        n = len(scores)
        size = max(1, n // buckets)
        curve: list[dict[str, Any]] = []
        for i in range(buckets):
            start = i * size
            end = n if i == buckets - 1 else min(n, (i + 1) * size)
            if start >= n:
                break
            chunk = scores[start:end]
            avg = sum(chunk) / len(chunk)
            curve.append(
                {
                    "segment": i + 1,
                    "q_from": start + 1,
                    "q_to": end,
                    "difficulty_avg": round(avg, 1),
                    "band": _band(avg),
                }
            )
        return curve

    est = difficulty_estimation or {}
    # Synthetic classic ÖSYM-ish arc when only aggregates exist
    easy = float(est.get("easy") or 0.25)
    med = float(est.get("medium") or 0.45)
    hard = float(est.get("hard") or 0.3)
    return [
        {"segment": 1, "band": "easy", "weight": round(easy, 3), "difficulty_avg": 35.0},
        {"segment": 2, "band": "medium", "weight": round(med * 0.5, 3), "difficulty_avg": 55.0},
        {"segment": 3, "band": "hard", "weight": round(hard * 0.6, 3), "difficulty_avg": 72.0},
        {"segment": 4, "band": "very_hard", "weight": round(hard * 0.4, 3), "difficulty_avg": 85.0},
        {"segment": 5, "band": "medium", "weight": round(med * 0.5, 3), "difficulty_avg": 58.0},
    ]
