"""M30 answer verifier tests."""

from __future__ import annotations

from app.services.question_review.answer_verifier import verify_answer


def test_single_correct_ok():
    q = {
        "stem": "Metne göre ana düşünce hangisidir?",
        "choices": {"A": "Doğru", "B": "Yanlış1", "C": "Yanlış2", "D": "Yanlış3", "E": "Yanlış4"},
        "correct_key": "A",
    }
    r = verify_answer(q)
    assert r["passed"]
    assert r["single_correct"]


def test_duplicate_options_fail():
    q = {
        "stem": "x",
        "choices": {"A": "Aynı", "B": "Aynı", "C": "Farklı", "D": "Diğer", "E": "Son"},
        "correct_key": "A",
    }
    r = verify_answer(q)
    assert not r["passed"]
    assert "non_unique_options" in r["flags"] or "identical:A/B" in r["flags"]


def test_invalid_correct_key():
    q = {
        "stem": "x",
        "choices": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        "correct_key": "Z",
    }
    r = verify_answer(q)
    assert "invalid_correct_key" in r["flags"]
