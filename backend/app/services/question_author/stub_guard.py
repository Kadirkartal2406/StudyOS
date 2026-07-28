"""Detect offline Author stub templates so they never ship as real questions."""

from __future__ import annotations

from typing import Any

# Phrases unique to question_writer._stub_question / distractor fallbacks
_STUB_STEM_MARKERS = (
    "bloom düzeyi",
    "ölçülen kazanım",
    "okuma süresi yaklaşık",
    "kelimelik resmi bir üslup",
    "günlük yaşamdan bir durumu anlatan kısa bir metin düşününüz",
)

_STUB_CHOICE_MARKERS = (
    "doğru yanıt —",
    "doğru yanıt -",
    "çeldirici ",
    "içeren çeldirici",
)


class AuthorLLMError(RuntimeError):
    """Raised when use_llm=True but the model did not produce a usable question."""


def looks_like_author_stub(
    stem: str | None = None,
    choices: dict[str, Any] | None = None,
) -> bool:
    text = (stem or "").lower()
    if any(m in text for m in _STUB_STEM_MARKERS):
        return True
    if not choices:
        return False
    joined = " ".join(str(v) for v in choices.values()).lower()
    stub_hits = sum(1 for m in _STUB_CHOICE_MARKERS if m in joined)
    # Multiple labeled placeholders → definitely stub
    if stub_hits >= 2:
        return True
    # Correct-label + at least one Çeldirici trap name
    if "doğru yanıt" in joined and "çeldirici" in joined:
        return True
    return False
