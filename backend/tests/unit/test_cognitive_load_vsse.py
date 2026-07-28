"""M31 VSSE cognitive load tests."""

from __future__ import annotations

from app.services.question_virtual_student.cognitive_load import analyze_cognitive_load


def test_cognitive_load_fields():
    r = analyze_cognitive_load(
        {
            "stem": "Kısa bir cümle. Başka bir cümle daha var ve soru nedir?",
        }
    )
    assert "intrinsic_load" in r
    assert "extraneous_load" in r
    assert "working_memory_load" in r
    assert r["sentence_complexity"] in ("low", "medium", "high")


def test_very_high_load_on_long_stem():
    stem = ("Uzun cümle, " * 40) + "sonuç nedir?"
    r = analyze_cognitive_load({"stem": stem})
    assert r["very_high"] or r["working_memory_load"] >= 0.5
