"""Quality Gate v2 — composite 0–100; below 85 must not reach users."""

from __future__ import annotations

import re
from typing import Any

from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.qie.similarity import similarity_score
from app.services.qie.types import (
    MIN_QUALITY_SCORE,
    QualityBreakdown,
    QuestionPlan,
)

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", re.UNICODE)


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")


def score_quality(
    item: ValidatedQuizItem,
    plan: QuestionPlan,
    *,
    difficulty_score: int,
    existing_stems: list[str] | None = None,
    style_dna: dict[str, Any] | None = None,
) -> QualityBreakdown:
    style_dna = style_dna or {}
    existing_stems = existing_stems or []

    is_reading = any(
        k in (plan.topic_name or "").lower() or k in (plan.topic_code or "").lower()
        for k in ("paragraf", "anlam", "okuma", "reading", "clozer", "passage", "metin")
    )
    stem_n = len(_words(item.stem))
    target = plan.paragraph_length or (160 if is_reading else 40)
    # Style: length vs DNA/plan
    if abs(stem_n - target) <= target * 0.50:
        style = 90
    elif abs(stem_n - target) <= target * 0.80:
        style = 75
    else:
        style = 65

    # Difficulty channel
    difficulty = max(0, min(100, difficulty_score))

    # Similarity (unique is good)
    similarity = similarity_score(item, existing_stems=existing_stems)

    # Grammar / formal tone proxy
    low = (item.stem or "").lower()
    grammar = 88
    if any(x in low for x in ("chatgpt", "as an ai", "tabii ki", "😊")):
        grammar = 30
    if len(item.stem.strip()) < 12:
        grammar = min(grammar, 40)

    # Option balance
    lens = [len(_words(str(v))) for v in (item.choices or {}).values()]
    if lens and (max(lens) - min(lens)) <= max(6, int(sum(lens) / len(lens))):
        option_balance = 90
    elif lens:
        option_balance = 65
    else:
        option_balance = 20

    # Distractor quality: no duplicates, not empty
    norms = {re.sub(r"\s+", " ", str(v).strip().lower()) for v in (item.choices or {}).values()}
    distractor_quality = 88
    if len(norms) < len(item.choices or {}):
        distractor_quality = 25
    if any(not str(v).strip() for v in (item.choices or {}).values()):
        distractor_quality = 20

    # Blueprint match: choice count + stem type intent
    expect = plan.choice_count
    blueprint_match = 92 if len(item.choices or {}) == expect else 40
    if plan.stem_type in ("main_idea", "paragraph_completion", "sentence_ordering"):
        if stem_n < 40:
            blueprint_match = min(blueprint_match, 60)

    # Reading time proxy from length
    reading_time = 85
    if is_reading and plan.reading_time_sec >= 70 and stem_n < 50:
        reading_time = 55
    elif plan.reading_time_sec <= 45 and stem_n > 220:
        reading_time = 60

    # Exam feel: formal + self-contained
    exam_feel = 80
    if any(
        p in low
        for p in ("yukarıdaki paragraf", "verilen tablo", "yukarıdaki şekil")
    ) and stem_n < 50:
        exam_feel = 35
    if style_dna.get("wording_style") or style_dna.get("vocabulary_level"):
        exam_feel = min(100, exam_feel + 5)
    if difficulty >= 70 and option_balance >= 80:
        exam_feel = min(100, exam_feel + 5)

    return QualityBreakdown(
        style=style,
        difficulty=difficulty,
        similarity=similarity,
        grammar=grammar,
        option_balance=option_balance,
        distractor_quality=distractor_quality,
        blueprint_match=blueprint_match,
        reading_time=reading_time,
        exam_feel=exam_feel,
    )


def passes_quality_gate(breakdown: QualityBreakdown) -> bool:
    return breakdown.total >= MIN_QUALITY_SCORE
