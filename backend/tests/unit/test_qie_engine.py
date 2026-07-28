"""Sprint 25 — QIE unit tests (no LLM required)."""

from __future__ import annotations

from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.qie.adaptive_calibration import (
    AdaptiveCalibrationPlanner,
    adapt_difficulty_band,
)
from app.services.qie.calibration_planner import CalibrationPlanner
from app.services.qie.distractor_model import DistractorPattern, pick_distractor
from app.services.qie.planner import QuestionPlanner
from app.services.qie.prompt_builder_v3 import build_qie_messages
from app.services.qie.quality_gate_v2 import passes_quality_gate, score_quality
from app.services.qie.similarity import is_similar_question, stem_hash
from app.services.qie.types import GenerateContext, MIN_QUALITY_SCORE, QuestionPlan


def test_calibration_skills_unique():
    plans = CalibrationPlanner().plan(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="paragraf",
        topic_name="Paragraf",
        count=12,
    )
    skills = [p.skill for p in plans]
    assert len(skills) == 12
    assert len(set(skills)) == 12


def test_planner_respects_count_and_forbidden_cycle():
    ctx = GenerateContext(
        exam="kpss",
        subject_code="turkce",
        subject_name="Türkçe",
        topic_code="anlam",
        topic_name="Anlam",
        count=5,
        recent_patterns=["meaning_shift"],
    )
    plans = QuestionPlanner().plan_batch(ctx, style={"choice_count": 5})
    assert len(plans) == 5
    assert all(p.distractor_pattern != "meaning_shift" or i > 0 for i, p in enumerate(plans[:1]))
    assert plans[0].distractor_pattern != "meaning_shift"


def test_pick_distractor_deterministic():
    a = pick_distractor(index=0, forbidden=[])
    b = pick_distractor(index=0, forbidden=[])
    assert a == b
    assert a == DistractorPattern.MEANING_SHIFT.value


def test_adaptive_high_accuracy_harder():
    band, diff = adapt_difficulty_band(0.9)
    assert band == "hard"
    assert diff >= 80
    plans = AdaptiveCalibrationPlanner().plan_remaining(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="x",
        topic_name="x",
        total_count=12,
        already_done=4,
        used_skills=["vocabulary", "sentence_meaning", "main_idea", "supporting_idea"],
        early_accuracy=0.9,
    )
    assert len(plans) == 8
    assert all(p.difficulty >= 80 for p in plans)


def test_adaptive_low_accuracy_easier_foundational():
    band, diff = adapt_difficulty_band(0.2)
    assert band == "easy"
    assert diff <= 52
    plans = AdaptiveCalibrationPlanner().plan_remaining(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="x",
        topic_name="x",
        total_count=12,
        already_done=4,
        used_skills=["main_idea", "logic", "mixed_reasoning", "coherence"],
        early_accuracy=0.2,
    )
    assert len(plans) == 8
    assert all(p.difficulty <= 52 for p in plans)


def test_prompt_v3_contract_forbids_llm_decisions():
    plan = QuestionPlan(
        exam="kpss",
        subject_code="t",
        subject_name="Türkçe",
        topic_code="p",
        topic_name="Paragraf",
        skill="inference",
        difficulty=78,
        bloom="analyze",
        distractor_pattern="meaning_shift",
        stem_type="comparison",
        paragraph_length=430,
    )
    messages, fp = build_qie_messages([plan], style_dna={"exam_code": "kpss", "choice_count": 5})
    assert fp
    system = messages[0]["content"]
    assert "KARAR VERMEYECEKSİN" in system
    assert "DEĞİŞTİRMEYECEKSİN" in system
    assert "skill=inference" in messages[1]["content"] or '"skill": "inference"' in messages[1]["content"]


def test_similarity_rejects_near_duplicate():
    item = ValidatedQuizItem(
        stem="Paragrafta yazarın asıl anlatmak istediği düşünce aşağıdakilerden hangisidir?",
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="A",
    )
    existing = [
        "Paragrafta yazarın asıl anlatmak istediği düşünce aşağıdakilerden hangisidir?"
    ]
    assert is_similar_question(item, existing_stems=existing)
    assert stem_hash(item.stem) == stem_hash(existing[0])


def test_quality_gate_threshold():
    from app.services.qie.types import QualityBreakdown

    plan = QuestionPlan(
        exam="kpss",
        subject_code="t",
        subject_name="Türkçe",
        topic_code="p",
        topic_name="Paragraf Anlam",
        skill="main_idea",
        difficulty=75,
        bloom="analyze",
        paragraph_length=70,
        reading_time_sec=70,
        stem_type="inference",
        choice_count=5,
    )
    good = ValidatedQuizItem(
        stem=(
            "Aşağıdaki metinde yazar toplumsal değişimi ve bireysel sorumluluğu tartışır. "
            "Temel iddia, kurumların şeffaflığı olmadan güvenin oluşamayacağıdır. "
            "Ayrıca kamuoyunun denetim mekanizmalarının güçlenmesi gerektiği vurgulanır. "
            "Buna göre paragrafın ana düşüncesi aşağıdakilerden hangisidir?"
        ),
        choices={
            "A": "Kurumsal şeffaflık güvenin önkoşuludur",
            "B": "Bireysel sorumluluk gereksizdir",
            "C": "Değişim rastlantısaldır",
            "D": "Metin yalnızca tarih anlatır",
            "E": "Yazar mizah yapmaktadır",
        },
        correct_key="A",
    )
    q = score_quality(good, plan, difficulty_score=88, existing_stems=[])
    bad = ValidatedQuizItem(
        stem="Hangisi doğrudur?",
        choices={"A": "a", "B": "a", "C": "a", "D": "a", "E": "a"},
        correct_key="A",
    )
    q2 = score_quality(bad, plan, difficulty_score=40, existing_stems=[])
    assert q.total > q2.total
    assert q2.total < MIN_QUALITY_SCORE
    assert not passes_quality_gate(q2)
    # Gate threshold itself
    assert passes_quality_gate(
        QualityBreakdown(
            style=90,
            difficulty=90,
            similarity=95,
            grammar=90,
            option_balance=90,
            distractor_quality=90,
            blueprint_match=90,
            reading_time=85,
            exam_feel=90,
        )
    )
