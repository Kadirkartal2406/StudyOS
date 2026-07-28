"""QuestionCard helpers."""

from __future__ import annotations

from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.qie.types import QuestionCard, QuestionPlan, QualityBreakdown


def build_card(
    item: ValidatedQuizItem,
    plan: QuestionPlan,
    *,
    difficulty_score: int,
    quality: QualityBreakdown,
    style_score: int = 0,
    provider: str | None = None,
    model: str | None = None,
) -> QuestionCard:
    return QuestionCard(
        stem=item.stem,
        choices=dict(item.choices),
        correct_key=item.correct_key,
        explanation=item.explanation,
        plan=plan,
        difficulty_score=difficulty_score,
        quality=quality,
        style_score=style_score or quality.style,
        provider=provider,
        model=model,
    )
