"""Difficulty Analyzer wrapper for QIE — reuses Sprint 23 heuristics."""

from __future__ import annotations

from typing import Any

from app.services.ai.difficulty_analyzer import (
    DifficultyScore,
    analyze_question_difficulty,
)
from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.qie.types import MIN_DIFFICULTY_SCORE, QuestionPlan


def analyze_for_plan(
    item: ValidatedQuizItem,
    plan: QuestionPlan,
    *,
    style: dict[str, Any] | None = None,
) -> DifficultyScore:
    style = dict(style or {})
    style.setdefault(
        "paragraph_words",
        f"{max(40, plan.paragraph_length - 40)}-{plan.paragraph_length + 60}",
    )
    style.setdefault("difficulty", "high" if plan.difficulty >= 75 else "medium")
    style.setdefault("reasoning_type", plan.reasoning_type)
    result = analyze_question_difficulty(
        item, style=style, topic_name=plan.topic_name
    )
    # Align toward planned difficulty band
    if plan.difficulty >= 75 and result.score < MIN_DIFFICULTY_SCORE:
        return result
    if plan.difficulty < 50 and result.score > 95:
        # Too hard vs easy plan — slight penalty
        adj = max(0, result.score - 8)
        return DifficultyScore(
            score=adj,
            passed=adj >= MIN_DIFFICULTY_SCORE,
            reasons=list(result.reasons) + ["easier_than_plan_penalty"],
        )
    return result
