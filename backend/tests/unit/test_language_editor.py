"""M30 language editor tests."""

from __future__ import annotations

from app.services.question_review.language_editor import edit_language


def test_clean_language_passes():
    q = {
        "stem": "Paragrafa göre yazarın asıl anlatmak istediği aşağıdakilerden hangisidir?",
        "choices": {"A": "a", "B": "b", "C": "c", "D": "d", "E": "e"},
    }
    r = edit_language(q)
    assert r["score"] >= 80


def test_ai_phrase_penalized():
    q = {
        "stem": "Bu soruda dikkat edilirse yapay zeka ile ilgili bir metin vardır?",
        "choices": {"A": "a", "B": "b"},
    }
    r = edit_language(q)
    assert r["score"] < 90
    assert any("ai_phrase" in f for f in r["flags"])


def test_word_repetition_flagged():
    q = {
        "stem": "kitap kitap kitap hakkında ne söylenebilir?",
        "choices": {"A": "x"},
    }
    r = edit_language(q)
    assert "word_repetition" in r["flags"]
