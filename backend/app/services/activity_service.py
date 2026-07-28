"""
StudyOS — Activity Service
Olay kaydı ve Dashboard recent-activities okuma.
Sprint-1.7 (Meeting-015)
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DASHBOARD_RECENT_ACTIVITIES_LIMIT
from app.models.activity import Activity, ActivityEventType
from app.models.study_plan import StudyPlan
from app.models.study_session import StudySession
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import ActivityRead


class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ActivityRepository(db)

    async def record(
        self,
        *,
        user_id: uuid.UUID,
        event_type: ActivityEventType | str,
        title: str,
        description: str | None = None,
        study_session_id: uuid.UUID | None = None,
        study_plan_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> Activity:
        return await self.repo.create_activity(
            user_id=user_id,
            event_type=str(event_type),
            title=title,
            description=description,
            study_session_id=study_session_id,
            study_plan_id=study_plan_id,
            metadata=metadata,
            occurred_at=occurred_at or datetime.now(UTC),
        )

    async def record_session_started(
        self, session: StudySession, plan: StudyPlan | None = None
    ) -> Activity:
        plan_label = plan.title if plan is not None else "Serbest çalışma"
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.SESSION_STARTED,
            title=f"Çalışma başladı: {plan_label}",
            description=f"{session.planned_duration_minutes} dk odak planlandı",
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
            metadata={
                "planned_duration_minutes": session.planned_duration_minutes,
                "plan_title": plan.title if plan else None,
                "subject": plan.subject if plan else None,
            },
            occurred_at=session.started_at,
        )

    async def record_session_paused(self, session: StudySession) -> Activity:
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.SESSION_PAUSED,
            title="Çalışma duraklatıldı",
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
            occurred_at=session.paused_at or datetime.now(UTC),
        )

    async def record_session_resumed(self, session: StudySession) -> Activity:
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.SESSION_RESUMED,
            title="Çalışma devam ediyor",
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
        )

    async def record_session_completed(
        self, session: StudySession, plan: StudyPlan | None = None
    ) -> Activity:
        plan_label = plan.title if plan is not None else "Serbest çalışma"
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.SESSION_COMPLETED,
            title=f"{session.actual_duration_minutes} dk Pomodoro tamamlandı",
            description=plan_label,
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
            metadata={
                "actual_duration_minutes": session.actual_duration_minutes,
                "completed_questions": session.completed_questions,
                "plan_title": plan.title if plan else None,
                "subject": plan.subject if plan else None,
            },
            occurred_at=session.ended_at or datetime.now(UTC),
        )

    async def record_break_started(self, session: StudySession) -> Activity:
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.BREAK_STARTED,
            title="Mola başladı",
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
            metadata={"subject_code": session.subject_code, "topic_code": session.topic_code},
        )

    async def record_break_ended(self, session: StudySession) -> Activity:
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.BREAK_ENDED,
            title="Derse dönüldü",
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
            metadata={
                "actual_break_minutes": int(getattr(session, "actual_break_minutes", 0) or 0),
            },
        )

    async def record_study_finished(self, session: StudySession) -> Activity:
        """Journey: Study Finished — session_completed ile birlikte kullanılabilir."""
        return await self.record(
            user_id=session.user_id,
            event_type=ActivityEventType.STUDY_FINISHED,
            title="Çalışma bitti",
            description=f"{session.actual_duration_minutes} dk odak",
            study_session_id=session.id,
            study_plan_id=session.study_plan_id,
            occurred_at=session.ended_at or datetime.now(UTC),
        )

    async def record_plan_completed(self, plan: StudyPlan) -> Activity:
        return await self.record(
            user_id=plan.user_id,
            event_type=ActivityEventType.PLAN_COMPLETED,
            title=f"{plan.title} tamamlandı",
            description=plan.topic or plan.subject,
            study_plan_id=plan.id,
            metadata={
                "subject": plan.subject,
                "topic": plan.topic,
                "completed_minutes": plan.completed_minutes,
                "completed_question_count": plan.completed_question_count,
            },
        )

    async def get_recent_for_dashboard(self, user_id: uuid.UUID) -> list[ActivityRead]:
        rows = await self.repo.list_recent_for_user(
            user_id, limit=DASHBOARD_RECENT_ACTIVITIES_LIMIT
        )
        return [ActivityRead.model_validate(row) for row in rows]
