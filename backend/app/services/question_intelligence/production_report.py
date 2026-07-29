"""P10 — Production Report for sprint completion."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
from app.services.question_intelligence.types import BatchQualityReport


@dataclass
class ProductionReport:
    """Sprint-end production readiness report."""
    total_batches: int = 0
    total_questions: int = 0
    reject_rate: float = 0.0
    rewrite_rate: float = 0.0
    blueprint_match_avg: float = 0.0
    exam_feel_avg: float = 0.0
    best_topic: str = ""
    weakest_topic: str = ""
    production_ready: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_production_report(
    batch_reports: list[BatchQualityReport],
    topic_scores: dict[str, float] | None = None,
) -> ProductionReport:
    """Aggregate batch reports into a production readiness report."""
    topic_scores = topic_scores or {}
    
    total_q = sum(br.total for br in batch_reports)
    total_rejected = sum(br.rejected for br in batch_reports)
    total_rewritten = sum(br.rewritten for br in batch_reports)
    total_accepted = sum(br.accepted for br in batch_reports)
    
    reject_rate = (total_rejected / max(total_q, 1)) * 100
    rewrite_rate = (total_rewritten / max(total_q, 1)) * 100
    
    bp_avgs = [br.average_blueprint_match for br in batch_reports if br.average_blueprint_match > 0]
    bp_avg = sum(bp_avgs) / len(bp_avgs) if bp_avgs else 0.0
    
    feel_avgs = [br.average_exam_feel for br in batch_reports if br.average_exam_feel > 0]
    feel_avg = sum(feel_avgs) / len(feel_avgs) if feel_avgs else 0.0
    
    best_topic = max(topic_scores, key=topic_scores.get, default="") if topic_scores else ""
    weakest_topic = min(topic_scores, key=topic_scores.get, default="") if topic_scores else ""
    
    # Production ready: reject < 30%, avg blueprint >= 80, avg feel > 75
    production_ready = (
        reject_rate < 30
        and bp_avg >= 80
        and feel_avg >= 75
        and total_accepted > 0
    )
    
    return ProductionReport(
        total_batches=len(batch_reports),
        total_questions=total_q,
        reject_rate=round(reject_rate, 2),
        rewrite_rate=round(rewrite_rate, 2),
        blueprint_match_avg=round(bp_avg, 2),
        exam_feel_avg=round(feel_avg, 2),
        best_topic=best_topic,
        weakest_topic=weakest_topic,
        production_ready=production_ready,
    )
