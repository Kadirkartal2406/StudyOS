"""M31 distractor attraction tests."""

from __future__ import annotations

from app.services.question_virtual_student.distractor_attraction import (
    rank_distractor_attraction,
)


def test_attraction_ranks_similar_wrong_high():
    q = {
        "stem": "Metindeki ana düşünce toplumsal değişimdir",
        "choices": {
            "A": "Toplumsal değişimin sonuçları",
            "B": "Kısa",
            "C": "xyz",
            "D": "abc",
            "E": "def",
        },
        "correct_key": "A",
    }
    ranked = rank_distractor_attraction(q)
    assert ranked[0].option in {"A", "B", "C", "D", "E"}
    wrong = [d for d in ranked if d.option != "A"]
    assert wrong
    assert all(0.0 <= d.attraction_score <= 1.0 for d in ranked)
    assert all(d.trap_type for d in ranked)


def test_correct_marked_as_correct_trap():
    q = {
        "stem": "Soru",
        "choices": {"A": "Doğru uzun metin", "B": "Yanlış", "C": "Yanlış2", "D": "Y3", "E": "Y4"},
        "correct_key": "A",
    }
    ranked = rank_distractor_attraction(q)
    correct = next(d for d in ranked if d.option == "A")
    assert correct.trap_type == "correct"
