"""
StudyOS — ContextBuilder
Sprint-2.4: tek standart context şeması (v2).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    AI_CONTEXT_ACTIVE_GOALS,
    AI_CONTEXT_RECENT_ACTIVITIES,
    AI_CONTEXT_TODAY_PLANS,
    AI_CONTEXT_TODAY_SESSIONS,
    AI_CONTEXT_VERSION,
)
from app.models.user import User
from app.repositories.study_session_repository import StudySessionRepository
from app.services.activity_service import ActivityService
from app.services.ai.memory_retriever import MemoryRetriever
from app.services.ai_insights_service import AiInsightsService
from app.services.dashboard_service import DashboardService
from app.services.goal_service import GoalService, _eta_hint
from app.services.memory_service import MemoryService
from app.services.notification_settings_service import NotificationSettingsService
from app.services.question_record_service import QuestionRecordService
from app.services.statistics_service import StatisticsService
from app.services.study_plan_service import StudyPlanService
from app.services.study_resource_service import StudyResourceService
from app.services.study_session_service import StudySessionService
from app.services.achievement_service import AchievementService
from app.services.exam_service import ExamService
from app.services.learning_profile_service import LearningProfileService
from app.services.revision_service import RevisionService


class ContextBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build(
        self,
        user: User,
        *,
        conversation_summary: str | None = None,
    ) -> dict[str, Any]:
        # Aynı AsyncSession üzerinde paralel await güvenli değil — sıralı.
        today = datetime.now(UTC).date()
        dashboard = await DashboardService(self.db).get_dashboard(user)
        overview = await StatisticsService(self.db).get_overview(user.id)
        goals = await GoalService(self.db).list_active(user.id)
        progress = await GoalService(self.db).get_progress(user.id)
        insights = await AiInsightsService(self.db).get_overview(user.id)
        q_stats = await QuestionRecordService(self.db).get_statistics_overview(user.id)
        sessions_today = await StudySessionService(self.db).get_today(user.id)
        plans_today = await StudyPlanService(self.db).list_plans(user.id, study_date=today)
        activities = await ActivityService(self.db).get_recent_for_dashboard(user.id)
        notif = await NotificationSettingsService(self.db).get_settings(user.id)
        memory_enabled = await MemoryService(self.db).is_memory_enabled(user.id)
        active_session = await StudySessionRepository(self.db).get_active_for_user(user.id)
        memory_items = (
            await MemoryRetriever(self.db).to_context_items(user.id) if memory_enabled else []
        )
        resource_items = await StudyResourceService(self.db).context_items(user.id)
        resource_stats = await StudyResourceService(self.db).get_statistics(user.id)
        exams_ctx = await ExamService(self.db).context_payload(user.id)
        revisions_ctx = await RevisionService(self.db).context_payload(user.id)
        achievements_ctx = await AchievementService(self.db).context_payload(user.id)
        learning_profile_ctx = await LearningProfileService(self.db).context_payload(user.id)

        top_goal = None
        if goals:
            top_goal = min(goals, key=lambda g: (float(g.progress), g.end_date))

        goal_items = [
            {
                "title": g.title,
                "progress": float(g.progress),
                "remaining": max(0.0, float(g.target_value) - float(g.current_value)),
                "goal_type": str(g.goal_type),
            }
            for g in goals[:AI_CONTEXT_ACTIVE_GOALS]
        ]

        plan_items = [
            {
                "title": p.title,
                "subject": p.subject,
                "status": str(p.status),
            }
            for p in plans_today[:AI_CONTEXT_TODAY_PLANS]
        ]

        session_items = [
            {
                "id": str(s.id),
                "status": str(s.status),
                "planned_duration_minutes": s.planned_duration_minutes,
                "actual_duration_minutes": s.actual_duration_minutes,
            }
            for s in sessions_today[:AI_CONTEXT_TODAY_SESSIONS]
        ]

        current = None
        if active_session is not None:
            current = {
                "id": str(active_session.id),
                "status": str(active_session.status),
                "planned_duration_minutes": active_session.planned_duration_minutes,
                "actual_duration_minutes": active_session.actual_duration_minutes,
            }

        return {
            "context_version": AI_CONTEXT_VERSION,
            "conversation_summary": conversation_summary,
            "dashboard": {
                "today_study_minutes": dashboard.today_study_minutes,
                "today_questions_solved": dashboard.today_questions_solved,
                "daily_progress_percentage": dashboard.daily_progress_percentage,
                "streak_days": dashboard.streak_days,
            },
            "statistics": {
                "streak_days": overview.streak_days,
                "week_study_minutes": overview.week_study_minutes,
                "total_pomodoros": overview.total_pomodoros,
                "most_studied_subject": overview.most_studied_subject,
            },
            "goals": {
                "active_count": progress.active_count,
                "average_progress": progress.average_progress,
                "top_title": top_goal.title if top_goal else None,
                "top_progress": float(top_goal.progress) if top_goal else 0.0,
                "top_remaining": (
                    max(0.0, float(top_goal.target_value) - float(top_goal.current_value))
                    if top_goal
                    else 0.0
                ),
                "eta_hint": _eta_hint(top_goal) if top_goal else None,
                "items": goal_items,
            },
            "insights": {
                "has_enough_data": insights.has_enough_data,
                "top_recommendation": (
                    insights.top_recommendation.message if insights.top_recommendation else None
                ),
                "correct_rate": insights.correct_rate,
            },
            "questions": {
                "total_questions": q_stats.total_questions,
                "correct_rate": q_stats.correct_rate,
                "today_questions": q_stats.today_questions,
            },
            "plans": {
                "today_count": len(plans_today),
                "items": plan_items,
            },
            "sessions": {
                "today_count": len(sessions_today),
                "today": session_items,
                "current": current,
            },
            "activity": {
                "recent": [
                    {"title": a.title, "event_type": a.event_type}
                    for a in activities[:AI_CONTEXT_RECENT_ACTIVITIES]
                ],
            },
            "notification_preferences": {
                "daily_goal_enabled": notif.daily_goal_enabled,
                "daily_reminder_enabled": notif.daily_reminder_enabled,
                "pomodoro_enabled": notif.pomodoro_enabled,
                "streak_reminder_enabled": notif.streak_reminder_enabled,
            },
            "widget": {
                "auto_update_enabled": notif.widget_auto_update_enabled,
            },
            "memory": {
                "enabled": memory_enabled,
                "count": len(memory_items),
                "items": memory_items,
            },
            "resources": {
                "count": resource_stats.total_count,
                "completed_count": resource_stats.completed_count,
                "today_opened_count": resource_stats.today_opened_count,
                "today_completed_count": resource_stats.today_completed_count,
                "items": resource_items,
            },
            "exams": exams_ctx,
            "revisions": revisions_ctx,
            "achievements": achievements_ctx,
            "learning_profile": learning_profile_ctx,
        }
