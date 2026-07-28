"""M30 fairness checker tests."""

from __future__ import annotations

from app.services.question_review.fairness_checker import check_fairness


def test_fair_question_high_score():
    q = {
        "stem": "Metindeki olayın sonucu nedir?",
        "choices": {
            "A": "Kısa cevap bir",
            "B": "Kısa cevap iki",
            "C": "Kısa cevap üç",
            "D": "Kısa cevap dört",
            "E": "Kısa cevap beş",
        },
        "correct_key": "B",
    }
    r = check_fairness(q)
    assert r["score"] >= 85


def test_repeated_correct_key_flagged():
    q = {
        "stem": "Soru kökü burada yer alır ve ölçüm yapar?",
        "choices": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        "correct_key": "C",
    }
    r = check_fairness(q, recent_correct_keys=["C", "C", "C"])
    assert "repeated_correct_key" in r["flags"]


def test_longest_answer_bias():
    q = {
        "stem": "Hangisi uygundur?",
        "choices": {
            "A": "kısa",
            "B": "kısa iki",
            "C": "çok daha uzun ve ayrıntılı doğru seçenek metni burada",
            "D": "kısa üç",
            "E": "kısa dört",
        },
        "correct_key": "C",
    }
    r = check_fairness(q)
    assert "longest_answer_bias" in r["flags"]
