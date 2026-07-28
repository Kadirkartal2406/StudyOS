"""
StudyOS — Spaced Repetition Rule Engine (SM-2 lite)
Sprint-2.8 — LLM difficulty/interval'a dokunmaz.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import (
    REVISION_DEFAULT_DIFFICULTY,
    REVISION_DEFAULT_EASE,
    REVISION_MAX_DIFFICULTY,
    REVISION_MAX_EASE,
    REVISION_MIN_DIFFICULTY,
    REVISION_MIN_EASE,
)
from app.models.revision import RevisionGrade


@dataclass(frozen=True)
class Sm2Result:
    interval_days: int
    ease_factor: float
    repetition_count: int
    lapse_count: int
    difficulty: int


def clamp_difficulty(value: int) -> int:
    return max(REVISION_MIN_DIFFICULTY, min(REVISION_MAX_DIFFICULTY, value))


def clamp_ease(value: float) -> float:
    return max(REVISION_MIN_EASE, min(REVISION_MAX_EASE, value))


def apply_sm2_lite(
    *,
    grade: RevisionGrade,
    interval_days: int,
    ease_factor: float,
    repetition_count: int,
    lapse_count: int,
    difficulty: int,
) -> Sm2Result:
    """
    SM-2 lite:
    - again → reset reps, interval=1, ease↓, difficulty↑
    - hard → interval * 1.2, ease↓
    - good → classic SM-2 interval growth
    - easy → faster growth, ease↑, difficulty↓
    """
    ease = ease_factor or REVISION_DEFAULT_EASE
    diff = difficulty or REVISION_DEFAULT_DIFFICULTY
    interval = max(1, interval_days)
    reps = repetition_count
    lapses = lapse_count

    if grade == RevisionGrade.AGAIN:
        lapses += 1
        reps = 0
        interval = 1
        ease = clamp_ease(ease - 0.20)
        diff = clamp_difficulty(diff + 1)
    elif grade == RevisionGrade.HARD:
        reps += 1
        interval = max(1, int(round(interval * 1.2)))
        ease = clamp_ease(ease - 0.15)
        # difficulty unchanged or slight bump if already high reps failing soft
        if interval <= 2:
            diff = clamp_difficulty(diff + 0)
    elif grade == RevisionGrade.GOOD:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        else:
            interval = max(1, int(round(interval * ease)))
        reps += 1
        if reps >= 3 and diff > REVISION_DEFAULT_DIFFICULTY:
            diff = clamp_difficulty(diff - 1)
    else:  # EASY
        if reps == 0:
            interval = 3
        elif reps == 1:
            interval = 7
        else:
            interval = max(1, int(round(interval * ease * 1.3)))
        reps += 1
        ease = clamp_ease(ease + 0.15)
        diff = clamp_difficulty(diff - 1)

    return Sm2Result(
        interval_days=interval,
        ease_factor=ease,
        repetition_count=reps,
        lapse_count=lapses,
        difficulty=diff,
    )


def initial_reason_for_subject(
    subject: str,
    *,
    source: str,
    accuracy: float | None = None,
    net: float | None = None,
    target_net: float | None = None,
) -> str:
    if accuracy is not None:
        return (
            f"{subject} doğruluk oranı %{accuracy:.0f} — spaced repetition ile güçlendirilmeli."
        )
    if net is not None and target_net is not None:
        gap = target_net - net
        if gap > 0:
            return (
                f"{subject} deneme neti {net:.1f}; hedef {target_net:.1f} "
                f"(hedefe {gap:.1f} net var) — tekrar kuyruğuna alındı."
            )
        return (
            f"{subject} deneme neti {net:.1f} (hedef {target_net:.1f}) — "
            "bakım tekrarı için eklendi."
        )
    if net is not None:
        return (
            f"{subject} deneme neti {net:.1f} — hedefe yaklaşmak için tekrar kuyruğuna alındı."
        )
    if source == "manual":
        return f"{subject} manuel olarak yanlış defterine eklendi."
    return f"{subject} kural motoru tarafından tekrar için seçildi."
