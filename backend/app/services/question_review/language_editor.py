"""Turkish language editor checks (detect only)."""

from __future__ import annotations

import re
from typing import Any

_REPEAT = re.compile(r"\b(\w+)(\s+\1){2,}\b", re.IGNORECASE)
_SPACING = re.compile(r"\s{2,}| ,|,  ")
_TRAILING = re.compile(r"[,:;]\s*$")


def edit_language(question: dict[str, Any]) -> dict[str, Any]:
    stem = str(question.get("stem") or "")
    flags: list[str] = []
    score = 100

    if _REPEAT.search(stem):
        flags.append("word_repetition")
        score -= 15

    if _SPACING.search(stem):
        flags.append("spacing_punctuation")
        score -= 8

    # Very long sentence without comma/period
    sentences = re.split(r"[.!?]+", stem)
    for s in sentences:
        words = s.split()
        if len(words) >= 55:
            flags.append("overlong_sentence")
            score -= 12
            break

    # Devrik / awkward AI openers
    low = stem.lower().strip()
    for bad in ("bu soruda dikkat edilirse", "yapay zeka", "aşağıdaki metne göre dikkatlice"):
        if bad in low:
            flags.append(f"ai_phrase:{bad}")
            score -= 18

    # Missing terminal punctuation on question
    if "?" not in stem and len(stem.split()) > 20:
        flags.append("missing_question_mark")
        score -= 10

    # Options language
    for k, v in (question.get("choices") or {}).items():
        if _REPEAT.search(str(v)):
            flags.append(f"option_repetition:{k}")
            score -= 8

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "passed": score >= 70,
    }
