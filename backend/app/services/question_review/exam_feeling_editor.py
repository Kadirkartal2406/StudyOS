"""ÖSYM exam-feeling editor score (detect only)."""

from __future__ import annotations

from typing import Any


def score_exam_feeling(question: dict[str, Any]) -> dict[str, Any]:
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    words = len(stem.split())
    flags: list[str] = []
    score = 78

    if 40 <= words <= 220:
        score += 12
    elif words < 20:
        flags.append("too_short_for_exam")
        score -= 20
    elif words > 280:
        flags.append("too_long_for_exam")
        score -= 10

    if len(choices) >= 4:
        score += 6

    low = stem.lower()
    formal_hits = sum(
        1
        for w in ("göre", "aşağıdakilerden", "paragrafa", "metne", "hangisi", "değildir")
        if w in low
    )
    score += min(8, formal_hits * 2)

    for bad in (
        "stub",
        "geçici",
        "lorem",
        "test sorusu",
        "ai ",
        "bloom düzeyi",
        "ölçülen kazanım",
        "kelimelik resmi bir üslup",
        "günlük yaşamdan bir durumu anlatan kısa bir metin düşününüz",
    ):
        if bad in low:
            flags.append(f"non_exam_tone:{bad}")
            score -= 25

    choice_blob = " ".join(str(v) for v in choices.values()).lower()
    if ("doğru yanıt" in choice_blob and "çeldirici" in choice_blob) or (
        choice_blob.count("çeldirici") >= 2
    ):
        flags.append("non_exam_tone:stub_choices")
        score -= 40

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "passed": score >= 70,
    }
