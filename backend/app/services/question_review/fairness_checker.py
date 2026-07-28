"""Fairness checker — cueing, length bias, key bias patterns."""

from __future__ import annotations

from typing import Any


def check_fairness(
    question: dict[str, Any],
    *,
    recent_correct_keys: list[str] | None = None,
) -> dict[str, Any]:
    choices = {str(k).upper(): str(v) for k, v in (question.get("choices") or {}).items()}
    correct = str(question.get("correct_key") or "A").upper()
    stem = str(question.get("stem") or "").lower()
    flags: list[str] = []
    score = 100

    # Cue words in correct option mirrored in stem
    if correct in choices:
        cwords = set(w for w in choices[correct].lower().split() if len(w) >= 5)
        overlap = [w for w in cwords if w in stem]
        if len(overlap) >= 3:
            flags.append("stem_cues_correct")
            score -= 18

    # Always-positive correct vs negative distractors
    pos = ("en uygun", "doğru", "geçerlidir", "anlaşılır")
    neg = ("değildir", "yanlış", "olamaz", "anlamsız")
    if correct in choices:
        cl = choices[correct].lower()
        if any(p in cl for p in pos):
            neg_count = sum(
                1
                for k, v in choices.items()
                if k != correct and any(n in v.lower() for n in neg)
            )
            if neg_count >= max(1, len(choices) - 2):
                flags.append("polarity_cue")
                score -= 12

    # Correct key always C pattern in recent history
    recent = [str(k).upper() for k in (recent_correct_keys or [])]
    if len(recent) >= 3 and all(k == correct for k in recent[-3:]):
        flags.append("repeated_correct_key")
        score -= 20

    # Length cue already partly in distractor_balance; light touch here
    lengths = {k: len(v.split()) for k, v in choices.items()}
    if correct in lengths and lengths:
        if lengths[correct] == max(lengths.values()) and lengths[correct] >= 6:
            flags.append("longest_answer_bias")
            score -= 10

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "passed": score >= 70,
    }
