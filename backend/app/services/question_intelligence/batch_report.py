"""P8 — Batch Quality Report generator."""
from __future__ import annotations
from typing import Any
from app.services.question_intelligence.types import BatchQualityReport, QuestionScorecard


def generate_batch_report(
    scorecards: list[QuestionScorecard],
    *,
    total_attempted: int = 0,
    rejected_count: int = 0,
    rewritten_count: int = 0,
    gemini_cost: float = 0.0,
    reject_reasons: dict[str, int] | None = None,
) -> BatchQualityReport:
    """Generate a quality report for a batch of questions."""
    accepted = len(scorecards)
    total = total_attempted or (accepted + rejected_count)
    
    if scorecards:
        avg_quality = sum(sc.overall for sc in scorecards) / len(scorecards)
        avg_blueprint = sum(sc.blueprint for sc in scorecards) / len(scorecards)
        avg_feel = sum(sc.exam_feel for sc in scorecards) / len(scorecards)
        avg_diff = sum(sc.difficulty for sc in scorecards) / len(scorecards)
    else:
        avg_quality = 0.0
        avg_blueprint = 0.0
        avg_feel = 0.0
        avg_diff = 0.0
    
    return BatchQualityReport(
        total=total,
        rejected=rejected_count,
        rewritten=rewritten_count,
        accepted=accepted,
        average_quality=round(avg_quality, 2),
        average_blueprint_match=round(avg_blueprint, 2),
        average_exam_feel=round(avg_feel, 2),
        average_difficulty=round(avg_diff, 2),
        gemini_cost=gemini_cost,
        reject_reasons=reject_reasons or {},
    )
