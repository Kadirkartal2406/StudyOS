"""
StudyOS — StatisticsService Birim Testleri
"""

import asyncio
import uuid
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.study_plan import StudyPlanCreate
from app.schemas.study_session import StudySessionFinishRequest, StudySessionStartRequest
from app.services.statistics_service import StatisticsService
from app.services.study_plan_service import StudyPlanService
from app.services.study_session_service import StudySessionService


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"stats.{uuid.uuid4()}@studyos.dev",
        hashed_password="irrelevant",
        first_name="Stats",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=False,
    )
    return await UserRepository(db).add(user)


async def _finish_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    minutes_plan: int = 25,
    questions: int = 5,
    study_plan_id: uuid.UUID | None = None,
) -> None:
    svc = StudySessionService(db)
    await svc.start(
        user_id,
        StudySessionStartRequest(
            planned_duration_minutes=minutes_plan,
            break_duration_minutes=5,
            study_plan_id=study_plan_id,
        ),
    )
    await asyncio.sleep(0.05)
    await svc.finish(
        user_id,
        StudySessionFinishRequest(completed_questions=questions, completed_topics=1),
    )


@pytest.mark.asyncio
async def test_overview_empty(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    overview = await StatisticsService(db_session).get_overview(user.id)
    assert overview.total_study_minutes == 0
    assert overview.streak_days == 0
    assert overview.total_pomodoros == 0


@pytest.mark.asyncio
async def test_overview_after_session(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    await _finish_session(db_session, user.id, questions=7)

    overview = await StatisticsService(db_session).get_overview(user.id)
    assert overview.total_pomodoros == 1
    assert overview.today_questions == 7
    assert overview.total_questions == 7
    assert overview.streak_days >= 1
    assert overview.most_studied_subject == "Serbest"


@pytest.mark.asyncio
async def test_unbound_pomodoro_counts_with_active_exam(
    db_session: AsyncSession,
) -> None:
    """Serbest (subject_code=NULL) oturumlar aktif sınav scope'unda da Hedeflerim'e yazılır."""
    from app.models.question_record import ExamType
    from app.models.study_session import StudySession, StudySessionStatus
    from app.schemas.learning_profile import (
        BaselineLevel,
        OnboardingCompleteRequest,
        OnboardingExamTargetInput,
    )
    from app.services.dashboard_service import DashboardService
    from app.services.learning_profile_service import LearningProfileService

    user = await _make_user(db_session)
    await LearningProfileService(db_session).complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                    target_net=90,
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=3,
            daily_study_minutes=120,
            baseline_level=BaselineLevel.BEGINNER,
            baseline_reason="test",
        ),
    )

    # Direkt completed session — süre hesabına bağlı kalmadan
    from datetime import UTC, datetime

    session = StudySession(
        user_id=user.id,
        planned_duration_minutes=25,
        actual_duration_minutes=25,
        break_duration_minutes=5,
        completed_questions=0,
        completed_topics=0,
        status=StudySessionStatus.COMPLETED,
        subject_code=None,
        topic_code=None,
        started_at=datetime.now(UTC),
        ended_at=datetime.now(UTC),
    )
    db_session.add(session)
    await db_session.flush()

    overview = await StatisticsService(db_session).get_overview(user.id)
    assert overview.today_study_minutes == 25
    assert overview.total_pomodoros == 1

    dash = await DashboardService(db_session).get_dashboard(user)
    assert dash.today_study_minutes == 25
    assert dash.daily_progress_percentage > 0


def test_subject_scope_filter_includes_null_subject() -> None:
    from sqlalchemy.dialects import postgresql

    from app.repositories.statistics_repository import StatisticsRepository

    clause = StatisticsRepository._subject_scope_filter({"matematik"})
    sql = str(
        clause.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    ).lower()
    assert "is null" in sql
    assert "matematik" in sql


@pytest.mark.asyncio
async def test_subject_distribution_uses_plan(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    plan = await StudyPlanService(db_session).create_plan(
        user.id,
        StudyPlanCreate(
            title="Mat",
            subject="Matematik",
            topic="Türev",
            target_question_count=10,
            estimated_minutes=30,
            study_date=date.today(),
        ),
    )
    await _finish_session(db_session, user.id, questions=4, study_plan_id=plan.id)

    subjects = await StatisticsService(db_session).get_subjects(user.id)
    assert subjects.items[0].name == "Matematik"
    assert subjects.items[0].question_count == 4

    topics = await StatisticsService(db_session).get_topics(user.id)
    assert topics.items[0].name == "Türev"


@pytest.mark.asyncio
async def test_daily_weekly_monthly_heatmap_streak(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    await _finish_session(db_session, user.id, questions=3)

    svc = StatisticsService(db_session)
    daily = await svc.get_daily(user.id)
    assert daily.session_count == 1
    assert len(daily.buckets) == 24

    weekly = await svc.get_weekly(user.id)
    assert weekly.session_count == 1
    assert len(weekly.buckets) == 7

    monthly = await svc.get_monthly(user.id)
    assert monthly.session_count == 1

    heatmap = await svc.get_heatmap(user.id)
    assert len(heatmap.days) == 30
    assert sum(d.session_count for d in heatmap.days) == 1

    streak = await svc.get_streak(user.id)
    assert streak.current_streak_days >= 1
    assert streak.longest_streak_days >= 1


@pytest.mark.asyncio
async def test_productivity_has_weekday_and_hour_arrays(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    await _finish_session(db_session, user.id)

    insight = await StatisticsService(db_session).get_productivity(user.id)
    assert len(insight.weekday_minutes) == 7
    assert len(insight.hour_minutes) == 24
    assert sum(insight.weekday_minutes) >= 0
