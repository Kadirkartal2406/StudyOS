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
    target_asset_id = None
    correct_node_id = None
    if item.eae_interaction:
        target_asset_id = item.eae_interaction.get("target_asset_id")
        correct_node_id = item.eae_interaction.get("correct_node_id")

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
        target_asset_id=target_asset_id,
        correct_node_id=correct_node_id,
        eae_interaction=item.eae_interaction,
    )
