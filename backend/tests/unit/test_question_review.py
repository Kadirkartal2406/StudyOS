"""M30 question review package smoke tests."""

from __future__ import annotations

from app.services.question_review.ambiguity_detector import detect_ambiguity
from app.services.question_review.cognitive_load import measure_cognitive_load
from app.services.question_review.distractor_balance import analyze_distractor_balance
from app.services.question_review.exam_feeling_editor import score_exam_feeling
from app.services.question_review.review_report import build_review_report
from app.services.question_review.review_score import build_review_breakdown, passes_review
from app.services.question_review.types import ReviewBreakdown, ReviewResult


def test_ambiguity_flags_vague_ask():
    r = detect_ambiguity({"stem": "Hangisi doğrudur?"})
    assert r["score"] < 90
    assert r["flags"]


def test_distractor_balance_correct_longest():
    r = analyze_distractor_balance(
        {
            "choices": {
                "A": "çok uzun doğru cevap burada fazladan kelimelerle",
                "B": "kısa",
                "C": "kısa2",
                "D": "kısa3",
                "E": "kısa4",
            },
            "correct_key": "A",
        }
    )
    assert "correct_is_longest" in r["flags"]


def test_cognitive_load_excessive():
    stem = "kelime " * 300 + "Hangisi?"
    r = measure_cognitive_load({"stem": stem})
    assert "excessive_length" in r["flags"]


def test_exam_feeling_penalizes_stub():
    r = score_exam_feeling({"stem": "Bu bir stub test sorusu", "choices": {"A": "1"}})
    assert r["score"] < 80


def test_review_score_threshold():
    high = ReviewBreakdown(
        clarity=92,
        fairness=91,
        language=93,
        exam_feeling=90,
        distractors=92,
        uniqueness=90,
        cognitive_load=91,
        answer_validity=94,
    )
    assert passes_review(high)
    low = ReviewBreakdown(clarity=70, fairness=70, language=70, exam_feeling=70)
    assert not passes_review(low)


def test_review_report_internal_only_fields():
    result = ReviewResult(passed=True, breakdown=ReviewBreakdown(clarity=95, fairness=90))
    report = build_review_report(result)
    assert report["clarity_score"] == 95
    assert "stem" not in report
