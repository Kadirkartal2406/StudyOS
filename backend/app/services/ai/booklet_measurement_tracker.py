"""Booklet-level measurement quota tracker (stub).

Tracks subject/archetype/visual marginal quotas from the compact contract when
filling booklets. Does NOT compute mean item-distance booklet compliance.
Inactive when MEASUREMENT_MODE=off.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.ai.compact_generation_contract import CompactGenerationContract
from app.services.ai_cost.measurement_flags import measurement_enabled, measurement_mode


@dataclass
class BookletQuotaSnapshot:
    exam_unit: str | None = None
    subject_counts: dict[str, int] = field(default_factory=dict)
    archetype_counts: dict[str, int] = field(default_factory=dict)
    visual_counts: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "exam_unit": self.exam_unit,
            "subject_counts": dict(self.subject_counts),
            "archetype_counts": dict(self.archetype_counts),
            "visual_counts": dict(self.visual_counts),
            "notes": list(self.notes),
            "mode": measurement_mode(),
        }


class BookletMeasurementTracker:
    """Optional metadata tracker — no live booklet mutation."""

    def __init__(self, contract: CompactGenerationContract | None = None) -> None:
        self.contract = contract
        self.snapshot = BookletQuotaSnapshot(
            exam_unit=contract.exam_unit if contract else None,
            notes=["inactive"] if not measurement_enabled() else ["active_soft_quota_stub"],
        )

    @property
    def active(self) -> bool:
        return measurement_enabled() and self.contract is not None

    def record_item(
        self,
        *,
        subject: str | None = None,
        archetype: str | None = None,
        visual_used: bool | None = None,
    ) -> None:
        if not self.active:
            return
        if subject:
            self.snapshot.subject_counts[subject] = (
                self.snapshot.subject_counts.get(subject, 0) + 1
            )
        if archetype:
            self.snapshot.archetype_counts[archetype] = (
                self.snapshot.archetype_counts.get(archetype, 0) + 1
            )
        if visual_used is not None:
            key = "with_visual" if visual_used else "no_visual"
            self.snapshot.visual_counts[key] = self.snapshot.visual_counts.get(key, 0) + 1

    def quota_hints(self) -> dict[str, Any]:
        """Marginal hints only — never mean item-distance compliance."""
        if not self.active or not self.contract:
            return {"active": False}
        return {
            "active": True,
            "exam_unit": self.contract.exam_unit,
            "archetype_hint": self.contract.archetype_hint,
            "visual_policy": self.contract.visual.status if self.contract.visual else None,
            "note": "quota_margins_only_no_mean_distance",
            "snapshot": self.snapshot.to_dict(),
        }
