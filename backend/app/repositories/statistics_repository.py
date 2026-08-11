"""
StudyOS — Statistics Repository
StudySession + StudyPlan üzerinde aggregate sorgular (N+1 yok).
Sprint-1.6: QuestionStatistics tablosu kullanılmaz — bkz. Meeting-014.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import STATISTICS_FREE_LABEL
from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.models.study_session import StudySession, StudySessionStatus


class StatisticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _subject_scope_filter(subject_codes: set[str]):
        """Active-exam codes OR unbound (null) sessions — 'Serbest' pomodoro counts."""
        codes = {c.lower() for c in subject_codes}
        return or_(
            StudySession.subject_code.is_(None),
            func.lower(StudySession.subject_code).in_(codes),
        )

    def _completed_filters(
        self,
        user_id: uuid.UUID,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        subject_codes: set[str] | None = None,
    ) -> list:
        filters = [
            StudySession.user_id == user_id,
            StudySession.status == StudySessionStatus.COMPLETED,
        ]
        if started_from is not None:
            filters.append(StudySession.started_at >= started_from)
        if started_to is not None:
            filters.append(StudySession.started_at < started_to)
        if subject_codes:
            filters.append(self._subject_scope_filter(subject_codes))
        return filters

    async def aggregate_sessions(
        self,
        user_id: uuid.UUID,
        *,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        subject_codes: set[str] | None = None,
    ) -> tuple[int, int, int, int, float, int]:
        """
        Returns:
            (total_minutes, session_count, question_count, topic_count,
             avg_minutes, max_minutes)
        """
        filters = self._completed_filters(
            user_id, started_from, started_to, subject_codes=subject_codes
        )
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
                func.count(StudySession.id),
                func.coalesce(func.sum(StudySession.completed_questions), 0),
                func.coalesce(func.sum(StudySession.completed_topics), 0),
                func.coalesce(func.avg(StudySession.actual_duration_minutes), 0.0),
                func.coalesce(func.max(StudySession.actual_duration_minutes), 0),
            ).where(*filters)
        )
        row = result.one()
        return (
            int(row[0]),
            int(row[1]),
            int(row[2]),
            int(row[3]),
            float(row[4]),
            int(row[5]),
        )

    async def count_completed_plans(
        self,
        user_id: uuid.UUID,
        *,
        study_date_from: date | None = None,
        study_date_to: date | None = None,
        subject_names: set[str] | None = None,
    ) -> int:
        filters = [
            StudyPlan.user_id == user_id,
            StudyPlan.deleted_at.is_(None),
            StudyPlan.status == StudyPlanStatus.COMPLETED,
        ]
        if study_date_from is not None:
            filters.append(StudyPlan.study_date >= study_date_from)
        if study_date_to is not None:
            filters.append(StudyPlan.study_date <= study_date_to)
        if subject_names:
            names = {n.lower() for n in subject_names}
            filters.append(func.lower(StudyPlan.subject).in_(names))
        result = await self.db.execute(select(func.count()).select_from(StudyPlan).where(*filters))
        return int(result.scalar_one())

    async def daily_minutes_series(
        self,
        user_id: uuid.UUID,
        started_from: datetime,
        started_to: datetime,
        *,
        subject_codes: set[str] | None = None,
    ) -> list[tuple[date, int, int, int]]:
        """(day, minutes, sessions, questions) — gün bazlı aggregate."""
        day_col = func.date(StudySession.started_at).label("day")
        filters = self._completed_filters(
            user_id, started_from, started_to, subject_codes=subject_codes
        )
        result = await self.db.execute(
            select(
                day_col,
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
                func.count(StudySession.id),
                func.coalesce(func.sum(StudySession.completed_questions), 0),
            )
            .where(*filters)
            .group_by(day_col)
            .order_by(day_col)
        )
        return [(row[0], int(row[1]), int(row[2]), int(row[3])) for row in result.all()]

    async def hourly_minutes_series(
        self,
        user_id: uuid.UUID,
        started_from: datetime,
        started_to: datetime,
        *,
        subject_codes: set[str] | None = None,
    ) -> list[tuple[int, int, int, int]]:
        """(hour 0-23, minutes, sessions, questions) — UTC saat."""
        hour_col = func.extract("hour", StudySession.started_at).label("hour")
        filters = self._completed_filters(
            user_id, started_from, started_to, subject_codes=subject_codes
        )
        result = await self.db.execute(
            select(
                hour_col,
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
                func.count(StudySession.id),
                func.coalesce(func.sum(StudySession.completed_questions), 0),
            )
            .where(*filters)
            .group_by(hour_col)
            .order_by(hour_col)
        )
        return [(int(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in result.all()]

    async def weekday_minutes(
        self,
        user_id: uuid.UUID,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        *,
        subject_codes: set[str] | None = None,
    ) -> list[tuple[int, int]]:
        """PostgreSQL DOW: 0=Pazar … 6=Cumartesi → (dow, minutes)."""
        dow_col = func.extract("dow", StudySession.started_at).label("dow")
        filters = self._completed_filters(
            user_id, started_from, started_to, subject_codes=subject_codes
        )
        result = await self.db.execute(
            select(
                dow_col,
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
            )
            .where(*filters)
            .group_by(dow_col)
        )
        return [(int(row[0]), int(row[1])) for row in result.all()]

    async def subject_distribution(
        self,
        user_id: uuid.UUID,
        *,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 20,
        subject_codes: set[str] | None = None,
    ) -> list[tuple[str, int, int, int]]:
        """(subject_name, minutes, sessions, questions)."""
        subject_label = func.coalesce(StudyPlan.subject, STATISTICS_FREE_LABEL).label(
            "subject_name"
        )
        filters = self._completed_filters(
            user_id, started_from, started_to, subject_codes=subject_codes
        )
        result = await self.db.execute(
            select(
                subject_label,
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
                func.count(StudySession.id),
                func.coalesce(func.sum(StudySession.completed_questions), 0),
            )
            .select_from(StudySession)
            .outerjoin(StudyPlan, StudySession.study_plan_id == StudyPlan.id)
            .where(*filters)
            .group_by(subject_label)
            .order_by(func.sum(StudySession.actual_duration_minutes).desc())
            .limit(limit)
        )
        return [(str(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in result.all()]

    async def topic_distribution(
        self,
        user_id: uuid.UUID,
        *,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        limit: int = 20,
        subject_codes: set[str] | None = None,
    ) -> list[tuple[str, int, int, int]]:
        topic_expr = func.coalesce(StudyPlan.topic, StudyPlan.subject, STATISTICS_FREE_LABEL)
        filters = self._completed_filters(
            user_id, started_from, started_to, subject_codes=subject_codes
        )
        result = await self.db.execute(
            select(
                topic_expr.label("topic_name"),
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
                func.count(StudySession.id),
                func.coalesce(func.sum(StudySession.completed_questions), 0),
            )
            .select_from(StudySession)
            .outerjoin(StudyPlan, StudySession.study_plan_id == StudyPlan.id)
            .where(*filters)
            .group_by(topic_expr)
            .order_by(func.sum(StudySession.actual_duration_minutes).desc())
            .limit(limit)
        )
        return [(str(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in result.all()]

    async def study_dates_desc(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 400,
        subject_codes: set[str] | None = None,
    ) -> list[date]:
        """Streak hesabı için distinct çalışma günleri (yeniden eskiye)."""
        day_col = func.date(StudySession.started_at)
        filters = [
            StudySession.user_id == user_id,
            StudySession.status == StudySessionStatus.COMPLETED,
        ]
        if subject_codes:
            filters.append(self._subject_scope_filter(subject_codes))
        result = await self.db.execute(
            select(day_col)
            .where(*filters)
            .group_by(day_col)
            .order_by(day_col.desc())
            .limit(limit)
        )
        return [row[0] for row in result.all()]
