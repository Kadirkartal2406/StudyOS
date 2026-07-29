"""P4 — Question Uniqueness via semantic similarity."""
from __future__ import annotations
import re
from typing import Any
from app.services.question_intelligence.types import UniquenessResult

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", re.UNICODE)
_STOP_WORDS = frozenset({
    "ve", "ile", "bir", "bu", "da", "de", "için", "olan", "olarak",
    "gibi", "en", "çok", "her", "daha", "ya", "ki", "ne", "mi",
    "mu", "mı", "mü", "ise", "hem", "ama", "fakat", "ancak",
    "veya", "ya da", "den", "dan", "dir", "dır", "dür", "dur",
    "nin", "nın", "nün", "nun", "ın", "in", "un", "ün",
})

def _normalize(text: str) -> set[str]:
    """Extract meaningful words from text."""
    words = _WORD_RE.findall(text.lower())
    return {w for w in words if w not in _STOP_WORDS and len(w) > 2}

def _trigrams(text: str) -> set[str]:
    """Character trigrams for fuzzy matching."""
    clean = re.sub(r"\s+", " ", text.lower().strip())
    return {clean[i:i+3] for i in range(len(clean) - 2)} if len(clean) >= 3 else set()

def _similarity(stem_a: str, stem_b: str) -> float:
    """Jaccard + trigram hybrid similarity (0-1)."""
    words_a = _normalize(stem_a)
    words_b = _normalize(stem_b)
    
    # Word-level Jaccard
    if words_a or words_b:
        word_sim = len(words_a & words_b) / max(len(words_a | words_b), 1)
    else:
        word_sim = 0.0
    
    # Trigram similarity
    tri_a = _trigrams(stem_a)
    tri_b = _trigrams(stem_b)
    if tri_a or tri_b:
        tri_sim = len(tri_a & tri_b) / max(len(tri_a | tri_b), 1)
    else:
        tri_sim = 0.0
    
    # Weighted combination
    return 0.6 * word_sim + 0.4 * tri_sim


def check_uniqueness(
    stem: str,
    existing_stems: list[str],
    threshold: float = 0.55,
    max_check: int = 10000,
) -> UniquenessResult:
    """Check if a question stem is unique among existing stems."""
    if not existing_stems:
        return UniquenessResult(is_unique=True, similarity_score=0.0, checked_count=0)
    
    stems_to_check = existing_stems[-max_check:] if len(existing_stems) > max_check else existing_stems
    
    max_sim = 0.0
    most_similar: str | None = None
    
    for existing in stems_to_check:
        sim = _similarity(stem, existing)
        if sim > max_sim:
            max_sim = sim
            most_similar = existing
    
    return UniquenessResult(
        is_unique=max_sim < threshold,
        most_similar_stem=most_similar if max_sim >= threshold * 0.8 else None,
        similarity_score=round(max_sim, 4),
        checked_count=len(stems_to_check),
    )
