"""M34 multi_stage language — Roman numeral choices must not count as empty."""

from __future__ import annotations

from app.services.question_intelligence.multi_stage_review import (
    MIN_STAGE_SCORE,
    _choice_is_empty,
    _stage_language,
    run_multi_stage_review,
)


def test_choice_is_empty_rejects_blank_but_keeps_romans() -> None:
    assert _choice_is_empty("") is True
    assert _choice_is_empty("   ") is True
    assert _choice_is_empty(".") is True  # single non-roman glyph still empty-ish
    for roman in ("I", "V", "II", "III", "IV", "VI", "IX", "X", "i", "v"):
        assert _choice_is_empty(roman) is False, roman
    assert _choice_is_empty("Yalnız I") is False


def test_stage_language_roman_choices_i_through_v_not_empty_penalty() -> None:
    """ÖSYM-style I–V options must not trigger empty_opts (−30)."""
    question = {
        "stem": (
            "(I) Established on 7 April 1948, the World Health Organisation (WHO) "
            "is one of the original agencies of the United Nations. (II) WHO defines "
            "health not merely as the absence of disease. (III) Headquartered in "
            "Geneva, Switzerland, WHO was set up to improve international cooperation. "
            "(IV) It took over from earlier health organisations. (V) Those organisations "
            "had focused on epidemics and quarantine."
        ),
        "choices": {"A": "I", "B": "II", "C": "III", "D": "IV", "E": "V"},
        "correct_key": "D",
    }
    score = _stage_language(question)
    # Without Roman fix this scored 45 (empty I/V −30). Must clear stage threshold.
    assert score >= MIN_STAGE_SCORE, score
    # empty_opts penalty for I+V was −30; score must be well above the old failure band
    assert score >= 70, score


def test_run_multi_stage_does_not_fail_language_on_roman_choices() -> None:
    question = {
        "stem": (
            "(I) Established on 7 April 1948, the World Health Organisation (WHO) "
            "is one of the original agencies of the United Nations. (II) WHO defines "
            "health not merely as the absence of disease or illness, but as a state of "
            "complete physical, mental, and social well-being. (III) Headquartered in "
            "Geneva, Switzerland, WHO was set up to improve international cooperation "
            "for better health conditions across the world. (IV) It took over from the "
            "Health Organisation of the League of Nations and the International Public "
            "Office of Health in Paris. (V) Those two organisations had focused on the "
            "control of epidemics, quarantine measures, and the standardisation of drugs."
        ),
        "choices": {"A": "I", "B": "II", "C": "III", "D": "IV", "E": "V"},
        "correct_key": "D",
    }
    result = run_multi_stage_review(question, plan={"difficulty": 70})
    assert result.language >= MIN_STAGE_SCORE
    assert result.failed_stage != "language"


def test_truly_empty_choice_still_penalized() -> None:
    question = {
        "stem": "Bu parçanın anlatımında aşağıdakilerden hangisi yoktur? Açıklama ve örnekleme içeren yeterli uzunlukta bir Türkçe stem metni.",
        "choices": {"A": "Betimleme", "B": "", "C": " ", "D": "Öyküleme", "E": "Tanımlama"},
        "correct_key": "A",
    }
    # Two empty options → −30 from base 90 (minus possible other small hits)
    score = _stage_language(question)
    assert _choice_is_empty("") is True
    assert _choice_is_empty(" ") is True
    assert score <= 90 - 30
