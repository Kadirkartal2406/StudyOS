"""Unit tests for SoftMeasurementScorer — never hard REJECT."""

from __future__ import annotations

from app.services.ai.compact_generation_contract import (
    CompactGenerationContract,
    VisualInterfaceStub,
)
from app.services.ai.soft_measurement_scorer import score_against_contract


def _ready_contract(**kwargs) -> CompactGenerationContract:
    base = dict(
        contract_version="cgc_v1_phase4b",
        exam_unit="yks_tyt",
        family="yks",
        readiness="READY_FOR_STRESS_REVIEW",
        do_not_enforce=False,
        soft_stem_band={"low": 74.0, "high": 242.0, "source": "phase4b_cleaned"},
        visual=VisualInterfaceStub(status="optional"),
    )
    base.update(kwargs)
    return CompactGenerationContract(**base)


def test_ok_within_band():
    stem = " ".join(["kelime"] * 120)
    s = score_against_contract(stem=stem, choices=["a", "b"], contract=_ready_contract())
    assert s.status == "OK"
    assert s.distance == 0.0


def test_review_or_regen_outside_band():
    stem = "kısa"
    s = score_against_contract(stem=stem, choices=["a"], contract=_ready_contract())
    assert s.status == "REVIEW_OR_REGEN"
    assert s.distance is not None and s.distance > 0.25


def test_unscored_when_no_contract():
    s = score_against_contract(stem="x", choices=None, contract=None)
    assert s.status == "UNSCORED"
    assert s.uncertainty is True


def test_unscored_do_not_enforce():
    c = _ready_contract(do_not_enforce=True, readiness="INSUFFICIENT_EVIDENCE")
    s = score_against_contract(stem="kısa", choices=[], contract=c)
    assert s.status == "UNSCORED"


def test_never_emits_reject():
    stem = ""
    s = score_against_contract(stem=stem, choices=[], contract=_ready_contract())
    assert s.status in {"OK", "REVIEW_OR_REGEN", "UNSCORED"}
    assert s.status != "REJECT"


def test_visual_required_does_not_claim_generator():
    c = _ready_contract(visual=VisualInterfaceStub(status="required", visual_spec=None))
    s = score_against_contract(stem=" ".join(["k"] * 100), choices=[], contract=c)
    assert c.visual.visual_spec is None
    assert s.visual_status == "required"
