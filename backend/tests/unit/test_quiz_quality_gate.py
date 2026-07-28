"""Sprint 14 — Quiz Quality Gate unit tests."""

from app.services.ai.quiz_quality_gate import (
    extract_json_payload,
    validate_quiz_payload,
)


def test_extract_json_from_fence():
    text = '```json\n{"questions": []}\n```'
    assert extract_json_payload(text) == {"questions": []}


def test_valid_four_choice_item():
    payload = {
        "questions": [
            {
                "stem": "Anayasa'nın üstünlüğü ne anlama gelir?",
                "choices": {
                    "A": "Yasalar anayasaya uygun olmalı",
                    "B": "Anayasa değiştirilemez",
                    "C": "Mahkemeler karar veremez",
                    "D": "Hükümet anayasayı yok sayabilir",
                },
                "correct_key": "A",
                "explanation": "Kısa açıklama",
            }
        ]
    }
    gate = validate_quiz_payload(payload, topic_name="Anayasa", expected_count=1)
    assert len(gate.valid) == 1
    assert gate.valid[0].correct_key == "A"
    assert gate.rejected_count == 0


def test_rejects_missing_choice():
    payload = {
        "questions": [
            {
                "stem": "Geçerli uzunlukta bir soru metni burada",
                "choices": {"A": "1", "B": "2", "C": "3"},
                "correct_key": "A",
            }
        ]
    }
    gate = validate_quiz_payload(payload, expected_count=1)
    assert gate.valid == []
    assert gate.rejected_count == 1


def test_rejects_invalid_correct_key():
    payload = [
        {
            "stem": "Geçerli uzunlukta bir soru metni burada",
            "choices": {"A": "1", "B": "2", "C": "3", "D": "4"},
            "correct_key": "E",
        }
    ]
    gate = validate_quiz_payload(payload, expected_count=1)
    assert gate.valid == []


def test_rejects_placeholder():
    payload = {
        "questions": [
            {
                "stem": "example question about nothing really here",
                "choices": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_key": "A",
            }
        ]
    }
    gate = validate_quiz_payload(payload, topic_name="Anayasa Hukuku", expected_count=1)
    assert gate.valid == []


def test_truncates_to_expected_count():
    items = [
        {
            "stem": f"Geçerli uzunlukta soru numarası {i} burada",
            "choices": {"A": "a", "B": "b", "C": "c", "D": "d"},
            "correct_key": "B",
        }
        for i in range(5)
    ]
    gate = validate_quiz_payload({"questions": items}, expected_count=2)
    assert len(gate.valid) == 2
