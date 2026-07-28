"""Similarity Engine — stem hash + n-gram + option similarity (beta)."""

from __future__ import annotations

import hashlib
from typing import Iterable

from app.services.ai.duplicate_checker import (
    is_near_duplicate,
    normalize_stem,
    stem_similarity,
)
from app.services.ai.quiz_quality_gate import ValidatedQuizItem


def stem_hash(stem: str) -> str:
    return hashlib.sha256(normalize_stem(stem).encode("utf-8")).hexdigest()[:24]


def option_similarity(a: dict[str, str], b: dict[str, str]) -> float:
    """Average pairwise stem-similarity of option texts."""
    va = [normalize_stem(str(v)) for v in (a or {}).values() if v]
    vb = [normalize_stem(str(v)) for v in (b or {}).values() if v]
    if not va or not vb:
        return 0.0
    scores: list[float] = []
    for x in va:
        best = max((stem_similarity(x, y) for y in vb), default=0.0)
        scores.append(best)
    return sum(scores) / len(scores) if scores else 0.0


def is_similar_question(
    item: ValidatedQuizItem,
    *,
    existing_stems: Iterable[str],
    existing_option_sets: Iterable[dict[str, str]] | None = None,
    stem_threshold: float = 0.72,
    option_threshold: float = 0.85,
) -> bool:
    if is_near_duplicate(item.stem, existing_stems, threshold=stem_threshold):
        return True
    h = stem_hash(item.stem)
    for other in existing_stems:
        if stem_hash(other) == h:
            return True
    if existing_option_sets:
        for opts in existing_option_sets:
            if option_similarity(item.choices, opts) >= option_threshold:
                return True
    return False


def similarity_score(
    item: ValidatedQuizItem,
    *,
    existing_stems: Iterable[str],
) -> int:
    """0–100 where 100 = unique, 0 = near-duplicate."""
    stems = list(existing_stems)
    if not stems:
        return 100
    best = max((stem_similarity(item.stem, s) for s in stems), default=0.0)
    return max(0, min(100, int(round((1.0 - best) * 100))))
