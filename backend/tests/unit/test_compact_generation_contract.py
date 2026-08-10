"""Unit tests for CompactGenerationContract (Phase4B soft guidance)."""

from __future__ import annotations

from app.services.ai.compact_generation_contract import (
    build_compact_generation_contract,
    resolve_measurement_unit,
)


def test_resolve_measurement_unit_isolation():
    assert resolve_measurement_unit("tyt") == "yks_tyt"
    assert resolve_measurement_unit("ayt", "matematik") == "yks_ayt_sayisal"
    assert resolve_measurement_unit("ayt", "ayt_edebiyat") == "yks_ayt_ea"
    assert resolve_measurement_unit("ayt", "ayt_tarih_2") == "yks_ayt_sozel"
    assert resolve_measurement_unit("ayt", None) == "yks_ayt_ea"
    assert resolve_measurement_unit("ayt", "") != "yks_ayt_sayisal"
    assert resolve_measurement_unit("kpss") == "kpss_lisans"
    assert resolve_measurement_unit("lgs", "turkce") == "lgs_sozel"
    assert resolve_measurement_unit("yds") == "yds"
    assert resolve_measurement_unit("ales_sozel") == "ales_sozel"
    assert resolve_measurement_unit("yokdil_fen") == "yokdil_fen"


def test_build_contract_from_phase4b_tyt():
    c = build_compact_generation_contract(exam="tyt", subject_code="turkce")
    assert c is not None
    assert c.exam_unit == "yks_tyt"
    assert c.readiness == "READY_FOR_STRESS_REVIEW"
    assert c.do_not_enforce is False
    assert c.soft_stem_band is not None
    assert c.soft_stem_band["source"] == "phase4b_cleaned"
    assert c.soft_stem_band["low"] is not None
    assert c.soft_stem_band["high"] is not None
    # No Phase3B dirty bands
    assert "phase3b" not in str(c.soft_stem_band).lower()
    block = c.to_prompt_block()
    assert "MEASUREMENT SOFT CONTRACT" in block
    assert "hard reject" not in block.lower() or "not a hard reject" in block.lower()
    assert c.visual is not None
    assert c.visual.visual_spec is None


def test_yokdil_do_not_enforce():
    c = build_compact_generation_contract(exam="yokdil_fen")
    assert c is not None
    assert c.readiness == "INSUFFICIENT_EVIDENCE"
    assert c.do_not_enforce is True
    assert c.soft_stem_band is None
    assert "do NOT force" in c.to_prompt_block() or "advisory" in c.to_prompt_block().lower()


def test_dgs_needs_review_weak_soft():
    c = build_compact_generation_contract(exam="dgs_sayisal")
    assert c is not None
    assert c.readiness == "NEEDS_REVIEW"
    assert c.do_not_enforce is True


def test_exam_isolation_different_bands():
    tyt = build_compact_generation_contract(exam="tyt")
    ales = build_compact_generation_contract(exam="ales_sayisal")
    assert tyt and ales
    assert tyt.exam_unit != ales.exam_unit
    if tyt.soft_stem_band and ales.soft_stem_band:
        # bands may differ; at least units/calibration refs differ
        assert tyt.calibration_ref != ales.calibration_ref
