"""
Sprint 20 — Weekly reflection (Journey).
Yeni Decision yok; trends + performance okur.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.coach import CoachWin, WeeklyReflection
from app.services.ai.achievement_detector import AchievementDetector
from app.services.ai_insights_service import AiInsightsService


class WeeklyReflectionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.insights = AiInsightsService(db)
        self.wins = AchievementDetector(db)

    async def build(self, user_id: uuid.UUID) -> WeeklyReflection:
        trends = await self.insights.get_trends(user_id)
        perf = await self.insights.get_performance(user_id)
        wins = await self.wins.detect_wins(user_id)

        q = trends.weekly_questions
        mins = trends.weekly_study_minutes
        delta = trends.questions_delta_pct

        if delta is None:
            conf_label = None
        elif delta >= 10:
            conf_label = f"Soru hacmi %{delta:.0f} arttı"
        elif delta <= -10:
            conf_label = f"Soru hacmi %{abs(delta):.0f} azaldı"
        else:
            conf_label = "Soru temposu dengeli"

        strongest = None
        weakest = None
        if perf.subjects_by_accuracy:
            # value is % (0–100); only call out weak below 70
            weak_rows = [m for m in perf.subjects_by_accuracy if m.value < 70]
            strong_rows = [m for m in perf.subjects_by_accuracy if m.value >= 85]
            if weak_rows:
                weakest = min(weak_rows, key=lambda m: m.value).label
            if strong_rows:
                strongest = max(strong_rows, key=lambda m: m.value).label
            elif perf.subjects_by_accuracy:
                strongest = perf.subjects_by_accuracy[-1].label

        if weakest and strongest and weakest != strongest:
            suggestion = (
                f"Haftanın önerisi: {weakest} için hedefe yaklaştıran kısa revision + quiz; "
                f"{strongest} ritmini koru."
            )
        elif weakest:
            suggestion = f"Haftanın önerisi: {weakest} hedefine yaklaşmak için 2 kısa oturum."
        else:
            suggestion = (
                "Haftanın önerisi: Her gün 20 dk tutarlı oturum — "
                "Coach seni buradan takip edecek."
            )

        body = (
            f"Bu hafta {q} soru çözdün ve {mins} dk çalıştın. "
            + (f"{conf_label}. " if conf_label else "")
            + (
                f"En çok gelişen alan: {strongest}. "
                if strongest
                else ""
            )
            + (
                f"Hedefe en uzak: {weakest}. "
                if weakest and weakest != strongest
                else ""
            )
            + suggestion
        )

        return WeeklyReflection(
            questions_solved=q,
            study_minutes=mins,
            confidence_delta_label=conf_label,
            strongest_topic=strongest,
            weakest_topic=weakest,
            weekly_suggestion=suggestion,
            wins=wins,
            body=body,
        )
