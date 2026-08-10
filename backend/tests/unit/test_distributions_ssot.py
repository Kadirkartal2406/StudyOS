"""Distribution SSOT validation — subject quotas + topic evidence wiring."""

from __future__ import annotations

from app.services.ai.exam_question_blueprint import get_exam_blueprint
from app.services.ai.subject_catalog_seed import codes_for_exam
from app.services.exam_catalog.distributions import (
    EXAM_TOTALS,
    SUBJECT_QUOTAS,
    resolve_quota_key,
    topic_table_for,
)
from app.services.exam_catalog.seed import build_exam_intelligence_seed
from app.services.subject_net_targets import (
    exam_total_question_count,
    official_subject_question_count,
)
from app.services.trial_exam_scheduler import _ALL_EXAMS


def _sum_topic_avg(subjects: list[dict]) -> dict[str, float]:
    out: dict[str, float] = {}
    for s in subjects:
        out[s["code"]] = sum(float(t["average_question_count"] or 0) for t in s["topics"])
    return out


def test_subject_quotas_match_official_totals():
    assert EXAM_TOTALS["kpss_lisans"] == 120
    assert EXAM_TOTALS["tyt"] == 120
    assert EXAM_TOTALS["ayt_sayisal"] == 80
    assert EXAM_TOTALS["ayt_ea"] == 80
    assert EXAM_TOTALS["ayt_sozel"] == 80
    assert EXAM_TOTALS["ydt_ingilizce"] == 80
    assert EXAM_TOTALS["lgs_sayisal"] == 40
    assert EXAM_TOTALS["lgs_sozel"] == 50
    assert EXAM_TOTALS["lgs"] == 90
    assert EXAM_TOTALS["ags"] == 80
    assert EXAM_TOTALS["ales_sayisal"] == 50
    assert EXAM_TOTALS["dgs_sozel"] == 60
    assert EXAM_TOTALS["yds_ingilizce"] == 80
    assert EXAM_TOTALS["yokdil_fen"] == 80


def test_blueprint_uses_ssot_quotas():
    assert get_exam_blueprint("kpss", "lisans").total_count == 120
    assert get_exam_blueprint("lgs", "sayisal").total_count == 40
    assert get_exam_blueprint("lgs", "sozel").total_count == 50
    assert get_exam_blueprint("yokdil", "fen").total_count == 80
    assert get_exam_blueprint("yokdil", "sosyal").total_count == 80
    assert {s.subject_code for s in get_exam_blueprint("lgs", "sayisal").sections} == {
        "lgs_matematik",
        "lgs_fen",
    }


def test_kpss_variants_have_independent_topic_means():
    seed = build_exam_intelligence_seed()
    kpss = next(e for e in seed if e["code"] == "kpss")
    packs = {p["code"]: p for p in kpss["packs"]}
    lisans_par = next(
        t
        for t in packs["kpss_lisans"]["subjects"][0]["topics"]
        if t["code"].endswith("__paragraf")
    )
    orta_par = next(
        t
        for t in packs["kpss_ortaogretim"]["subjects"][0]["topics"]
        if t["code"].endswith("__paragraf")
    )
    assert lisans_par["source"] == "official"
    assert orta_par["source"] == "official"
    assert lisans_par["average_question_count"] != orta_par["average_question_count"]


def test_lgs_seed_split_and_uncertain_topics():
    seed = build_exam_intelligence_seed()
    lgs = next(e for e in seed if e["code"] == "lgs")
    packs = {p["branch_key"]: p for p in lgs["packs"]}
    assert set(packs) == {"sayisal", "sozel"}
    say_codes = {s["code"] for s in packs["sayisal"]["subjects"]}
    soz_codes = {s["code"] for s in packs["sozel"]["subjects"]}
    assert say_codes == {"lgs_matematik", "lgs_fen"}
    assert soz_codes == {"lgs_turkce", "lgs_inkilap", "lgs_din", "lgs_ingilizce"}
    mat_topics = {t["code"].split("__", 1)[1] for t in packs["sayisal"]["subjects"][0]["topics"]}
    assert "uncertain" in mat_topics
    assert "geometri" in mat_topics


def test_yokdil_fields_preserved():
    seed = build_exam_intelligence_seed()
    yok = next(e for e in seed if e["code"] == "yokdil")
    assert {p["branch_key"] for p in yok["packs"]} == {"fen", "saglik", "sosyal"}


def test_topic_avg_not_used_as_booklet_total():
    """Guard: EI topic avg sums may exceed/under quota; blueprint is authoritative."""
    table = topic_table_for("kpss_lisans")
    turkce_sum = sum(m["average_question_count"] for _, _, m in table["kpss_turkce"])
    # Fine topics + uncertain can be near 30 but must not redefine quota
    assert SUBJECT_QUOTAS["kpss_lisans"]["kpss_turkce"] == 30
    assert abs(turkce_sum - 30) < 8  # residual estimated fine topics allowed
    assert get_exam_blueprint("kpss_lisans").sections[0].count == 30


def test_codes_for_exam_lgs_branches():
    assert codes_for_exam("lgs", "sayisal") == {"lgs_matematik", "lgs_fen"}
    assert "lgs_turkce" in codes_for_exam("lgs", "sozel")
    assert "lgs_matematik" not in codes_for_exam("lgs", "sozel")


def test_trial_scheduler_lgs_and_yokdil():
    keys = set(_ALL_EXAMS)
    assert ("lgs", "sayisal") in keys
    assert ("lgs", "sozel") in keys
    assert ("lgs", None) not in keys
    assert ("yokdil", "fen") in keys
    assert ("yokdil", "saglik") in keys
    assert ("yokdil", "sosyal") in keys


def test_subject_net_from_ssot():
    assert official_subject_question_count(exam_type="ags", subject_name="Türkçe") == 40
    assert exam_total_question_count("lgs_sayisal") == 40
    assert exam_total_question_count("ayt_sozel") == 80
    assert resolve_quota_key("yokdil", "fen") == "yokdil_fen"


def test_no_negative_or_absurd_topic_counts():
    for exam in build_exam_intelligence_seed():
        for pack in exam["packs"]:
            stack = [pack]
            while stack:
                p = stack.pop()
                stack.extend(p.get("children") or [])
                for s in p.get("subjects") or []:
                    for t in s["topics"]:
                        avg = float(t["average_question_count"])
                        qmin = int(t["question_range_min"])
                        qmax = int(t["question_range_max"])
                        assert avg >= 0
                        assert qmin >= 0
                        assert qmax >= qmin
                        assert avg <= 80
                        assert t["source"] in {"official", "estimated"}
