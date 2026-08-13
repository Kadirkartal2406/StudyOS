"""Domain-aware QuestionPlanner regression tests."""

from __future__ import annotations

from app.services.qie.planner import QuestionPlanner
from app.services.qie.skill_profiles import (
    LANGUAGE_FORM_SKILLS,
    get_skill_profile,
    resolve_domain,
)
from app.services.qie.types import GenerateContext

# KPSS exam-level DNA historically injected Türkçe skill_distribution for ALL subjects.
_KPSS_TURKCE_DNA = {
    "choice_count": 5,
    "skill_distribution": {
        "logic": 0.06,
        "grammar": 0.1,
        "spelling": 0.08,
        "coherence": 0.08,
        "main_idea": 0.1,
        "vocabulary": 0.08,
        "punctuation": 0.08,
        "mixed_reasoning": 0.06,
        "supporting_idea": 0.1,
        "sentence_meaning": 0.08,
        "sentence_ordering": 0.08,
        "paragraph_completion": 0.1,
    },
    "paragraph_length_avg": 150,
}


def _plan(
    *,
    exam: str,
    subject_code: str,
    subject_name: str,
    topic_code: str,
    topic_name: str,
    count: int = 5,
    style: dict | None = None,
) -> list:
    ctx = GenerateContext(
        exam=exam,
        subject_code=subject_code,
        subject_name=subject_name,
        topic_code=topic_code,
        topic_name=topic_name,
        count=count,
        difficulty_band="medium",
    )
    return QuestionPlanner().plan_batch(ctx, style=style or {"choice_count": 5})


def _skills(plans) -> set[str]:
    return {p.skill for p in plans}


def _stems(plans) -> set[str]:
    return {p.stem_type for p in plans}


def test_kpss_tarih_no_language_form_skills():
    plans = _plan(
        exam="kpss_lisans",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__osmanli",
        topic_name="Osmanlı",
        style=_KPSS_TURKCE_DNA,
    )
    assert plans
    bad = _skills(plans) & LANGUAGE_FORM_SKILLS
    assert not bad, f"KPSS Tarih leaked language skills: {bad}"
    assert all(p.stem_type not in LANGUAGE_FORM_SKILLS for p in plans)
    assert resolve_domain(subject_code="kpss_tarih") == "tarih"


def test_kpss_cografya_no_spelling_grammar():
    plans = _plan(
        exam="kpss_lisans",
        subject_code="kpss_cografya",
        subject_name="Coğrafya",
        topic_code="kpss_cografya__nufus",
        topic_name="Nüfus",
        style=_KPSS_TURKCE_DNA,
    )
    skills = _skills(plans)
    assert "spelling" not in skills
    assert "grammar" not in skills
    assert not (skills & LANGUAGE_FORM_SKILLS)
    profile = get_skill_profile(subject_code="kpss_cografya", topic_code="kpss_cografya__nufus")
    assert profile.domain == "cografya"
    assert skills <= set(profile.skills)
    # Topic boost: nüfus → population first
    assert plans[0].skill == "population"


def test_tyt_matematik_no_language_cycle():
    plans = _plan(
        exam="tyt",
        subject_code="tyt_matematik",
        subject_name="Matematik",
        topic_code="tyt_matematik__temel_kavramlar",
        topic_name="Temel Kavramlar",
        style={
            "choice_count": 5,
            "skill_distribution": {
                "main_idea": 0.15,
                "grammar": 0.12,
                "vocabulary": 0.12,
                "logic": 0.12,
            },
            "paragraph_length_avg": 175,
        },
    )
    bad = _skills(plans) & LANGUAGE_FORM_SKILLS
    assert not bad, f"TYT Matematik leaked language skills: {bad}"
    assert all(
        p.stem_type
        in {
            "calculation",
            "equation_solving",
            "problem_solving",
            "interpretation",
            "application",
            "multi_step",
        }
        for p in plans
    )


def test_ayt_matematik_no_turkish_skill_cycle():
    plans = _plan(
        exam="ayt",
        subject_code="ayt_matematik",
        subject_name="Matematik",
        topic_code="ayt_matematik__fonksiyonlar",
        topic_name="Fonksiyonlar",
        style={"choice_count": 5},  # empty DNA skills → old bug used _SKILL_DEFAULTS
    )
    bad = _skills(plans) & LANGUAGE_FORM_SKILLS
    assert not bad
    assert "vocabulary" not in _skills(plans)
    assert "spelling" not in _skills(plans)


def test_lgs_matematik_no_turkish_cycle_choice_count_4():
    plans = _plan(
        exam="lgs",
        subject_code="lgs_matematik",
        subject_name="Matematik",
        topic_code="lgs_matematik__sayilar",
        topic_name="Sayılar",
        style={"choice_count": 4},
    )
    bad = _skills(plans) & LANGUAGE_FORM_SKILLS
    assert not bad
    assert all(p.choice_count == 4 for p in plans)


def test_ales_sayisal_no_turkish_cycle():
    plans = _plan(
        exam="ales",
        subject_code="ales_sayisal",
        subject_name="Sayısal",
        topic_code="ales_sayisal__problemler",
        topic_name="Problemler",
        style={"choice_count": 5},
    )
    bad = _skills(plans) & LANGUAGE_FORM_SKILLS
    assert not bad
    profile = get_skill_profile(subject_code="ales_sayisal")
    assert profile.domain == "quantitative"
    assert _skills(plans) <= set(profile.skills)


def test_yds_english_language_skills_allowed():
    plans = _plan(
        exam="yds",
        subject_code="yds_ingilizce",
        subject_name="İngilizce",
        topic_code="yds_ingilizce__vocabulary",
        topic_name="Vocabulary",
        style={"choice_count": 5},
    )
    skills = _skills(plans)
    assert skills & {"vocabulary", "grammar", "reading", "cloze", "translation", "sentence_completion"}
    # Must not use Turkish-only form skills like spelling/punctuation/coherence
    assert "spelling" not in skills
    assert "punctuation" not in skills
    assert resolve_domain(exam="yds", subject_code="yds_ingilizce") == "english"


def test_ydt_english_language_skills_allowed():
    plans = _plan(
        exam="ydt",
        subject_code="ydt_ingilizce",
        subject_name="İngilizce",
        topic_code="ydt_ingilizce__reading",
        topic_name="Reading",
        style={"choice_count": 5},
    )
    assert resolve_domain(exam="ydt", subject_code="ydt_ingilizce") == "english"
    assert "spelling" not in _skills(plans)


def test_tyt_turkce_keeps_language_skills():
    plans = _plan(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="tyt_turkce__paragraf",
        topic_name="Paragraf",
        style={
            "choice_count": 5,
            "skill_distribution": {
                "main_idea": 0.2,
                "vocabulary": 0.2,
                "grammar": 0.2,
                "spelling": 0.2,
                "paragraph_completion": 0.2,
            },
        },
    )
    skills = _skills(plans)
    assert skills & LANGUAGE_FORM_SKILLS
    assert resolve_domain(subject_code="tyt_turkce", topic_code="tyt_turkce__paragraf") == "turkce"


def test_topic_specific_geometri_under_matematik():
    plans = _plan(
        exam="tyt",
        subject_code="tyt_matematik",
        subject_name="Matematik",
        topic_code="tyt_matematik__ucgenler",
        topic_name="Üçgenler",
        style={"choice_count": 5},
    )
    profile = get_skill_profile(
        subject_code="tyt_matematik",
        topic_code="tyt_matematik__ucgenler",
        topic_name="Üçgenler",
    )
    assert profile.domain == "geometri"
    assert _skills(plans) <= set(profile.skills)
    assert not (_skills(plans) & LANGUAGE_FORM_SKILLS)


def test_unknown_subject_does_not_fall_to_turkish():
    plans = _plan(
        exam="custom",
        subject_code="xyz_unknown_branch",
        subject_name="Unknown Branch",
        topic_code="xyz_unknown_branch__misc",
        topic_name="Misc",
        style={
            "choice_count": 5,
            "skill_distribution": {
                "vocabulary": 0.5,
                "spelling": 0.5,
                "grammar": 0.5,
            },
        },
    )
    bad = _skills(plans) & LANGUAGE_FORM_SKILLS
    assert not bad, f"Unknown subject fell back to Turkish skills: {bad}"
    profile = get_skill_profile(subject_code="xyz_unknown_branch")
    assert profile.domain == "unknown"
    assert _skills(plans) <= set(profile.skills)


def test_kpss_turkce_still_uses_language_profile():
    plans = _plan(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="kpss_turkce__paragraf",
        topic_name="Paragraf",
        style=_KPSS_TURKCE_DNA,
    )
    assert _skills(plans) & LANGUAGE_FORM_SKILLS
    assert resolve_domain(subject_code="kpss_turkce") == "turkce"


def test_context_fields_preserved_on_plans():
    plans = _plan(
        exam="kpss_lisans",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__cumhuriyet",
        topic_name="Cumhuriyet",
        style={"choice_count": 5},
    )
    for p in plans:
        assert p.exam == "kpss_lisans"
        assert p.subject_code == "kpss_tarih"
        assert p.topic_code == "kpss_tarih__cumhuriyet"
        assert p.choice_count == 5
        assert p.skill
        assert p.stem_type


def test_factual_recall_caps_paragraph_length_not_reading():
    plans = _plan(
        exam="kpss_lisans",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__osmanli",
        topic_name="Osmanlı",
        count=1,
        style={"choice_count": 5, "paragraph_length_avg": 150},
    )
    assert plans[0].stem_type == "factual_recall"
    assert plans[0].paragraph_length <= 50


def test_turkce_paragraf_keeps_long_paragraph_length():
    plans = _plan(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="tyt_turkce__paragraf",
        topic_name="Paragraf",
        count=1,
        style={"choice_count": 5, "paragraph_length_avg": 180},
    )
    assert plans[0].paragraph_length >= 80
