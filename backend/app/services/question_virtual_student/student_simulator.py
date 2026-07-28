"""Simulate each virtual student solving a question (heuristic, no generation)."""

from __future__ import annotations

import hashlib
from typing import Any

from app.services.question_virtual_student.distractor_attraction import (
    rank_distractor_attraction,
)
from app.services.question_virtual_student.profiles import StudentProfile
from app.services.question_virtual_student.types import StudentAttempt


def _stable_unit(seed: str) -> float:
    h = hashlib.sha1(seed.encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _as_question(question: Any) -> dict[str, Any]:
    if isinstance(question, dict):
        return {
            "stem": str(question.get("stem") or ""),
            "choices": {str(k).upper(): str(v) for k, v in (question.get("choices") or {}).items()},
            "correct_key": str(question.get("correct_key") or "A").upper(),
        }
    return {
        "stem": str(getattr(question, "stem", "") or ""),
        "choices": {
            str(k).upper(): str(v)
            for k, v in (getattr(question, "choices", {}) or {}).items()
        },
        "correct_key": str(getattr(question, "correct_key", "A") or "A").upper(),
    }


def simulate_student(
    question: Any,
    profile: StudentProfile,
) -> StudentAttempt:
    q = _as_question(question)
    stem = q["stem"]
    choices = q["choices"]
    correct = q["correct_key"]
    keys = sorted(choices.keys())
    if not keys:
        return StudentAttempt(
            profile=profile.name,
            chosen_option="A",
            confidence=0.2,
            reasoning="no_choices",
            reading_time_sec=5.0,
            thinking_time_sec=5.0,
            correct=False,
        )

    words = max(1, len(stem.split()))
    reading = (words / 160.0) * 60.0 / max(profile.speed, 0.4)
    thinking = 8.0 + words * 0.04 * (1.0 + profile.overthink)
    if profile.prefers_rules:
        thinking *= 0.9
    if profile.prefers_inference:
        thinking *= 1.15

    attractions = rank_distractor_attraction(q)
    top_wrong = next((a for a in attractions if a.option != correct), None)
    roll = _stable_unit(f"{profile.name}|{stem[:80]}|{correct}")

    # Accuracy tendency vs carelessness / overthink traps
    picks_correct = roll < profile.skill * (1.0 - 0.35 * profile.carelessness)
    if profile.overthink > 0.5 and top_wrong and top_wrong.attraction_score >= 0.55:
        if roll > 0.45:
            picks_correct = False

    if picks_correct and correct in choices:
        chosen = correct
        conf = 0.55 + 0.4 * profile.skill
        reasoning = "matched_stem_to_correct"
        confused = None
        attractive = top_wrong.option if top_wrong else None
    else:
        if top_wrong and (profile.carelessness > 0.25 or profile.overthink > 0.4):
            chosen = top_wrong.option
            reasoning = top_wrong.reason
            attractive = top_wrong.option
            confused = "attractive_distractor"
        else:
            # pick pseudo-random wrong
            wrongs = [k for k in keys if k != correct] or keys
            idx = int(_stable_unit(f"wrong|{profile.name}|{stem[:40]}") * len(wrongs)) % len(
                wrongs
            )
            chosen = wrongs[idx]
            reasoning = "uncertain_elimination"
            attractive = chosen
            confused = "option_similarity"
        conf = 0.25 + 0.35 * (1.0 - profile.skill)

    return StudentAttempt(
        profile=profile.name,
        chosen_option=chosen,
        confidence=round(min(0.99, max(0.05, conf)), 3),
        reasoning=reasoning,
        reading_time_sec=round(reading, 1),
        thinking_time_sec=round(thinking, 1),
        confused_at=confused,
        attractive_distractor=attractive,
        correct=(chosen == correct),
    )


def simulate_all(question: Any, profiles: list[StudentProfile]) -> list[StudentAttempt]:
    return [simulate_student(question, p) for p in profiles]
