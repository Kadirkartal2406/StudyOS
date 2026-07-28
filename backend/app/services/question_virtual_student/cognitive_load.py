"""Cognitive load model for VSSE (separate from Review cognitive_load)."""

from __future__ import annotations

import re
from typing import Any


def analyze_cognitive_load(question: dict[str, Any]) -> dict[str, Any]:
    stem = str(question.get("stem") or "")
    words = len(stem.split())
    sentences = [s for s in re.split(r"[.!?]+", stem) if s.strip()]
    avg_sent = words / max(len(sentences), 1)

    intrinsic = min(1.0, words / 180.0)
    # Extraneous: long clauses, nested commas
    commas = stem.count(",")
    extraneous = min(1.0, (commas / 8.0) * 0.5 + (0.3 if avg_sent > 28 else 0.0))
    working = min(1.0, 0.5 * intrinsic + 0.5 * extraneous)
    complexity = (
        "high" if avg_sent >= 30 or words >= 200 else ("medium" if avg_sent >= 18 else "low")
    )

    return {
        "intrinsic_load": round(intrinsic, 3),
        "extraneous_load": round(extraneous, 3),
        "working_memory_load": round(working, 3),
        "sentence_complexity": complexity,
        "avg_sentence_words": round(avg_sent, 1),
        "very_high": working >= 0.75 or words >= 260,
    }
