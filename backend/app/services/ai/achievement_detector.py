"""
Sprint 20 — Win detection (kutlama).
Yeni achievement yazmaz; mevcut achievement + confidence/streak okur.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.coach import CoachWin
from app.services.achievement_service import AchievementService
from app.services.ai_insights_service import AiInsightsService


class AchievementDetector:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.achievements = AchievementService(db)
        self.insights = AiInsightsService(db)

    async def detect_wins(self, user_id: uuid.UUID) -> list[CoachWin]:
        wins: list[CoachWin] = []
        try:
            summary = await self.achievements.dashboard_summary(user_id)
            if summary.recent_title:
                wins.append(
                    CoachWin(
                        code="recent_achievement",
                        title=summary.recent_title,
                        message=summary.recent_reason
                        or "Bu başarını fark ettim — devam.",
                    )
                )
        except Exception:
            pass

        try:
            overview = await self.insights.get_overview(user_id)
            if overview.streak_days >= 5:
                wins.append(
                    CoachWin(
                        code="streak_5",
                        title=f"{overview.streak_days} günlük seri",
                        message="Üst üste çalışma alışkanlığın güçleniyor.",
                    )
                )
            if overview.correct_rate >= 75 and overview.has_enough_data:
                wins.append(
                    CoachWin(
                        code="accuracy_high",
                        title="Yüksek doğruluk",
                        message=f"Genel doğruluk %{overview.correct_rate:.0f} — güçlü sinyal.",
                    )
                )
        except Exception:
            pass

        # Confidence HIGH — read-only from trends if available
        try:
            from app.services.learning_intelligence_service import (
                LearningIntelligenceService,
            )

            trends = await LearningIntelligenceService(self.db).journey_trends(
                user_id
            )
            rising = trends.rising or []
            high = [
                t
                for t in rising
                if (t.confidence_level or "").lower() == "high"
            ]
            if high:
                t0 = high[0]
                wins.append(
                    CoachWin(
                        code="confidence_high",
                        title="HIGH Confidence",
                        message=(
                            f"{t0.topic_name or t0.topic_code}: "
                            "İlk kez veya yeniden yüksek güvene ulaştın."
                        ),
                    )
                )
        except Exception:
            pass

        # Deduplicate by code
        seen: set[str] = set()
        out: list[CoachWin] = []
        for w in wins:
            if w.code in seen:
                continue
            seen.add(w.code)
            out.append(w)
        return out[:3]
