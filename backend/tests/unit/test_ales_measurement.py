"""Verification tests for ALES official-exam measurement artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ALES_DIR = ROOT / "data" / "analysis" / "ales"


def _load(dir_path: Path, name: str):
    path = dir_path / name
    assert path.exists(), f"missing {path}"
    if name.endswith(".jsonl"):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ales_artifacts():
    return {
        "inventory": _load(ALES_DIR, "inventory.json"),
        "records": _load(ALES_DIR, "question_records.jsonl"),
        "aggregates": _load(ALES_DIR, "aggregates.json"),
        "feature_vectors": _load(ALES_DIR, "feature_vectors.json"),
        "cross_year": _load(ALES_DIR, "cross_year_comparison.json"),
        "cross_booklet": _load(ALES_DIR, "cross_booklet_comparison.json"),
        "verification": _load(ALES_DIR, "verification.json"),
    }


def test_ales_all_pdfs_opened(ales_artifacts):
    inv = ales_artifacts["inventory"]
    assert len(inv) == 6
    assert all(i["opened_and_analyzed"] for i in inv)
    assert {i["booklet"] for i in inv} == {"1", "2", "3"}
    assert {i["year"] for i in inv} == {2019, 2021}


def test_ales_section_totals_official(ales_artifacts):
    for item in ales_artifacts["inventory"]:
        assert item["extracted_question_count"] == 100
        sections = {s["section"]: s["question_count"] for s in item["section_summaries"]}
        assert sections == {"sayisal": 50, "sozel": 50}


def test_ales_records_no_stem_text(ales_artifacts):
    for r in ales_artifacts["records"]:
        assert "text" not in r or r.get("text") in (None, "")
        assert r.get("content_fingerprint")
        assert r["exam"] == "ales"
        assert r["booklet"] in {"1", "2", "3"}
        assert r["subject"] in {"sayisal", "sozel"}


def test_ales_subject_sum_matches_records(ales_artifacts):
    agg = ales_artifacts["aggregates"]["ales"]
    subject_sum = sum(v["count"] for v in agg["subject_distributions"]["overall"].values())
    assert subject_sum == len(ales_artifacts["records"]) == 600


def test_ales_uncertain_not_forced_away(ales_artifacts):
    uncertain = [r for r in ales_artifacts["records"] if r["topic"] == "uncertain"]
    assert len(uncertain) > 0
    assert len(uncertain) / len(ales_artifacts["records"]) >= 0.15


def test_ales_booklets_not_collapsed(ales_artifacts):
    fv = ales_artifacts["feature_vectors"]
    assert "ales_1" in fv and "ales_2" in fv and "ales_3" in fv
    xb = ales_artifacts["cross_booklet"]
    assert set(xb["booklet_metrics"]) == {"1", "2", "3"}


def test_ales_thresholds_none(ales_artifacts):
    for key in ("ales", "ales_1", "ales_sayisal_section"):
        fv = ales_artifacts["feature_vectors"][key]
        assert fv["generation_thresholds"] is None
        assert fv["feature_weights"] is None
        assert fv["qie_binding"] is None


def test_ales_measurement_model_import():
    from app.services.ai import exam_measurement_model as emm

    assert len(emm.KPSS_MEASUREMENT_MODELS) == 3
    assert len(emm.YKS_MEASUREMENT_MODELS) == 5
    assert "lgs" in emm.LGS_DGS_MEASUREMENT_MODELS
    assert "dgs" in emm.LGS_DGS_MEASUREMENT_MODELS
    assert emm.ALES_MEASUREMENT_MODEL["generation_thresholds"] is None
    assert emm.ALES_MEASUREMENT_MODEL["feature_weights"] is None
    assert emm.ALES_MEASUREMENT_MODEL["qie_binding"] is None
    assert set(emm.ALES_MEASUREMENT_MODELS) >= {
        "ales",
        "ales_1",
        "ales_2",
        "ales_3",
        "ales_sayisal",
        "ales_sozel",
    }
