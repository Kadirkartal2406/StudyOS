"""Sprint 23 — Question Difficulty / Style Analyzer (post-LLM, pre-user).

Heuristic + style-profile checks. Score 0–100; <70 → regenerate.
No LLM call — cheap and deterministic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.services.ai.quiz_quality_gate import ValidatedQuizItem


@dataclass
class DifficultyScore:
    score: int
    passed: bool
    reasons: list[str]


_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", re.UNICODE)


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")


def _looks_textbook(stem: str) -> bool:
    low = (stem or "").lower()
    bad = (
        "aşağıdakilerden hangisi doğrudur",
        "hangisi yanlıştır",
        "chatgpt",
        "örnek olarak şöyle",
        "basitçe söylemek gerekirse",
    )
    # "hangisi" alone is ok for exams; textbook combo with very short stem is bad
    if len(_words(stem)) < 18 and any(b in low for b in bad[:2]):
        return True
    return any(b in low for b in bad[2:])


def analyze_question_difficulty(
    item: ValidatedQuizItem,
    *,
    style: dict[str, Any] | None = None,
    topic_name: str | None = None,
) -> DifficultyScore:
    """Score one question against style targets."""
    style = style or {}
    reasons: list[str] = []
    score = 55  # baseline if schema-valid

    stem = item.stem or ""
    w = _words(stem)
    n = len(w)
    choices = item.choices or {}

    # Length bands
    para_range = str(style.get("paragraph_words") or "40-200")
    try:
        pmin_s, pmax_s = para_range.split("-", 1)
        pmin, pmax = int(pmin_s), int(pmax_s)
    except Exception:
        pmin, pmax = 40, 200

    # Reading / paragraph skills prefer longer stems
    want_long = any(
        k in (topic_name or "").lower()
        for k in ("paragraf", "anlam", "okuma", "reading", "clozer", "passage", "metin")
    ) or (style.get("reasoning_type") or "") in ("paragraph_inference", "paragraph_reading")

    if want_long:
        if n >= pmin:
            score += 15
            reasons.append("paragraph_length_ok")
        elif n >= max(30, pmin // 2):
            score += 5
            reasons.append("paragraph_length_partial")
        else:
            score -= 20
            reasons.append("paragraph_too_short")
    else:
        if 12 <= n <= 120:
            score += 10
            reasons.append("stem_length_ok")
        elif n < 8:
            score -= 15
            reasons.append("stem_too_short")

    # Option balance
    lens = [len(_words(str(v))) for v in choices.values()]
    if lens:
        avg = sum(lens) / len(lens)
        spread = max(lens) - min(lens)
        if spread <= max(8, avg):
            score += 10
            reasons.append("options_balanced")
        else:
            score -= 8
            reasons.append("options_imbalanced")
        if min(lens) == 0:
            score -= 20
            reasons.append("empty_option")

    # Guessability: correct much shorter/longer
    correct = (item.correct_key or "A").upper()
    if correct in choices and lens:
        c_len = len(_words(str(choices[correct])))
        others = [len(_words(str(choices[k]))) for k in choices if k != correct]
        if others and c_len <= 1 and max(others) >= 6:
            score -= 15
            reasons.append("correct_too_obvious_short")

    # Distractor strength proxy: options not near-identical
    norms = {k: re.sub(r"\s+", " ", str(v).strip().lower()) for k, v in choices.items()}
    vals = list(norms.values())
    if len(vals) != len(set(vals)):
        score -= 25
        reasons.append("duplicate_options")

    if _looks_textbook(stem):
        score -= 18
        reasons.append("textbook_wording")

    # Self-contained: dangling references
    low = stem.lower()
    if any(
        p in low
        for p in (
            "yukarıdaki paragraf",
            "aşağıdaki metin",
            "verilen tablo",
            "yukarıdaki şekil",
        )
    ) and n < 40:
        score -= 25
        reasons.append("dangling_reference")

    # Style difficulty preference
    band = (style.get("difficulty") or "").lower()
    if band in ("high", "zor", "hard") and n < 20 and want_long:
        score -= 10
        reasons.append("too_easy_for_high_band")

    score = max(0, min(100, score))
    return DifficultyScore(score=score, passed=score >= 70, reasons=reasons)


def filter_by_difficulty(
    items: list[ValidatedQuizItem],
    *,
    style: dict[str, Any] | None = None,
    topic_name: str | None = None,
    min_score: int = 70,
) -> tuple[list[ValidatedQuizItem], list[DifficultyScore]]:
    kept: list[ValidatedQuizItem] = []
    scores: list[DifficultyScore] = []
    for it in items:
        s = analyze_question_difficulty(it, style=style, topic_name=topic_name)
        scores.append(s)
        if s.score >= min_score:
            kept.append(it)
    return kept, scores
