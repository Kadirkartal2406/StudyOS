"""Verification tests for YDS / YÖKDİL measurement artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
YDS_DIR = ROOT / "data" / "analysis" / "yds"
YOK_DIR = ROOT / "data" / "analysis" / "yokdil"


def _load(dir_path: Path, name: str):
    path = dir_path / name
    assert path.exists(), f"missing {path}"
    if name.endswith(".jsonl"):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def yds_artifacts():
    if not (YDS_DIR / "verification.json").exists():
        pytest.skip("YDS analysis artifacts not generated yet")
    return {
        "inventory": _load(YDS_DIR, "inventory.json"),
        "records": _load(YDS_DIR, "question_records.jsonl"),
        "aggregates": _load(YDS_DIR, "aggregates.json"),
        "feature_vectors": _load(YDS_DIR, "feature_vectors.json"),
        "verification": _load(YDS_DIR, "verification.json"),
    }


@pytest.fixture(scope="module")
def yokdil_artifacts():
    if not (YOK_DIR / "verification.json").exists():
        pytest.skip("YÖKDİL analysis artifacts not generated yet")
    return {
        "inventory": _load(YOK_DIR, "inventory.json"),
        "records": _load(YOK_DIR, "question_records.jsonl"),
        "aggregates": _load(YOK_DIR, "aggregates.json"),
        "feature_vectors": _load(YOK_DIR, "feature_vectors.json"),
        "cross_domain": _load(YOK_DIR, "cross_domain_comparison.json"),
        "verification": _load(YOK_DIR, "verification.json"),
    }


def test_yds_pdfs_opened(yds_artifacts):
    inv = yds_artifacts["inventory"]
    ver = yds_artifacts["verification"]
    assert len(inv) == 3
    assert all(i["opened_and_analyzed"] for i in inv)
    assert {i["year"] for i in inv} == {2020, 2021}
    assert all(not i.get("ocr_used") for i in inv)


def test_yds_eighty_questions_per_analyzed_pdf(yds_artifacts):
    ver = yds_artifacts["verification"]
    for item in yds_artifacts["inventory"]:
        assert item["extracted_question_count"] == 80
        assert item["parsing_successful"] is True
    assert ver["total_questions"] == 240


def test_yds_no_stem_text(yds_artifacts):
    for r in yds_artifacts["records"]:
        assert "text" not in r or r.get("text") in (None, "")
        assert r["exam"] == "yds"
        assert r["subject"] == "ingilizce"
        assert r.get("domain") is None


def test_yds_thresholds_none(yds_artifacts):
    fv = yds_artifacts["feature_vectors"]["yds"]
    assert fv["generation_thresholds"] is None
    assert fv["feature_weights"] is None
    assert fv["qie_binding"] is None


def test_yokdil_six_pdfs_three_domains(yokdil_artifacts):
    inv = yokdil_artifacts["inventory"]
    assert len(inv) == 3
    assert all(i["opened_and_analyzed"] for i in inv)
    assert {i["domain"] for i in inv} == {"fen", "saglik", "sosyal"}
    assert {i["year"] for i in inv} == {2021}


def test_yokdil_eighty_questions_per_pdf(yokdil_artifacts):
    for item in yokdil_artifacts["inventory"]:
        assert item["extracted_question_count"] == 80
        assert item["parsing_successful"] is True


def test_yokdil_domains_independent(yokdil_artifacts):
    recs = yokdil_artifacts["records"]
    for dom in ("fen", "saglik", "sosyal"):
        drecs = [r for r in recs if r["domain"] == dom]
        assert len(drecs) == 80  # 2021 only (2025 OCR excluded)
        assert all(r["domain"] == dom for r in drecs)


def test_yokdil_no_stem_text(yokdil_artifacts):
    for r in yokdil_artifacts["records"]:
        assert "text" not in r or r.get("text") in (None, "")
        assert r["exam"] == "yokdil"
        assert r["domain"] in {"fen", "saglik", "sosyal"}


def test_yokdil_cross_domain_present(yokdil_artifacts):
    xb = yokdil_artifacts["cross_domain"]
    assert set(xb["domain_metrics"]) == {"fen", "saglik", "sosyal"}


def test_yokdil_thresholds_none(yokdil_artifacts):
    for key in ("yokdil_fen", "yokdil_saglik", "yokdil_sosyal"):
        fv = yokdil_artifacts["feature_vectors"][key]
        assert fv["generation_thresholds"] is None
        assert fv["feature_weights"] is None
        assert fv["qie_binding"] is None


def test_measurement_models_import():
    from app.services.ai import exam_measurement_model as emm

    assert len(emm.KPSS_MEASUREMENT_MODELS) == 3
    assert len(emm.YKS_MEASUREMENT_MODELS) == 5
    assert hasattr(emm, "ALES_MEASUREMENT_MODEL")
    if not hasattr(emm, "YDS_MEASUREMENT_MODEL"):
        pytest.skip("YDS/YÖKDİL models not appended yet")
    assert emm.YDS_MEASUREMENT_MODEL["generation_thresholds"] is None
    assert emm.YOKDIL_FEN_MEASUREMENT_MODEL["feature_weights"] is None
    assert emm.YOKDIL_SAGLIK_MEASUREMENT_MODEL["qie_binding"] is None
    assert set(emm.YOKDIL_MEASUREMENT_MODELS) >= {"yokdil_fen", "yokdil_saglik", "yokdil_sosyal"}
