"""Cognitive load — unnecessary length / unused paragraph."""

from __future__ import annotations

import re
from typing import Any


def measure_cognitive_load(question: dict[str, Any]) -> dict[str, Any]:
    stem = str(question.get("stem") or "")
    words = len(stem.split())
    flags: list[str] = []
    score = 100

    # Split passage vs ask (heuristic: last sentence with ?)
    parts = re.split(r"(?<=[.!?])\s+", stem.strip())
    ask = parts[-1] if parts else stem
    passage_words = max(0, words - len(ask.split()))

    if words > 260:
        flags.append("excessive_length")
        score -= 20
    if passage_words > 200 and len(ask.split()) < 8:
        flags.append("heavy_passage_weak_ask")
        score -= 15
    if passage_words >= 60 and not re.search(
        r"\b(paragraf|metin|göre|yukarıda|aşağıda)\b", ask.lower()
    ):
        # Long lead-in but ask doesn't reference it → possible fluff
        flags.append("passage_may_be_unnecessary")
        score -= 12

    if words < 15:
        flags.append("underloaded")
        score -= 10

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "word_count": words,
        "passage_words": passage_words,
        "passed": score >= 70,
    }
