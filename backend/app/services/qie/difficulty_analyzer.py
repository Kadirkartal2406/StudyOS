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
    if plan.difficulty < 55:
        style["difficulty"] = "easy"
    elif plan.difficulty >= 80:
        style["difficulty"] = "hard"
    style.setdefault("reasoning_type", plan.reasoning_type)
    result = analyze_question_difficulty(
        item, style=style, topic_name=plan.topic_name
    )
    # Align toward planned difficulty band
    if plan.difficulty >= 80 and result.score < MIN_DIFFICULTY_SCORE:
        return result
    if plan.difficulty < 55 and result.score > 85:
        # Too hard vs easy plan — penalty (not length alone)
        adj = max(0, result.score - 12)
        return DifficultyScore(
            score=adj,
            passed=adj >= MIN_DIFFICULTY_SCORE,
            reasons=list(result.reasons) + ["easier_than_plan_penalty"],
        )
    if plan.difficulty >= 80 and result.score < 55:
        # Too easy vs hard plan
        adj = min(100, result.score + 10)
        return DifficultyScore(
            score=adj,
            passed=adj >= MIN_DIFFICULTY_SCORE,
            reasons=list(result.reasons) + ["harder_than_plan_boost"],
        )
    return result
