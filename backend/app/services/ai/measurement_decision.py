"""Combine quality outcome + soft measurement + mode → final_action (no hard measurement REJECT)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.services.ai.soft_measurement_scorer import SoftMeasurementScore
from app.services.ai_cost.measurement_flags import (
    measurement_max_regen,
    measurement_mode,
)


@dataclass
class MeasurementDecision:
    final_action: str
    # keep_candidate | reject_quality | shadow_log | regen | measurement_review_hold | noop
    allow_autopool: bool
    should_regen: bool
    measurement_status: str | None
    quality_status: str
    mode: str
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decide_measurement_action(
    *,
    quality_status: str,
    score: SoftMeasurementScore | None,
    mode: str | None = None,
    retry_count: int = 0,
    generation_id: str | None = None,
    exam_unit: str | None = None,
    subject: str | None = None,
    topic: str | None = None,
    contract_version: str | None = None,
    visual_status: str | None = None,
) -> MeasurementDecision:
    """Quality FAIL always wins. Measurement never emits hard REJECT."""
    m = (mode or measurement_mode()).strip().lower()
    if m in {"soft-review", "softreview", "soft"}:
        m = "soft_review"
    if m not in {"off", "shadow", "soft_review"}:
        m = "off"

    q = (quality_status or "UNSURE").strip().upper()
    if q in {"FAIL", "REJECT", "FAILED"}:
        q_norm = "FAIL"
    elif q in {"PASS", "KEEP", "OK"}:
        q_norm = "PASS"
    else:
        q_norm = "UNSURE"

    ms = (score.status if score else "UNSCORED").upper()
    dist = score.distance if score else None
    uncertainty = bool(score.uncertainty) if score else True
    vis = visual_status or (score.visual_status if score else None)

    provenance = {
        "generation_id": generation_id,
        "exam_unit": exam_unit,
        "subject": subject,
        "topic": topic,
        "contract_version": contract_version,
        "measurement_status": ms if m != "off" else None,
        "measurement_distance": dist if m != "off" else None,
        "quality_status": q_norm,
        "retry_count": retry_count,
        "measurement_uncertainty": uncertainty if m != "off" else None,
        "visual_status": vis if m != "off" else None,
        "mode": m,
    }

    # OFF: noop
    if m == "off":
        return MeasurementDecision(
            final_action="noop",
            allow_autopool=True,
            should_regen=False,
            measurement_status=None,
            quality_status=q_norm,
            mode=m,
            provenance={**provenance, "final_action": "noop"},
        )

    # Quality FAIL → REJECT (existing path); measurement does not override
    if q_norm == "FAIL":
        return MeasurementDecision(
            final_action="reject_quality",
            allow_autopool=False,
            should_regen=False,
            measurement_status=ms,
            quality_status=q_norm,
            mode=m,
            provenance={**provenance, "final_action": "reject_quality"},
        )

    # SHADOW: log only; autopool unchanged by measurement
    if m == "shadow":
        return MeasurementDecision(
            final_action="shadow_log",
            allow_autopool=True,
            should_regen=False,
            measurement_status=ms,
            quality_status=q_norm,
            mode=m,
            provenance={**provenance, "final_action": "shadow_log"},
        )

    # SOFT_REVIEW
    if ms == "REVIEW_OR_REGEN":
        max_regen = measurement_max_regen()
        if retry_count < max_regen:
            return MeasurementDecision(
                final_action="regen",
                allow_autopool=False,
                should_regen=True,
                measurement_status=ms,
                quality_status=q_norm,
                mode=m,
                provenance={**provenance, "final_action": "regen"},
            )
        return MeasurementDecision(
            final_action="measurement_review_hold",
            allow_autopool=False,
            should_regen=False,
            measurement_status=ms,
            quality_status=q_norm,
            mode=m,
            provenance={**provenance, "final_action": "measurement_review_hold"},
        )

    # OK or UNSCORED → keep candidate (+ uncertainty flag already in provenance)
    return MeasurementDecision(
        final_action="keep_candidate",
        allow_autopool=True,
        should_regen=False,
        measurement_status=ms,
        quality_status=q_norm,
        mode=m,
        provenance={**provenance, "final_action": "keep_candidate"},
    )
