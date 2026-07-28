"""M27.6 style validation unit tests."""

from __future__ import annotations

import json

from app.services.exam_intelligence.style_learning.style_profile_builder import (
    build_topic_contract,
)
from app.services.exam_intelligence.style_learning.style_similarity import (
    style_similarity,
)
from app.services.exam_intelligence.style_validation.bloom_validator import (
    validate_bloom,
)
from app.services.exam_intelligence.style_validation.contract_validator import (
    validate_contract,
)
from app.services.exam_intelligence.style_validation.quality_score import score_contract
from app.services.exam_intelligence.style_validation.similarity_validator import (
    validate_similarity,
)
from app.services.exam_intelligence.style_validation.benchmark_runner import (
    BenchmarkRunner,
)


def _sample_stats(exam: str, subject: str, topic: str, skill: str, para: float) -> dict:
    return {
        "exam_code": exam,
        "subject_code": f"{exam}_{subject}",
        "topic_code": f"{exam}_{subject}__{topic}",
        "sample_size": 12,
        "paragraph_avg": para,
        "sentence_avg": 5.0,
        "difficulty_avg": 60,
        "reading_avg": 30,
        "option_length": 6,
        "reasoning_avg": 0.6,
        "skill_type": skill,
        "distractor_pattern": "heuristic_balanced",
    }


def test_contract_validator_requires_fields():
    bad = validate_contract({"exam_code": "kpss"})
    assert not bad["passed"]
    good = validate_contract(
        build_topic_contract(stats=_sample_stats("kpss", "turkce", "paragraf", "inference", 110))
    )
    assert good["passed"]


def test_bloom_sums():
    c = build_topic_contract(stats=_sample_stats("tyt", "matematik", "problemler", "problem_solving", 40))
    res = validate_bloom(c)
    assert res["passed"]
    assert abs(res["sum"] - 1.0) < 0.08


def test_similarity_expectations():
    a = build_topic_contract(stats=_sample_stats("kpss", "turkce", "paragraf", "inference", 120))
    b = build_topic_contract(
        stats=_sample_stats("yds", "ingilizce", "reading", "reading_comprehension", 115)
    )
    c = build_topic_contract(stats=_sample_stats("tyt", "geometri", "ucgenler", "problem_solving", 25))
    report = validate_similarity(
        {
            a["topic_code"]: a,
            b["topic_code"]: b,
            c["topic_code"]: c,
            "ales_matematik__problemler": build_topic_contract(
                stats=_sample_stats("ales", "matematik", "problemler", "problem_solving", 35)
            ),
            "tyt_matematik__problemler": build_topic_contract(
                stats=_sample_stats("tyt", "matematik", "problemler", "problem_solving", 40)
            ),
            "yds_ingilizce__reading": b,
            "ayt_fizik__hareket": build_topic_contract(
                stats=_sample_stats("ayt", "fizik", "hareket", "problem_solving", 30)
            ),
            "kpss_turkce__paragraf": a,
            "tyt_geometri__ucgenler": c,
            "yokdil_ingilizce__fen": build_topic_contract(
                stats=_sample_stats("yokdil", "ingilizce", "fen", "reading_comprehension", 100)
            ),
            "dgs_matematik__problemler": build_topic_contract(
                stats=_sample_stats("dgs", "matematik", "problemler", "problem_solving", 38)
            ),
        },
        style_similarity,
    )
    assert report["tested"] >= 4


def test_quality_score_range():
    c = build_topic_contract(stats=_sample_stats("kpss", "turkce", "paragraf", "inference", 110))
    row = score_contract(
        c,
        contract_result=validate_contract(c),
        bloom_result=validate_bloom(c),
        similarity_bonus=1.0,
    )
    assert 0 <= row["score"] <= 100


def test_benchmark_writes_artifacts(tmp_path):
    # Minimal fake data tree
    contract = build_topic_contract(
        stats=_sample_stats("kpss", "turkce", "paragraf", "inference", 110)
    )
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
    # Add a few more for similarity pairs
    for exam, sub, top, skill, para in (
        ("yds", "ingilizce", "reading", "reading_comprehension", 100),
        ("tyt", "geometri", "ucgenler", "problem_solving", 20),
        ("ales", "matematik", "problemler", "problem_solving", 35),
        ("tyt", "matematik", "problemler", "problem_solving", 40),
        ("ayt", "fizik", "hareket", "problem_solving", 25),
        ("yokdil", "ingilizce", "fen", "reading_comprehension", 95),
        ("dgs", "matematik", "problemler", "problem_solving", 38),
    ):
        c = build_topic_contract(stats=_sample_stats(exam, sub, top, skill, para))
        p = (
            tmp_path
            / "exam_style_contracts"
            / exam
            / sub
            / top
            / "style_contract.json"
        )
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")

    result = BenchmarkRunner(tmp_path).run()
    assert (tmp_path / "style_validation" / "summary.json").exists()
    assert (tmp_path / "style_validation" / "validation.md").exists()
    assert result["summary"]["contracts_checked"] >= 8
