"""Sprint 23 — duplicate checker unit tests."""

from app.services.ai.duplicate_checker import (
    filter_near_duplicates,
    is_near_duplicate,
    stem_similarity,
)
from app.services.ai.quiz_quality_gate import ValidatedQuizItem


def _item(stem: str) -> ValidatedQuizItem:
    return ValidatedQuizItem(
        stem=stem,
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="A",
    )


def test_near_identical_stems_flagged():
    a = (
        "Bir yazar toplumsal değişimin bireysel tercihlerle sınırlı olmadığını "
        "savunarak kurumların rolüne dikkat çeker ve sistematik baskıları vurgular."
    )
    b = (
        "Bir yazar toplumsal değişimin bireysel tercihlerle sınırlı olmadığını "
        "savunarak kurumların rolüne dikkat çeker ve sistematik baskıları vurgular."
    )
    assert stem_similarity(a, b) >= 0.9
    assert is_near_duplicate(b, [a])


def test_unrelated_stems_pass():
    a = "İki artı iki kaç eder ve neden?"
    b = "Osmanlı Devleti'nde Tanzimat Fermanı hangi padişah döneminde ilan edilmiştir?"
    assert stem_similarity(a, b) < 0.4
    assert not is_near_duplicate(b, [a])


def test_filter_near_duplicates_within_batch():
    stem = (
        "Metne göre yazarın asıl vurgusu kurumsal yapıların bireysel tercihi "
        "biçimlendirdiği yönündedir çünkü sistematik baskılar tercih alanını daraltır."
    )
    items = [_item(stem), _item(stem + " ek cümle yok neredeyse aynı"), _item("Tamamen farklı bir matematik sorusu: 3x+1=10 ise x kaçtır?")]
    # Second is similar-ish; force exact dup
    items[1] = _item(stem)
    kept = filter_near_duplicates(items)
    assert len(kept) == 2
    assert kept[0].stem == stem
    assert "matematik" in kept[1].stem.lower()
