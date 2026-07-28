"""
StudyOS — AI Insights Service
InsightEngine + RuleEngine orkestrasyonu. Sprint-2.0 (Meeting-018).
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai_insights import (
    AiInsightMetric,
    AiOverviewResponse,
    AiPerformanceResponse,
    AiProductivityResponse,
    AiRecommendation,
    AiRecommendationsResponse,
    AiTrendPoint,
    AiTrendsResponse,
)
from app.services.ai.insight_engine import InsightEngine
from app.services.ai.rule_engine import RuleEngine


def _delta_pct(current: int, previous: int) -> float | None:
    if previous <= 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


class AiInsightsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.insight_engine = InsightEngine(db)
        self.rule_engine = RuleEngine()

    async def get_overview(self, user_id: uuid.UUID) -> AiOverviewResponse:
        ctx = await self.insight_engine.build_context(user_id)
        recs = self.rule_engine.generate(ctx)
        top = recs[0] if recs else None
        return AiOverviewResponse(
            has_enough_data=ctx.has_enough_data,
            streak_days=ctx.streak_days,
            average_daily_minutes=ctx.average_daily_minutes,
            average_daily_questions=ctx.average_daily_questions,
            most_studied_subject=ctx.most_studied_subject,
            least_studied_subject=ctx.least_studied_subject,
            most_questions_subject=ctx.most_questions_subject,
            correct_rate=ctx.correct_rate,
            pomodoro_completion_rate=ctx.pomodoro_completion_rate,
            most_productive_hour=ctx.most_productive_hour,
            least_productive_hour=ctx.least_productive_hour,
            idle_days_last_14=ctx.idle_days_last_14,
            top_recommendation=top,
            recommendations_count=len(recs),
        )

    async def get_recommendations(self, user_id: uuid.UUID) -> AiRecommendationsResponse:
        ctx = await self.insight_engine.build_context(user_id)
        items = self.rule_engine.generate(ctx)
        return AiRecommendationsResponse(items=items, has_enough_data=ctx.has_enough_data)

    async def get_top_recommendation(self, user_id: uuid.UUID) -> AiRecommendation | None:
        recs = await self.get_recommendations(user_id)
        return recs.items[0] if recs.items else None

    async def get_trends(self, user_id: uuid.UUID) -> AiTrendsResponse:
        ctx = await self.insight_engine.build_context(user_id)
        return AiTrendsResponse(
            weekly_study_minutes=ctx.week_study_minutes,
            previous_week_study_minutes=ctx.previous_week_study_minutes,
            study_minutes_delta_pct=_delta_pct(
                ctx.week_study_minutes, ctx.previous_week_study_minutes
            ),
            weekly_questions=ctx.weekly_questions,
            previous_week_questions=ctx.previous_week_questions,
            questions_delta_pct=_delta_pct(ctx.weekly_questions, ctx.previous_week_questions),
            monthly_study_minutes=ctx.month_study_minutes,
            previous_month_study_minutes=ctx.previous_month_study_minutes,
            daily_series=[
                AiTrendPoint(label=label, study_minutes=mins, question_count=qs)
                for label, mins, qs in ctx.daily_series
            ],
        )

    async def get_performance(self, user_id: uuid.UUID) -> AiPerformanceResponse:
        ctx = await self.insight_engine.build_context(user_id)
        by_acc = [
            AiInsightMetric(
                key=f"acc_{name}",
                label=name,
                value=round(rate, 1),
                unit="%",
            )
            for name, rate, _count in sorted(
                ctx.subjects_accuracy, key=lambda x: x[1]
            )[:10]
        ]
        by_q = [
            AiInsightMetric(
                key=f"q_{name}",
                label=name,
                value=count,
                unit="soru",
            )
            for name, count in ctx.subjects_questions[:10]
        ]
        return AiPerformanceResponse(
            correct_rate=ctx.correct_rate,
            wrong_rate=ctx.wrong_rate,
            total_net=ctx.total_net,
            total_questions=ctx.total_questions,
            subjects_by_accuracy=by_acc,
            subjects_by_questions=by_q,
            pomodoro_completion_rate=ctx.pomodoro_completion_rate,
            total_pomodoros=ctx.total_pomodoros,
        )

    async def get_productivity(self, user_id: uuid.UUID) -> AiProductivityResponse:
        ctx = await self.insight_engine.build_context(user_id)
        return AiProductivityResponse(
            most_productive_hour=ctx.most_productive_hour,
            least_productive_hour=ctx.least_productive_hour,
            most_productive_weekday_label=ctx.most_productive_weekday_label,
            hour_minutes=ctx.hour_minutes,
            weekday_minutes=ctx.weekday_minutes,
            streak_days=ctx.streak_days,
            idle_days_last_14=ctx.idle_days_last_14,
            average_daily_minutes=ctx.average_daily_minutes,
            average_daily_questions=ctx.average_daily_questions,
        )
