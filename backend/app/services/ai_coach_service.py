"""
StudyOS — AI Coach Service (Sprint 33)
Generates personalized daily coaching analysis, progress insights, and recommended question count.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import AssessmentSession
from app.models.question_record import QuestionRecord
from app.models.user import User
from app.services.learning_profile_service import LearningProfileService


class AICoachDailyRead(BaseModel):
    greeting: str
    target_exam: str
    goal_progress_pct: float
    badge: str
    insights: list[str]
    recommended_question_count: int
    recommended_topics: list[str]


class AICoachService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_svc = LearningProfileService(db)

    async def get_daily_coaching(self, user_id: uuid.UUID) -> AICoachDailyRead:
        user = await self.db.get(User, user_id)
        name = (user.first_name if user else "") or "Öğrenci"

        exam, _, _ = await self.profile_svc.resolve_active_scope(user_id)
        exam = (exam or "kpss").upper()

        # 1. Fetch user targets
        targets = await self.profile_svc.repo.list_exam_targets(user_id)
        target_score = 85.0
        if targets:
            target_score = float(targets[0].target_score or targets[0].target_net or 85.0)

        # 2. Fetch last 5 assessment sessions
        stmt = (
            select(AssessmentSession)
            .where(
                AssessmentSession.user_id == user_id,
                AssessmentSession.status == "submitted",
            )
            .order_by(AssessmentSession.created_at.desc())
            .limit(5)
        )
        sessions = list((await self.db.execute(stmt)).scalars().all())

        accuracies = [float(s.accuracy or 0) for s in sessions if s.accuracy is not None]
        avg_acc = (sum(accuracies) / len(accuracies)) if accuracies else 0.50
        est_score = round(avg_acc * 100.0, 1)

        progress_pct = min(100.0, round((est_score / target_score) * 100.0, 1))

        if progress_pct >= 85:
            badge = "🥇 Derece Adayı"
        elif progress_pct >= 65:
            badge = "🥈 Altın Hedef"
        elif progress_pct >= 40:
            badge = "🥉 Gümüş İlerleme"
        else:
            badge = "🌱 Başlangıç Seviyesi"

        # 3. Generate dynamic insights
        insights = []

        # Check today's activity
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        qr_today = await self.db.execute(
            select(func.count()).select_from(QuestionRecord).where(
                QuestionRecord.user_id == user_id,
                QuestionRecord.created_at >= today_start,
            )
        )
        today_count = qr_today.scalar() or 0

        if today_count == 0:
            insights.append("Bugün henüz soru çözmedin. Güne 15 soru çözerek başla!")
        else:
            insights.append(f"Bugün harika gittin, toplam {today_count} soru tamamladın!")

        if len(accuracies) >= 2:
            diff = accuracies[0] - accuracies[-1]
            if diff > 0.05:
                insights.append(f"Son denemelerinde {exam} başarın %{diff*100:.0f} yükseliyor! 🚀")
            elif diff < -0.05:
                insights.append(f"Son denemelerde hafif bir düşüş var (%{abs(diff)*100:.0f}), tekrar yapmalısın. 💡")

        insights.append(f"{exam} hedefine %{progress_pct:.0f} oranında yaklaştın!")
        insights.append("Bugün senin için 35 soru üretimi ve 1 konu tekrarı öneriyorum.")

        return AICoachDailyRead(
            greeting=f"Merhaba {name}! AI Koçun bugün seninle.",
            target_exam=exam,
            goal_progress_pct=progress_pct,
            badge=badge,
            insights=insights,
            recommended_question_count=35,
            recommended_topics=["Paragraf", "Matematik - Problemler"],
        )
