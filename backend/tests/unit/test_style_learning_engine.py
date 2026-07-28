"""M27.5 Style Learning unit tests (no PDF / no LLM)."""

from __future__ import annotations

import json

from app.services.exam_intelligence.style_learning.bloom_distribution import (
    build_bloom_distribution,
)
from app.services.exam_intelligence.style_learning.question_intent_analyzer import (
    analyze_question_intent,
)
from app.services.exam_intelligence.style_learning.style_contract import (
    validate_contract,
)
from app.services.exam_intelligence.style_learning.style_profile_builder import (
    build_topic_contract,
)
from app.services.exam_intelligence.style_learning.style_repository import (
    StyleRepository,
)
from app.services.exam_intelligence.style_learning.style_similarity import (
    style_similarity,
)
from app.services.exam_intelligence.style_learning.trap_pattern_analyzer import (
    analyze_trap_patterns,
)


def test_intent_kpss_paragraf():
    intent = analyze_question_intent(
        exam_code="kpss",
        topic_code="kpss_turkce__paragraf",
        skill_type="inference",
    )
    assert "ana_fikir" in intent["intents"]
    assert intent["primary"]


def test_trap_tyt_vs_ales():
    tyt = analyze_trap_patterns(exam_code="tyt", topic_slug="problemler")
    ales = analyze_trap_patterns(exam_code="ales")
    assert "islem_hatasi" in tyt["patterns"]
    assert "yanlis_cikarim" in ales["patterns"]


def test_bloom_sums_near_one():
    bloom = build_bloom_distribution(
        difficulty_avg=62, skill_type="problem_solving", reasoning_avg=0.5
    )
    assert abs(sum(bloom.values()) - 1.0) < 0.02


def test_build_contract_no_stem_and_valid(tmp_path):
    stats = {
        "exam_code": "kpss",
        "subject_code": "kpss_turkce",
        "topic_code": "kpss_turkce__paragraf",
        "sample_size": 20,
        "paragraph_avg": 110,
        "sentence_avg": 5.5,
        "difficulty_avg": 68,
        "reading_avg": 36,
        "option_length": 7.2,
        "reasoning_avg": 0.8,
        "skill_type": "inference",
        "distractor_pattern": "heuristic_balanced",
    }
    contract = build_topic_contract(stats=stats, exam_dna={"language_level": "formal_tr"})
    assert "stem" not in json.dumps(contract)
    assert contract["intent"]["intents"]
    assert contract["trap"]["patterns"]
    assert contract["reading_load"]["load_band"]
    assert contract["cluster"] == "reading_heavy"
    v = validate_contract(contract)
    assert v["passed"], v["issues"]

    # repository roundtrip
    path = (
        tmp_path
        / "exam_style_contracts"
        / "kpss"
        / "turkce"
        / "paragraf"
        / "style_contract.json"
    )
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(contract, ensure_ascii=False), encoding="utf-8")
    repo = StyleRepository(tmp_path)
    loaded = repo.get_topic_style("kpss", "turkce", "paragraf")
    assert loaded is not None
    assert repo.get_bloom("kpss_turkce__paragraf") is not None


def test_similarity_reading_pair():
    a = build_topic_contract(
        stats={
            "exam_code": "kpss",
            "subject_code": "kpss_turkce",
            "topic_code": "kpss_turkce__paragraf",
            "sample_size": 10,
            "paragraph_avg": 120,
            "sentence_avg": 6,
            "difficulty_avg": 65,
            "reading_avg": 40,
            "option_length": 8,
            "reasoning_avg": 0.7,
            "skill_type": "inference",
        }
    )
    b = build_topic_contract(
        stats={
            "exam_code": "yds",
            "subject_code": "yds_ingilizce",
            "topic_code": "yds_ingilizce__reading",
            "sample_size": 10,
            "paragraph_avg": 115,
            "sentence_avg": 5.5,
            "difficulty_avg": 63,
            "reading_avg": 38,
            "option_length": 7,
            "reasoning_avg": 0.65,
            "skill_type": "reading_comprehension",
        }
    )
    score = style_similarity(a, b)
    assert score >= 0.5
