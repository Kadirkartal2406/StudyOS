"""Catalog / identity / blueprint audit — distribution & wiring checks."""

from __future__ import annotations

from app.core.constants import PLANNER_FALLBACK_BY_EXAM, normalize_exam_code
from app.core.exam_identity import (
    canonicalize_exam_type,
    catalog_exam_and_branch,
    pool_exam_key,
)
from app.services.ai.exam_question_blueprint import get_exam_blueprint
from app.services.ai.subject_catalog_seed import codes_for_exam
from app.services.exam_catalog.seed import build_exam_intelligence_seed
from app.services.subject_net_targets import (
    exam_total_question_count,
    official_subject_question_count,
)
from app.services.trial_exam_scheduler import _ALL_EXAMS


def test_normalize_does_not_collapse_distinct_exams():
    assert normalize_exam_code("tyt") == "tyt"
    assert normalize_exam_code("ayt") == "ayt"
    assert normalize_exam_code("yks") == "yks"
    assert normalize_exam_code("yds") == "yds_ingilizce"
    assert normalize_exam_code("yokdil") == "yokdil_ingilizce"
    assert normalize_exam_code("ydt") == "ydt_ingilizce"
    assert normalize_exam_code("yds") != normalize_exam_code("yokdil")
    assert normalize_exam_code("ydt") != normalize_exam_code("yds")


def test_pool_keys_separate_kpss_variants():
    assert pool_exam_key("kpss", "lisans") == "kpss_lisans"
    assert pool_exam_key("kpss", "onlisans") == "kpss_onlisans"
    assert pool_exam_key("kpss", "ortaogretim") == "kpss_ortaogretim"
    assert len({pool_exam_key("kpss", b) for b in ("lisans", "onlisans", "ortaogretim")}) == 3


def test_catalog_routing_ydt_under_yks():
    assert catalog_exam_and_branch("ydt", "en") == ("yks", "en")
    assert catalog_exam_and_branch("ydt_ingilizce", None) == ("yks", "en")
    assert catalog_exam_and_branch("kpss_lisans", None) == ("kpss", "lisans")
    assert catalog_exam_and_branch("ayt_ea", None) == ("yks", "ea")


def test_blueprint_totals_official():
    assert get_exam_blueprint("kpss", "lisans").total_count == 120
    assert get_exam_blueprint("kpss_onlisans").total_count == 120
    assert get_exam_blueprint("tyt").total_count == 120
    assert get_exam_blueprint("ayt", "sayisal").total_count == 80
    assert get_exam_blueprint("ayt", "ea").total_count == 80
    assert get_exam_blueprint("ayt", "sozel").total_count == 80
    assert get_exam_blueprint("lgs").total_count == 90
    assert get_exam_blueprint("ags").total_count == 80
    assert get_exam_blueprint("ales", "sayisal").total_count == 50
    assert get_exam_blueprint("ales", "sozel").total_count == 50
    assert get_exam_blueprint("dgs", "sayisal").total_count == 60
    assert get_exam_blueprint("ydt", "en").total_count == 80
    assert get_exam_blueprint("yds", "en").total_count == 80
    assert get_exam_blueprint("yokdil", "en").total_count == 80


def test_ags_blueprint_is_turkce_matematik_not_eb():
    codes = [s.subject_code for s in get_exam_blueprint("ags").sections]
    assert codes == ["ags_turkce", "ags_matematik"]
    assert "ags_egitim_bilimleri" not in codes


def test_planner_fallback_no_duplicate_ags_and_correct_subjects():
    assert list(PLANNER_FALLBACK_BY_EXAM.keys()).count("ags") == 1
    assert PLANNER_FALLBACK_BY_EXAM["ags"] == ("Türkçe", "Matematik")
    for key in ("kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"):
        assert key in PLANNER_FALLBACK_BY_EXAM
    assert PLANNER_FALLBACK_BY_EXAM["dgs"] == ("Sayısal", "Sözel")


def test_seed_ags_subjects_match_official_parse():
    ags = next(e for e in build_exam_intelligence_seed() if e["code"] == "ags")
    pack = ags["packs"][0]
    codes = {s["code"] for s in pack["subjects"]}
    assert codes == {"ags_turkce", "ags_matematik"}


def test_codes_for_exam_granular_variants():
    assert codes_for_exam("kpss_lisans", None) == codes_for_exam("kpss", "lisans")
    assert "ayt_fizik" in codes_for_exam("ayt_sayisal", None)
    assert "ayt_edebiyat" in codes_for_exam("ayt_ea", None)
    assert codes_for_exam("yds_ingilizce", None) == {"yds_ingilizce"}
    assert codes_for_exam("yokdil", "en") == {"yokdil_ingilizce"}
    assert codes_for_exam("ags", None) == {"ags_turkce", "ags_matematik"}
    assert "ydt_ingilizce" in codes_for_exam("yks", "dil")


def test_subject_net_ags_and_english():
    assert official_subject_question_count(exam_type="ags", subject_name="Türkçe") == 40
    assert exam_total_question_count("ags") == 80
    assert exam_total_question_count("yds_ingilizce") == 80
    assert exam_total_question_count("ayt_sayisal") == 80
    assert exam_total_question_count("kpss_ortaogretim") == 120


def test_trial_scheduler_covers_canonical_set():
    keys = {(e, b) for e, b in _ALL_EXAMS}
    assert ("kpss", "lisans") in keys
    assert ("ayt", "sozel") in keys
    assert ("ydt", "en") in keys
    assert ("yds", "en") in keys
    assert ("yokdil", "fen") in keys
    assert ("lgs", "sayisal") in keys
    assert ("lgs", "sozel") in keys
    assert ("ags", None) in keys
    # Shared booklet exam string stays ydt; EI resolves via catalog_exam_and_branch
    assert catalog_exam_and_branch("ydt", "en") == ("yks", "en")
    assert get_exam_blueprint("ydt", "en").total_count == 80


def test_canonicalize_onboarding_parents():
    assert canonicalize_exam_type("kpss", "onlisans") == "kpss_onlisans"
    assert canonicalize_exam_type("yds", None) == "yds_ingilizce"
    assert canonicalize_exam_type("ayt", "ea") == "ayt_ea"
    assert canonicalize_exam_type("yks", "sayisal") == "yks"
