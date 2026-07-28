"""M31 confusion detector tests."""

from __future__ import annotations

from app.services.question_virtual_student.confusion_detector import analyze_confusion
from app.services.question_virtual_student.types import StudentAttempt


def _att(profile: str, opt: str, correct: bool = False) -> StudentAttempt:
    return StudentAttempt(
        profile=profile,
        chosen_option=opt,
        confidence=0.5,
        reasoning="t",
        reading_time_sec=10,
        thinking_time_sec=10,
        correct=correct,
        confused_at="x" if not correct else None,
    )


def test_majority_same_wrong_flagged():
    attempts = [_att(f"p{i}", "B") for i in range(5)] + [_att("p5", "A", True)]
    r = analyze_confusion(
        attempts,
        correct_key="A",
        question={"choices": {"A": "dogru", "B": "yanlis yakin", "C": "x", "D": "y", "E": "z"}},
    )
    assert "majority_same_wrong" in r["flags"]
    assert r["confusion_score"] >= 0.4


def test_clear_majority_correct_low_confusion():
    attempts = [_att(f"p{i}", "A", True) for i in range(7)] + [_att("p7", "C")]
    r = analyze_confusion(attempts, correct_key="A", question={"choices": {"A": "a", "C": "c"}})
    assert r["correct_count"] == 7
    assert "majority_same_wrong" not in r["flags"]
