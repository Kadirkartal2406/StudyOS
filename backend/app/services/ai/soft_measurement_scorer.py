"""Soft measurement scorer — lightweight post-gen side-channel (never hard REJECT)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from app.services.ai.compact_generation_contract import CompactGenerationContract

_VISUAL_HINT = re.compile(
    r"\b(şekil|grafik|tablo|diyagram|figure|graph|table|diagram|görsel)\b",
    re.IGNORECASE,
)
_CALC_HINT = re.compile(
    r"(\d+\s*[+\-*/×÷=]|\bhesapla\b|\bkaç\b|\bsonuç\b|\btoplam\b|\boran\b)",
    re.IGNORECASE,
)


@dataclass
class SoftMeasurementScore:
    status: str  # OK | REVIEW_OR_REGEN | UNSCORED
    distance: float | None = None
    reasons: list[str] = field(default_factory=list)
    features: dict[str, Any] = field(default_factory=dict)
    uncertainty: bool = False
    visual_status: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _stem_word_count(stem: str) -> int:
    return len(re.findall(r"\S+", stem or ""))


def extract_lightweight_features(stem: str, choices: list[str] | None = None) -> dict[str, Any]:
    text = stem or ""
    choice_blob = " ".join(choices or [])
    return {
        "stem_word_count": _stem_word_count(text),
        "mentions_visual": bool(_VISUAL_HINT.search(text) or _VISUAL_HINT.search(choice_blob)),
        "likely_calculation": bool(_CALC_HINT.search(text)),
        "choice_count": len(choices or []),
    }


def score_against_contract(
    *,
    stem: str,
    choices: list[str] | None = None,
    contract: CompactGenerationContract | None,
) -> SoftMeasurementScore:
    """Distance vs soft bands. Never emits hard REJECT."""
    feats = extract_lightweight_features(stem, choices)

    if contract is None:
        return SoftMeasurementScore(
            status="UNSCORED",
            reasons=["no_contract"],
            features=feats,
            uncertainty=True,
        )

    if contract.do_not_enforce or contract.readiness in {
        "INSUFFICIENT_EVIDENCE",
        "MISSING_CALIBRATION",
        "NEEDS_REVIEW",
    }:
        return SoftMeasurementScore(
            status="UNSCORED",
            reasons=["do_not_enforce_or_weak_readiness"],
            features=feats,
            uncertainty=True,
            visual_status=contract.visual.status if contract.visual else None,
        )

    band = contract.soft_stem_band
    if not band or band.get("low") is None or band.get("high") is None:
        return SoftMeasurementScore(
            status="UNSCORED",
            reasons=["missing_stem_band"],
            features=feats,
            uncertainty=True,
            visual_status=contract.visual.status if contract.visual else None,
        )

    lo = float(band["low"])
    hi = float(band["high"])
    wc = float(feats["stem_word_count"])
    # Soft margin: outside band by >25% of band width → REVIEW_OR_REGEN
    width = max(hi - lo, 1.0)
    if wc < lo:
        dist = (lo - wc) / width
    elif wc > hi:
        dist = (wc - hi) / width
    else:
        dist = 0.0

    reasons: list[str] = []
    status = "OK"
    if dist > 0.25:
        status = "REVIEW_OR_REGEN"
        reasons.append(f"stem_word_count_outside_soft_band dist={dist:.3f}")
    else:
        reasons.append("stem_word_count_within_soft_band")

    # Visual: advisory only — mention without generator is not a hard fail
    vis = contract.visual
    visual_status = vis.status if vis else None
    if vis and vis.status == "forbidden" and feats["mentions_visual"]:
        reasons.append("visual_mention_while_forbidden_advisory")
        # bump to review only if already borderline, else keep advisory note
        if status == "OK" and dist > 0.1:
            status = "REVIEW_OR_REGEN"

    return SoftMeasurementScore(
        status=status,
        distance=round(dist, 4),
        reasons=reasons,
        features=feats,
        uncertainty=False,
        visual_status=visual_status,
    )
