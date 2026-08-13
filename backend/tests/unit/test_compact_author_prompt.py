"""Compact author prompt carries planner Domain/Skill/StemType (no LLM)."""

from __future__ import annotations

from app.services.ai.quiz_quality_gate import extract_json_payload
from app.services.ai_cost.compact_author import _messages
from app.services.qie.planner import QuestionPlanner
from app.services.qie.skill_profiles import LANGUAGE_FORM_SKILLS
from app.services.qie.types import GenerateContext, QuestionPlan


def _plan(**kwargs) -> QuestionPlan:
    ctx = GenerateContext(
        exam=kwargs["exam"],
        subject_code=kwargs["subject_code"],
        subject_name=kwargs["subject_name"],
        topic_code=kwargs["topic_code"],
        topic_name=kwargs["topic_name"],
        count=1,
        difficulty_band="medium",
    )
    style = kwargs.get("style") or {"choice_count": kwargs.get("choice_count", 5)}
    return QuestionPlanner().plan_batch(ctx, style=style)[0]


def _user(plan: QuestionPlan) -> str:
    msgs = _messages(plan, {"measured_outcome": plan.skill, "paragraph_length": plan.paragraph_length})
    return msgs[1].content


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
    for leak in LANGUAGE_FORM_SKILLS:
        assert f"Skill={leak}" not in user
    assert plan.skill not in LANGUAGE_FORM_SKILLS


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
    assert plan.skill not in LANGUAGE_FORM_SKILLS
    for leak in LANGUAGE_FORM_SKILLS:
        assert f"Skill={leak}" not in user
    assert "\\\\frac" in user or "LaTeX" in user


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
        assert plan.skill not in LANGUAGE_FORM_SKILLS
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
    assert plan.skill not in LANGUAGE_FORM_SKILLS


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
