"""Adaptive Calibration — adjust remaining plans from early accuracy.

Does NOT touch Decision Engine. Only difficulty / bloom / skill band for QIE plans.
"""

from __future__ import annotations

from app.services.qie.calibration_planner import (
    CalibrationPlanner,
    resolve_skill_catalog,
)
from app.services.qie.planner import _bloom_for
from app.services.qie.types import QuestionPlan


def adapt_difficulty_band(early_accuracy: float) -> tuple[str, int]:
    """Return (band, difficulty_override) from first-batch accuracy 0–1."""
    acc = max(0.0, min(1.0, float(early_accuracy)))
    if acc >= 0.85:
        return "hard", 88
    if acc >= 0.65:
        return "hard", 80
    if acc >= 0.45:
        return "medium", 68
    if acc >= 0.25:
        return "easy", 52
    return "easy", 40


class AdaptiveCalibrationPlanner:
    """Plan remaining calibration slots after first N answers."""

    def __init__(self) -> None:
        self._base = CalibrationPlanner()

    def plan_remaining(
        self,
        *,
        exam: str,
        subject_code: str,
        subject_name: str,
        topic_code: str,
        topic_name: str,
        total_count: int,
        already_done: int,
        used_skills: list[str],
        early_accuracy: float,
        choice_count: int = 5,
        paragraph_length: int = 180,
        reading_time_sec: int = 75,
    ) -> list[QuestionPlan]:
        remaining = max(0, total_count - already_done)
        if remaining <= 0:
            return []

        band, diff_override = adapt_difficulty_band(early_accuracy)
        catalog = resolve_skill_catalog(exam, subject_code)
        used = set(used_skills)
        # Prefer unused skills; if accuracy low, bias toward foundational skills
        foundational = {
            "vocabulary",
            "grammar",
            "spelling",
            "punctuation",
            "sentence_meaning",
        }
        advanced = {
            "main_idea",
            "supporting_idea",
            "paragraph_completion",
            "sentence_ordering",
            "logic",
            "mixed_reasoning",
            "coherence",
        }

        ordered = [s for s in catalog if s["skill"] not in used]
        if early_accuracy < 0.4:
            ordered = sorted(
                ordered,
                key=lambda s: (0 if s["skill"] in foundational else 1, s["skill"]),
            )
        elif early_accuracy >= 0.75:
            ordered = sorted(
                ordered,
                key=lambda s: (0 if s["skill"] in advanced else 1, s["skill"]),
            )

        if len(ordered) < remaining:
            # wrap unused then any
            for s in catalog:
                if s not in ordered:
                    ordered.append(s)

        slice_ = ordered[:remaining]
        plans = self._base.plan(
            exam=exam,
            subject_code=subject_code,
            subject_name=subject_name,
            topic_code=topic_code,
            topic_name=topic_name,
            count=remaining,
            difficulty_band=band,
            choice_count=choice_count,
            paragraph_length=paragraph_length,
            reading_time_sec=reading_time_sec,
            start_index=already_done,
            skill_slice=slice_,
            difficulty_override=diff_override,
        )
        for p in plans:
            p.bloom = _bloom_for(p.difficulty)
            p.pack = "adaptive_calibration"
        return plans
