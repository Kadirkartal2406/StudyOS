"""Reading / thinking time predictions from attempts + stem."""

from __future__ import annotations

from typing import Any

from app.services.question_virtual_student.types import StudentAttempt


def reading_analytics(
    question: dict[str, Any],
    attempts: list[StudentAttempt],
) -> dict[str, Any]:
    stem = str(question.get("stem") or "")
    words = max(1, len(stem.split()))
    if attempts:
        read = sum(a.reading_time_sec for a in attempts) / len(attempts)
        think = sum(a.thinking_time_sec for a in attempts) / len(attempts)
    else:
        read = (words / 160.0) * 60.0
        think = 10.0 + words * 0.05
    total = read + think
    return {
        "reading_time_prediction": round(read, 1),
        "thinking_time_prediction": round(think, 1),
        "total_solve_time": round(total, 1),
        "word_count": words,
        "high_reading_load": words >= 220 or read >= 55,
    }
