"""Sprint 23 M23.5 — Near-duplicate stem checker (n-gram Jaccard).

No embeddings — cheap beta gate after difficulty filter.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

from app.services.ai.quiz_quality_gate import ValidatedQuizItem

_WORD_RE = re.compile(r"[a-z0-9ğüşıöç]+", re.UNICODE)

# Turkish-ish fold map for cheap normalize
_TR_MAP = str.maketrans(
    {
        "İ": "i",
        "I": "i",
        "ı": "i",
        "Ş": "s",
        "ş": "s",
        "Ğ": "g",
        "ğ": "g",
        "Ü": "u",
        "ü": "u",
        "Ö": "o",
        "ö": "o",
        "Ç": "c",
        "ç": "c",
    }
)


def normalize_stem(text: str) -> str:
    t = (text or "").translate(_TR_MAP)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.lower()
    return " ".join(_WORD_RE.findall(t))


def _word_ngrams(words: list[str], n: int = 3) -> set[str]:
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def stem_similarity(a: str, b: str) -> float:
    """Jaccard similarity over word 3-grams (fallback 1-grams if short)."""
    wa = normalize_stem(a).split()
    wb = normalize_stem(b).split()
    if not wa or not wb:
        return 0.0
    n = 3 if min(len(wa), len(wb)) >= 6 else 1
    sa, sb = _word_ngrams(wa, n), _word_ngrams(wb, n)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def is_near_duplicate(
    stem: str,
    accepted_stems: Iterable[str],
    *,
    threshold: float = 0.72,
) -> bool:
    for other in accepted_stems:
        if stem_similarity(stem, other) >= threshold:
            return True
    return False


def filter_near_duplicates(
    items: list[ValidatedQuizItem],
    *,
    existing_stems: Iterable[str] | None = None,
    threshold: float = 0.72,
) -> list[ValidatedQuizItem]:
    """Drop near-duplicates vs existing + within-batch earlier items."""
    accepted: list[str] = list(existing_stems or [])
    kept: list[ValidatedQuizItem] = []
    for item in items:
        if is_near_duplicate(item.stem, accepted, threshold=threshold):
            continue
        kept.append(item)
        accepted.append(item.stem)
    return kept
