"""M31 VirtualStudentEngine tests."""

from __future__ import annotations

from app.services.question_virtual_student import VirtualStudentEngine
from app.services.question_virtual_student.types import MIN_VSSE_SCORE


def _good_q() -> dict:
    return {
        "stem": (
            "Bir araştırmacı toplumsal değişimi gözlemleyerek neden-sonuç ilişkisi kurar. "
            "Paragrafa göre yazarın temel vurgusu aşağıdakilerden hangisinde en iyi verilir?"
        ),
        "choices": {
            "A": "Bireysel tercihler",
            "B": "Toplumsal sonuçlar",
            "C": "Üslup kaygısı",
            "D": "Zaman betimi",
            "E": "Mekân ayrıntısı",
        },
        "correct_key": "B",
        "author_difficulty": 70,
    }


def test_vsse_runs_all_profiles():
    result = VirtualStudentEngine().simulate(_good_q())
    assert len(result.attempts) == 9
    assert result.solve_distribution
    assert 0 <= result.virtual_student_score <= 100
    meta = result.internal_metadata()
    assert "student_profiles" in meta
    assert "confusion_score" in meta
    assert "distractor_attraction" in meta


def test_vsse_rejects_artificial_language():
    bad = {
        "stem": "Bu soruda dikkat edilirse yapay zeka stub lorem metni nedir?",
        "choices": {"A": "1", "B": "1", "C": "2", "D": "3", "E": "4"},
        "correct_key": "A",
    }
    result = VirtualStudentEngine().simulate(bad)
    assert not result.passed
    assert result.reject_reasons or result.virtual_student_score < MIN_VSSE_SCORE


def test_vsse_metadata_has_no_stem_key_as_output_contract():
    result = VirtualStudentEngine().simulate(_good_q())
    meta = result.internal_metadata()
    assert "stem" not in meta
