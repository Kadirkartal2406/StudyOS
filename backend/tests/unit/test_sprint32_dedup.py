import pytest
from app.services.deduplication_service import compute_stem_hash, filter_unseen_questions

def test_compute_stem_hash():
    h1 = compute_stem_hash("3x - 7 = 11 ise x kaçtır?")
    h2 = compute_stem_hash("  3x - 7 = 11 ise   x kaçtır?  ")
    assert h1 == h2
    assert len(h1) == 64

def test_filter_unseen_questions():
    items = [
        {"question": "Soru 1", "stem": "Soru 1"},
        {"question": "Soru 2", "stem": "Soru 2"},
        {"question": "Soru 3", "stem": "Soru 3"},
    ]
    seen_hashes = {compute_stem_hash("Soru 2")}
    unseen = filter_unseen_questions(items, seen_hashes)
    assert len(unseen) == 2
    assert [q["stem"] for q in unseen] == ["Soru 1", "Soru 3"]
