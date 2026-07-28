"""Aggregate review scores."""

from __future__ import annotations

from typing import Any

from app.services.question_review.types import ReviewBreakdown, MIN_REVIEW_SCORE


def build_review_breakdown(
    *,
    clarity: dict[str, Any],
    fairness: dict[str, Any],
    language: dict[str, Any],
    exam_feeling: dict[str, Any],
    distractors: dict[str, Any],
    cognitive_load: dict[str, Any],
    answer_validity: dict[str, Any],
    uniqueness: int = 85,
) -> ReviewBreakdown:
    return ReviewBreakdown(
        clarity=int(clarity.get("score") or 0),
        fairness=int(fairness.get("score") or 0),
        language=int(language.get("score") or 0),
        exam_feeling=int(exam_feeling.get("score") or 0),
        distractors=int(distractors.get("score") or 0),
        uniqueness=max(0, min(100, int(uniqueness))),
        cognitive_load=int(cognitive_load.get("score") or 0),
        answer_validity=int(answer_validity.get("score") or 0),
    )


def passes_review(breakdown: ReviewBreakdown) -> bool:
    return breakdown.review_score >= MIN_REVIEW_SCORE
