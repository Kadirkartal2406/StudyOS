"""Ambiguity / double-meaning detector (editor only)."""

from __future__ import annotations

import re
from typing import Any

_AMBIGUOUS = [
    r"\bhangisi doğrudur\b",
    r"\bhangisi yanlıştır\b",
    r"\byukarıdakilerden hangisi\b",
    r"\başağıdakilerden hangisi\b(?!\s+(doğru|yanlış|verilmiştir|söylenemez))",
    r"\bbelirsiz\b",
    r"\byoruma açık\b",
    r"\bolabilir\b.*\bolabilir\b",
    r"\bhem .* hem\b",
]

_INCOMPLETE = [
    r"\?\s*$",  # ok if has stem content
]


def detect_ambiguity(question: dict[str, Any]) -> dict[str, Any]:
    stem = str(question.get("stem") or "")
    low = stem.lower()
    flags: list[str] = []
    score = 100

    for pat in _AMBIGUOUS:
        if re.search(pat, low, flags=re.IGNORECASE):
            flags.append(f"ambiguous_phrase:{pat}")
            score -= 12

    # Double question marks / multiple asks
    if stem.count("?") >= 2:
        flags.append("multiple_questions")
        score -= 15

    # Missing concrete ask
    if len(stem.split()) < 12:
        flags.append("too_short_stem")
        score -= 20

    # Vague "doğru/yanlış" without criterion
    if re.search(r"hangisi\s+(daha\s+)?(doğru|uygun|iyidir)", low) and "göre" not in low:
        flags.append("vague_correctness_without_criterion")
        score -= 10

    # Incomplete info markers
    if re.search(r"\b(bilgi\s+yetersiz|eksik\s+veri|tam\s+değil)\b", low):
        flags.append("incomplete_info_signal")
        score -= 8

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "passed": score >= 70,
    }
