"""Unit tests — Exam Intelligence Catalog seed shape (Sprint X)."""

from __future__ import annotations

from app.services.exam_catalog.seed import build_exam_intelligence_seed


REQUIRED_EXAMS = {
    "yks",
    "kpss",
    "lgs",
    "dgs",
    "ales",
    "yds",
    "yokdil",
    "ags",
}


def test_seed_contains_all_exams() -> None:
    exams = {e["code"] for e in build_exam_intelligence_seed()}
    assert REQUIRED_EXAMS <= exams


def test_yks_has_tyt_ayt_tracks_and_ydt() -> None:
    yks = next(e for e in build_exam_intelligence_seed() if e["code"] == "yks")
    packs = {p["code"]: p for p in yks["packs"]}
    assert "tyt" in packs
    assert "ayt" in packs
    assert "ydt" in packs
    ayt_children = {c["code"] for c in packs["ayt"]["children"]}
    assert ayt_children == {"ayt_sayisal", "ayt_ea", "ayt_sozel"}
    child_branches = {
        c["code"]: c.get("branch_key") for c in packs["ayt"]["children"]
    }
    assert child_branches["ayt_sayisal"] == "sayisal"
    assert child_branches["ayt_ea"] == "ea"
    assert child_branches["ayt_sozel"] == "sozel"


def test_every_topic_has_metadata() -> None:
    for exam in build_exam_intelligence_seed():
        for pack in exam["packs"]:
            _assert_pack_topics(pack)


def _assert_pack_topics(pack: dict) -> None:
    for subj in pack.get("subjects") or []:
        assert subj["topics"], f"empty topics: {subj['code']}"
        for t in subj["topics"]:
            assert "importance_score" in t
            assert "average_question_count" in t
            assert "question_range_min" in t
            assert "question_range_max" in t
            assert "difficulty_score" in t
            assert "estimated_study_minutes" in t
            assert t["source"] in {"official", "estimated"}
            assert t["code"].startswith(subj["code"] + "__")
    for child in pack.get("children") or []:
        _assert_pack_topics(child)


def test_tyt_subject_coverage() -> None:
    yks = next(e for e in build_exam_intelligence_seed() if e["code"] == "yks")
    tyt = next(p for p in yks["packs"] if p["code"] == "tyt")
    codes = {s["code"] for s in tyt["subjects"]}
    assert {
        "tyt_turkce",
        "tyt_matematik",
        "tyt_geometri",
        "tyt_fizik",
        "tyt_kimya",
        "tyt_biyoloji",
        "tyt_tarih",
        "tyt_cografya",
        "tyt_felsefe",
        "tyt_din",
    } <= codes


def test_kpss_lisans_pack() -> None:
    kpss = next(e for e in build_exam_intelligence_seed() if e["code"] == "kpss")
    packs = {p["code"]: p for p in kpss["packs"]}
    assert "kpss_lisans" in packs
    subjects = {s["code"] for s in packs["kpss_lisans"]["subjects"]}
    assert {
        "kpss_turkce",
        "kpss_matematik",
        "kpss_tarih",
        "kpss_cografya",
        "kpss_vatandaslik",
        "kpss_guncel",
    } <= subjects
