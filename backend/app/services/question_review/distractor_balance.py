"""Distractor balance checks (editor only — does not rewrite options)."""

from __future__ import annotations

from typing import Any


def analyze_distractor_balance(question: dict[str, Any]) -> dict[str, Any]:
    choices = {str(k).upper(): str(v).strip() for k, v in (question.get("choices") or {}).items()}
    correct = str(question.get("correct_key") or "A").upper()
    flags: list[str] = []
    score = 100

    if len(choices) < 4:
        flags.append("too_few_choices")
        score -= 30

    lengths = {k: len(v.split()) for k, v in choices.items()}
    if lengths:
        vals = list(lengths.values())
        spread = max(vals) - min(vals)
        if spread >= 10:
            flags.append("length_imbalance")
            score -= 15
        # Correct answer longest by far
        if correct in lengths:
            others = [v for k, v in lengths.items() if k != correct]
            if others and lengths[correct] >= max(others) + 6:
                flags.append("correct_is_longest")
                score -= 18

    # Duplicate options
    texts = [v.lower() for v in choices.values()]
    if len(texts) != len(set(texts)):
        flags.append("duplicate_options")
        score -= 35

    # Near-duplicate
    for i, a in enumerate(texts):
        for b in texts[i + 1 :]:
            if a and b and (a in b or b in a) and abs(len(a) - len(b)) <= 8:
                flags.append("near_duplicate_options")
                score -= 12
                break

    # Obviously silly distractors
    silly = ("asdf", "???", "yok", "hepsi yanlış", "hiçbiri", "lorem")
    for k, v in choices.items():
        low = v.lower()
        if any(s in low for s in silly) or len(v) <= 1:
            flags.append(f"silly_option:{k}")
            score -= 20

    # Correct key missing
    if correct not in choices:
        flags.append("correct_key_missing")
        score -= 40

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "lengths": lengths,
        "passed": score >= 70,
    }
