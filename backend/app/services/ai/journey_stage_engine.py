"""
StudyOS — Journey Stage RuleEngine (Sprint-3.0 M1)
LLM journey_stage değiştirmez.
"""

from __future__ import annotations

from app.models.learning_profile import JourneyStage


def evaluate_journey_stage(
    *,
    onboarding_completed: bool,
    onboarding_skipped: bool,
    has_exam_targets: bool,
    streak_days: int,
    total_study_minutes: int,
    exam_count: int,
    question_count: int,
) -> JourneyStage:
    """Deterministik stage — metrics'ten türetilir."""
    if not onboarding_completed and not onboarding_skipped:
        if has_exam_targets:
            return JourneyStage.ONBOARDING
        return JourneyStage.NEW_USER

    # Advanced: zengin veri + süreklilik
    if exam_count >= 5 and streak_days >= 14 and total_study_minutes >= 2000:
        return JourneyStage.ADVANCED

    # Consistent: düzenli çalışma
    if streak_days >= 7 or (total_study_minutes >= 600 and question_count >= 100):
        return JourneyStage.CONSISTENT

    return JourneyStage.LEARNING


def build_stage_reason(stage: JourneyStage) -> str:
    return {
        JourneyStage.NEW_USER: "Profil henüz tamamlanmadı",
        JourneyStage.ONBOARDING: "Onboarding devam ediyor",
        JourneyStage.LEARNING: "Öğrenme yolculuğu başladı",
        JourneyStage.CONSISTENT: "Düzenli çalışma alışkanlığı oluşuyor",
        JourneyStage.ADVANCED: "İleri seviye veri ve süreklilik",
    }[stage]
