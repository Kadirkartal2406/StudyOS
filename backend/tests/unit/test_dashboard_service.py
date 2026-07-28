"""
StudyOS — Dashboard Service Unit Testleri
Sprint-1.5 itibarıyla süre/soru StudySession'dan, plan metrikleri StudyPlan'dan gelir.
"""

import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_DAILY_STUDY_GOAL_MINUTES
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.study_plan import StudyPlanCompleteRequest, StudyPlanCreate
from app.schemas.study_session import StudySessionFinishRequest, StudySessionStartRequest
from app.services.dashboard_service import DashboardService
from app.services.study_plan_service import StudyPlanService
from app.services.study_session_service import StudySessionService


async def _make_user(db: AsyncSession, **overrides: object) -> User:
    defaults: dict[str, object] = {
        "email": f"dashboard.{uuid.uuid4()}@studyos.dev",
        "hashed_password": "irrelevant",
        "first_name": "Kadir",
        "last_name": "Kartal",
        "role": UserRole.STUDENT,
        "status": UserStatus.ACTIVE,
        "is_verified": False,
    }
    defaults.update(overrides)
    user = User(**defaults)  # type: ignore[arg-type]
    return await UserRepository(db).add(user)


@pytest.mark.asyncio
async def test_get_dashboard_returns_user_first_name(db_session: AsyncSession) -> None:
    user = await _make_user(db_session, first_name="Ayşe")

    result = await DashboardService(db_session).get_dashboard(user)

    assert result.first_name == "Ayşe"


@pytest.mark.asyncio
async def test_get_dashboard_uses_default_goal_when_no_plan_today(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)

    result = await DashboardService(db_session).get_dashboard(user)

    assert result.daily_study_goal_minutes == DEFAULT_DAILY_STUDY_GOAL_MINUTES
    assert result.today_study_minutes == 0
    assert result.today_questions_solved == 0
    assert result.today_studied_topic is None
    assert result.daily_progress_percentage == 0.0
    assert result.today_plan_count == 0
    assert result.completed_plan_count == 0
    assert result.today_plans == []
    assert result.streak_days == 0
    assert result.total_pomodoros == 0
    assert result.recent_activities == []


@pytest.mark.asyncio
async def test_get_dashboard_returns_last_login_at(db_session: AsyncSession) -> None:
    last_login = datetime(2026, 7, 15, 10, 0, tzinfo=UTC)
    user = await _make_user(db_session, last_login_at=last_login)

    result = await DashboardService(db_session).get_dashboard(user)

    assert result.last_login_at == last_login


@pytest.mark.asyncio
async def test_get_dashboard_aggregates_plans_and_sessions(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    plan_service = StudyPlanService(db_session)
    session_service = StudySessionService(db_session)
    today = datetime.now(UTC).date()

    plan_a = await plan_service.create_plan(
        user.id,
        StudyPlanCreate(
            title="Matematik Tekrar",
            subject="Matematik",
            topic="Türev",
            target_question_count=20,
            estimated_minutes=60,
            study_date=today,
        ),
    )
    await plan_service.complete_plan(
        plan_a.id,
        user.id,
        StudyPlanCompleteRequest(completed_question_count=15, completed_minutes=45),
    )

    plan_b = await plan_service.create_plan(
        user.id,
        StudyPlanCreate(
            title="Fizik Soru Çözümü",
            subject="Fizik",
            target_question_count=10,
            estimated_minutes=40,
            study_date=today,
        ),
    )
    await plan_service.start_plan(plan_b.id, user.id)

    await session_service.start(
        user.id,
        StudySessionStartRequest(planned_duration_minutes=25, break_duration_minutes=5),
    )
    await session_service.finish(
        user.id,
        StudySessionFinishRequest(completed_questions=15, completed_topics=1),
    )

    result = await DashboardService(db_session).get_dashboard(user)

    assert result.today_plan_count == 2
    assert result.completed_plan_count == 1
    # B1 (Sprint-1.9): Dashboard soru sayısı QuestionRecord'dan; Session finish etkilemez.
    assert result.today_questions_solved == 0
    assert result.today_study_minutes >= 0
    assert result.daily_study_goal_minutes == 100
    assert result.today_studied_topic == "Fizik"
    assert len(result.today_plans) == 2
    assert result.total_pomodoros == 1
    assert result.streak_days >= 1


@pytest.mark.asyncio
async def test_get_dashboard_ignores_plans_from_other_dates(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    plan_service = StudyPlanService(db_session)
    yesterday = date.today() - timedelta(days=1)

    await plan_service.create_plan(
        user.id,
        StudyPlanCreate(
            title="Dünkü Plan",
            subject="Kimya",
            target_question_count=5,
            estimated_minutes=30,
            study_date=yesterday,
        ),
    )

    result = await DashboardService(db_session).get_dashboard(user)

    assert result.today_plan_count == 0


def test_calculate_progress_caps_at_100() -> None:
    percentage = DashboardService._calculate_progress(300, 120)

    assert percentage == 100.0


def test_calculate_progress_zero_goal_returns_zero() -> None:
    percentage = DashboardService._calculate_progress(50, 0)

    assert percentage == 0.0


def test_calculate_progress_rounds_to_one_decimal() -> None:
    percentage = DashboardService._calculate_progress(40, 120)

    assert percentage == 33.3
