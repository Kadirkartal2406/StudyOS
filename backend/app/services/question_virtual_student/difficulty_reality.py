"""Difficulty reality check vs author target."""

from __future__ import annotations

from typing import Any

from app.services.question_virtual_student.types import StudentAttempt


def difficulty_reality_check(
    attempts: list[StudentAttempt],
    *,
    author_difficulty: int | None = None,
) -> dict[str, Any]:
    n = max(len(attempts), 1)
    accuracy = sum(1 for a in attempts if a.correct) / n
    if accuracy >= 0.75:
        band = "easy"
        observed = 40
    elif accuracy >= 0.45:
        band = "medium"
        observed = 65
    else:
        band = "hard"
        observed = 85

    author = int(author_difficulty) if author_difficulty is not None else None
    gap = abs((author or observed) - observed) if author is not None else 0
    warn = bool(author is not None and gap >= 25)

    return {
        "observed_band": band,
        "observed_difficulty": observed,
        "author_difficulty": author,
        "accuracy": round(accuracy, 3),
        "gap": gap,
        "warning": warn,
        "message": (
            f"Author={author} vs observed={band}({observed})" if warn else "aligned"
        ),
    }
