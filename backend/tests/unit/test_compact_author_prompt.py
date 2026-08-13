"""Compact author prompt — Domain/Skill/DifficultyContract for Soru Üret."""

from __future__ import annotations

import pytest

from app.services.ai.quiz_quality_gate import extract_json_payload
from app.services.ai_cost.compact_author import _messages
from app.services.qie.planner import (
    QuestionPlanner,
    band_for_difficulty_score,
    difficulty_contract_for_band,
)
from app.services.qie.skill_profiles import LANGUAGE_FORM_SKILLS
from app.services.qie.types import GenerateContext, QuestionPlan


def _plan(
    *,
    exam: str,
    subject_code: str,
    subject_name: str,
    topic_code: str,
    topic_name: str,
    difficulty_band: str = "medium",
    style: dict | None = None,
) -> QuestionPlan:
    ctx = GenerateContext(
        exam=exam,
        subject_code=subject_code,
        subject_name=subject_name,
        topic_code=topic_code,
        topic_name=topic_name,
        count=1,
        difficulty_band=difficulty_band,
    )
    return QuestionPlanner().plan_batch(
        ctx, style=style or {"choice_count": 5}
    )[0]


def _msgs(plan: QuestionPlan) -> tuple[str, str]:
    msgs = _messages(
        plan,
        {
            "measured_outcome": plan.skill,
            "paragraph_length": plan.paragraph_length,
            "difficulty_target": plan.difficulty,
        },
    )
    return msgs[0].content, msgs[1].content


def _user(plan: QuestionPlan) -> str:
    return _msgs(plan)[1]


def _assert_no_language_leak(plan: QuestionPlan, user: str) -> None:
    assert plan.skill not in LANGUAGE_FORM_SKILLS
    for leak in LANGUAGE_FORM_SKILLS:
        assert f"Skill={leak}" not in user


def _assert_difficulty_contract(plan: QuestionPlan, system: str, user: str) -> None:
    band = band_for_difficulty_score(plan.difficulty)
    assert f"DifficultyBand={band}" in user
    assert f"DifficultyScore={plan.difficulty}" in user
    assert "DifficultyContract=" in user
    assert difficulty_contract_for_band(band).split("—")[0].strip()[:4] in user or band.upper() in user
    assert "uzatarak zorlaştırma YASAK" in system or "UZATARAK" in system


# ── Existing domain regressions ──────────────────────────────────────────


def test_compact_prompt_includes_stem_type_factual_recall():
    plan = _plan(
        exam="kpss_lisans",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__osmanli",
        topic_name="Osmanlı",
    )
    assert plan.skill == "ottoman_history"
    assert plan.stem_type == "factual_recall"
    user = _user(plan)
    assert "StemType=factual_recall" in user
    assert "Domain=tarih" in user
    assert "Skill=ottoman_history" in user
    assert "tarih alanına aittir" in user
    for leak in LANGUAGE_FORM_SKILLS:
        assert f"Skill={leak}" not in user


def test_compact_prompt_cografya_no_language_form_skill():
    plan = _plan(
        exam="kpss_lisans",
        subject_code="kpss_cografya",
        subject_name="Coğrafya",
        topic_code="kpss_cografya__nufus",
        topic_name="Nüfus",
    )
    user = _user(plan)
    assert "Domain=cografya" in user
    assert "coğrafya alanına aittir" in user
    _assert_no_language_leak(plan, user)


def test_compact_prompt_kpss_matematik_no_language_form():
    plan = _plan(
        exam="kpss_lisans",
        subject_code="kpss_matematik",
        subject_name="Matematik",
        topic_code="kpss_matematik__temel_matematik",
        topic_name="Temel Matematik",
    )
    user = _user(plan)
    assert "Domain=matematik" in user
    _assert_no_language_leak(plan, user)
    assert "\\\\frac" in user or "LaTeX" in user
    assert "paragraf anlatımı" in user or "hikâye" in user


def test_compact_prompt_tyt_ayt_matematik_no_turkish_cycle():
    for exam, code, topic, name in (
        ("tyt", "tyt_matematik", "tyt_matematik__temel_kavramlar", "Temel Kavramlar"),
        ("ayt", "ayt_matematik", "ayt_matematik__fonksiyonlar", "Fonksiyonlar"),
    ):
        plan = _plan(
            exam=exam,
            subject_code=code,
            subject_name="Matematik",
            topic_code=topic,
            topic_name=name,
        )
        user = _user(plan)
        _assert_no_language_leak(plan, user)
        assert "StemType=" in user
        assert "Domain=matematik" in user or "Domain=geometri" in user


def test_compact_prompt_lgs_choice_count_4():
    plan = _plan(
        exam="lgs",
        subject_code="lgs_matematik",
        subject_name="Matematik",
        topic_code="lgs_matematik__sayilar",
        topic_name="Sayılar",
        style={"choice_count": 4},
    )
    user = _user(plan)
    assert plan.choice_count == 4
    assert "ChoiceCount=4" in user
    _assert_no_language_leak(plan, user)


def test_compact_prompt_turkce_keeps_language_skills():
    plan = _plan(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="tyt_turkce__paragraf",
        topic_name="Paragraf",
        style={
            "choice_count": 5,
            "skill_distribution": {"main_idea": 0.5, "vocabulary": 0.5},
        },
    )
    user = _user(plan)
    assert "Domain=turkce" in user
    assert plan.skill in LANGUAGE_FORM_SKILLS or plan.skill in {"logic", "mixed_reasoning"}


def test_compact_prompt_yds_english_skills():
    plan = _plan(
        exam="yds",
        subject_code="yds_ingilizce",
        subject_name="İngilizce",
        topic_code="yds_ingilizce__vocabulary",
        topic_name="Vocabulary",
    )
    user = _user(plan)
    assert "Domain=english" in user
    assert "English" in user
    assert "spelling" not in plan.skill


def test_extract_json_keeps_latex_frac():
    payload = extract_json_payload(
        r'{"stem":"Hesapla $\\frac{1}{2}$","choices":{"A":"$\\sqrt{2}$","B":"1"},"correct_key":"A"}'
    )
    assert r"\frac{1}{2}" in payload["stem"]
    assert r"\sqrt{2}" in payload["choices"]["A"]


def test_compact_author_does_not_import_pdf_math_cleaner():
    import app.services.ai_cost.compact_author as mod

    src = open(mod.__file__, encoding="utf-8").read()
    assert "_clean_math_text" not in src


# ── Difficulty contract (easy / medium / hard) ───────────────────────────


@pytest.mark.parametrize("band", ("easy", "medium", "hard"))
def test_kpss_tarih_difficulty_contract(band: str):
    plan = _plan(
        exam="kpss_lisans",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__osmanli",
        topic_name="Osmanlı",
        difficulty_band=band,
    )
    system, user = _msgs(plan)
    assert band_for_difficulty_score(plan.difficulty) == band
    _assert_difficulty_contract(plan, system, user)
    assert "Domain=tarih" in user
    for leak in LANGUAGE_FORM_SKILLS:
        assert f"Skill={leak}" not in user


@pytest.mark.parametrize("band", ("easy", "medium", "hard"))
def test_tyt_matematik_difficulty_and_stem_instruction(band: str):
    plan = _plan(
        exam="tyt",
        subject_code="tyt_matematik",
        subject_name="Matematik",
        topic_code="tyt_matematik__problemler",
        topic_name="Problemler",
        difficulty_band=band,
    )
    system, user = _msgs(plan)
    assert band_for_difficulty_score(plan.difficulty) == band
    _assert_difficulty_contract(plan, system, user)
    assert "Domain=matematik" in user
    assert "matematik problemi" in user or "Matematiksel problem" in user
    assert "LaTeX" in user or "\\\\frac" in user
    _assert_no_language_leak(plan, user)
    assert plan.stem_type in {
        "calculation",
        "equation_solving",
        "problem_solving",
        "interpretation",
        "application",
        "multi_step",
    }


def test_ayt_matematik_hard_contract():
    plan = _plan(
        exam="ayt",
        subject_code="ayt_matematik",
        subject_name="Matematik",
        topic_code="ayt_matematik__fonksiyonlar",
        topic_name="Fonksiyonlar",
        difficulty_band="hard",
    )
    system, user = _msgs(plan)
    assert "DifficultyBand=hard" in user
    assert "HARD" in user or "çok adımlı" in user
    _assert_no_language_leak(plan, user)


def test_geometri_medium_no_paragraph_story():
    plan = _plan(
        exam="tyt",
        subject_code="tyt_matematik",
        subject_name="Matematik",
        topic_code="tyt_matematik__ucgenler",
        topic_name="Üçgenler",
        difficulty_band="medium",
    )
    user = _user(plan)
    assert "Domain=geometri" in user or "Domain=matematik" in user
    assert "paragraf-anlam" in user or "paragraf anlatımı" in user
    _assert_no_language_leak(plan, user)


def test_fizik_kimya_biyoloji_domain_instructions():
    cases = (
        ("tyt", "tyt_fizik", "Fizik", "tyt_fizik__kuvvet", "Kuvvet", "fizik"),
        ("tyt", "tyt_kimya", "Kimya", "tyt_kimya__atom", "Atom", "kimya"),
        ("tyt", "tyt_biyoloji", "Biyoloji", "tyt_biyoloji__hucre", "Hücre", "biyoloji"),
    )
    for exam, sub, sname, topic, tname, domain in cases:
        plan = _plan(
            exam=exam,
            subject_code=sub,
            subject_name=sname,
            topic_code=topic,
            topic_name=tname,
        )
        user = _user(plan)
        assert f"Domain={domain}" in user
        assert f"{domain} alanına aittir" in user
        _assert_no_language_leak(plan, user)


def test_ales_sayisal_and_sozel():
    say = _plan(
        exam="ales",
        subject_code="ales_sayisal",
        subject_name="Sayısal",
        topic_code="ales_sayisal__problemler",
        topic_name="Problemler",
        difficulty_band="medium",
    )
    user = _user(say)
    assert "Domain=quantitative" in user or "Domain=matematik" in user
    _assert_no_language_leak(say, user)
    assert "DifficultyBand=medium" in user

    soz = _plan(
        exam="ales",
        subject_code="ales_sozel",
        subject_name="Sözel",
        topic_code="ales_sozel__paragraf",
        topic_name="Paragraf",
    )
    user2 = _user(soz)
    assert "Domain=verbal_reasoning" in user2 or "Domain=turkce" in user2


def test_difficulty_bands_do_not_overlap_in_compact_prompt():
    for band in ("easy", "medium", "hard"):
        plan = _plan(
            exam="kpss_lisans",
            subject_code="kpss_tarih",
            subject_name="Tarih",
            topic_code="kpss_tarih__osmanli",
            topic_name="Osmanlı",
            difficulty_band=band,
        )
        assert band_for_difficulty_score(plan.difficulty) == band
        _, user = _msgs(plan)
        assert f"DifficultyBand={band}" in user
        # Only one band label in contract line
        others = {"easy", "medium", "hard"} - {band}
        # Contract text may mention other words; band assignment must match
        assert f"DifficultyBand={band}" in user
        for o in others:
            assert f"DifficultyBand={o}" not in user
