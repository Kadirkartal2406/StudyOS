"""Answer validity — single correct, no colliding options."""

from __future__ import annotations

from typing import Any


def verify_answer(question: dict[str, Any]) -> dict[str, Any]:
    choices = {str(k).upper(): str(v).strip() for k, v in (question.get("choices") or {}).items()}
    correct = str(question.get("correct_key") or "").upper()
    flags: list[str] = []
    score = 100

    if not correct or correct not in choices:
        flags.append("invalid_correct_key")
        score -= 50

    # Exact duplicates imply multiple correct
    values = list(choices.values())
    lower = [v.lower() for v in values]
    if correct in choices:
        ctext = choices[correct].lower()
        twins = [k for k, v in choices.items() if k != correct and v.lower() == ctext]
        if twins:
            flags.append("duplicate_correct_text")
            score -= 45

    # Substring collision: option contains another fully
    items = list(choices.items())
    for i, (ka, va) in enumerate(items):
        for kb, vb in items[i + 1 :]:
            a, b = va.lower().strip(), vb.lower().strip()
            if not a or not b:
                continue
            if a == b:
                flags.append(f"identical:{ka}/{kb}")
                score -= 40
            elif len(a) > 12 and len(b) > 12 and (a in b or b in a):
                flags.append(f"overlapping:{ka}/{kb}")
                score -= 15

    if len(set(lower)) < len(lower):
        flags.append("non_unique_options")
        score = min(score, 55)

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "single_correct": "duplicate_correct_text" not in flags
        and "invalid_correct_key" not in flags,
        "passed": score >= 70,
    }
