"""Heuristic difficulty 0–100 — no AI."""

from __future__ import annotations

from app.services.exam_intelligence.parser.question_locator import LocatedQuestion


def estimate_difficulty(q: LocatedQuestion) -> int:
    score = 40
    # Length / reading load
    if q.word_count >= 180:
        score += 22
    elif q.word_count >= 120:
        score += 16
    elif q.word_count >= 70:
        score += 10
    elif q.word_count < 25:
        score -= 8

    if q.sentence_count >= 8:
        score += 8
    elif q.sentence_count >= 5:
        score += 4

    if q.equation_count >= 2:
        score += 12
    elif q.equation_count == 1:
        score += 6

    if q.symbol_count >= 3:
        score += 6

    if q.option_lengths:
        spread = max(q.option_lengths) - min(q.option_lengths)
        avg = sum(q.option_lengths) / len(q.option_lengths)
        if avg >= 10:
            score += 5
        if spread <= 4 and avg >= 6:
            score += 4  # balanced hard distractors proxy

    if q.multi_step:
        score += 10
    if q.has_table or q.has_visual_hint:
        score += 6

    return max(5, min(98, int(score)))
