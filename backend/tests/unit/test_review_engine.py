"""M30 review engine orchestration tests."""

from __future__ import annotations

from app.services.question_review.review_engine import QuestionReviewEngine
from app.services.question_review.types import MIN_REVIEW_SCORE


def _good_question() -> dict:
    return {
        "stem": (
            "Bir yazar, gözlemlediği toplumsal değişimi neden-sonuç ilişkisiyle "
            "aktarır. Paragrafa göre anlatıcının temel vurgusu aşağıdakilerden "
            "hangisinde en doğru biçimde verilmiştir?"
        ),
        "choices": {
            "A": "Değişimin bireysel etkileri",
            "B": "Değişimin toplumsal sonuçları",
            "C": "Anlatıcının üslup tercihi",
            "D": "Zamanın doğrusal akışı",
            "E": "Mekân betimlemesinin rolü",
        },
        "correct_key": "B",
    }


def test_review_engine_passes_good_question():
    result = QuestionReviewEngine().review(_good_question())
    assert result.passed
    assert result.breakdown.review_score >= MIN_REVIEW_SCORE
    meta = result.internal_metadata()
    assert "review_score" in meta
    assert "review_comments" in meta


def test_review_engine_fails_ambiguous_duplicate():
    bad = {
        "stem": "Hangisi doğrudur?",
        "choices": {"A": "Aynı", "B": "Aynı", "C": "x", "D": "y", "E": "z"},
        "correct_key": "A",
    }
    result = QuestionReviewEngine().review(bad)
    assert not result.passed
    assert result.breakdown.review_score < MIN_REVIEW_SCORE
