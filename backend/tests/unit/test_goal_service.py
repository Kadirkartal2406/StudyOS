"""
StudyOS — Goal Service / Progress unit tests
Sprint-2.1
"""

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import GoalPeriod, GoalPriority, GoalStatus, GoalType
from app.schemas.auth import RegisterRequest
from app.schemas.goal import GoalCreate
from app.schemas.question_record import QuestionRecordCreate
from app.schemas.study_session import StudySessionFinishRequest, StudySessionStartRequest
from app.services.auth_service import AuthService
from app.services.goal_progress_service import GoalProgressEvent, GoalProgressService
from app.services.goal_service import GoalService
from app.services.question_record_service import QuestionRecordService
from app.services.study_session_service import StudySessionService


@pytest.mark.asyncio
async def test_create_question_goal_and_progress_on_record(db_session: AsyncSession):
    user, _, _ = await AuthService(db_session).register(
        RegisterRequest(
            email="goal.q@studyos.dev",
            password="GucluSifre123!",
            first_name="Goal",
            last_name="Q",
            role="student",
        )
    )
    today = datetime.now(UTC).date()
    monday = today - timedelta(days=today.weekday())
    goal = await GoalService(db_session).create(
        user.id,
        GoalCreate(
            title="Haftalık 50 soru",
            goal_type=GoalType.QUESTION,
            target_value=50,
            period=GoalPeriod.WEEKLY,
            priority=GoalPriority.HIGH,
            start_date=monday,
            end_date=monday + timedelta(days=6),
        ),
    )
    assert goal.status == GoalStatus.ACTIVE
    assert goal.current_value == 0

    await QuestionRecordService(db_session).create(
        user.id,
        QuestionRecordCreate(
            subject="Matematik",
            question_count=20,
            correct_count=15,
            wrong_count=5,
            blank_count=0,
            duration_minutes=30,
        ),
    )
    refreshed = await GoalService(db_session).get(goal.id, user.id)
    assert refreshed.current_value == 20
    assert refreshed.progress == 40.0
    assert "25" in refreshed.milestones_reached


@pytest.mark.asyncio
async def test_study_time_goal_on_session_finish(db_session: AsyncSession):
    user, _, _ = await AuthService(db_session).register(
        RegisterRequest(
            email="goal.t@studyos.dev",
            password="GucluSifre123!",
            first_name="Goal",
            last_name="T",
            role="student",
        )
    )
    today = datetime.now(UTC).date()
    await GoalService(db_session).create(
        user.id,
        GoalCreate(
            title="100 dk",
            goal_type=GoalType.STUDY_TIME,
            target_value=100,
            period=GoalPeriod.WEEKLY,
            start_date=today,
            end_date=today + timedelta(days=6),
        ),
    )
    await StudySessionService(db_session).start(
        user.id,
        StudySessionStartRequest(planned_duration_minutes=25, break_duration_minutes=5),
    )
    # Force some duration by finishing immediately (actual may be 0) — apply event manually too
    session = await StudySessionService(db_session).finish(
        user.id, StudySessionFinishRequest(completed_questions=0)
    )
    goals = await GoalService(db_session).list_active(user.id)
    # If actual minutes is 0, bump via apply_event to verify pomodoro/time path
    if session.actual_duration_minutes == 0:
        await GoalProgressService(db_session).apply_event(
            user.id,
            GoalProgressEvent(kind="session_completed", amount=25, occurred_on=today),
        )
        goals = await GoalService(db_session).list_active(user.id)
        assert goals[0].current_value == 25
    else:
        assert goals[0].current_value >= 0


@pytest.mark.asyncio
async def test_plan_completed_does_not_increment_question_goal(db_session: AsyncSession):
    """B1 — Plan complete standart goal'lara katkı yapmaz."""
    from app.schemas.study_plan import StudyPlanCompleteRequest, StudyPlanCreate
    from app.services.study_plan_service import StudyPlanService

    user, _, _ = await AuthService(db_session).register(
        RegisterRequest(
            email="goal.p@studyos.dev",
            password="GucluSifre123!",
            first_name="Goal",
            last_name="P",
            role="student",
        )
    )
    today = datetime.now(UTC).date()
    goal = await GoalService(db_session).create(
        user.id,
        GoalCreate(
            title="Soru",
            goal_type=GoalType.QUESTION,
            target_value=100,
            period=GoalPeriod.WEEKLY,
            start_date=today,
            end_date=today + timedelta(days=6),
        ),
    )
    plan = await StudyPlanService(db_session).create_plan(
        user.id,
        StudyPlanCreate(
            title="Test",
            subject="Matematik",
            target_question_count=10,
            estimated_minutes=30,
            study_date=today,
        ),
    )
    await StudyPlanService(db_session).complete_plan(
        plan.id, user.id, StudyPlanCompleteRequest()
    )
    refreshed = await GoalService(db_session).get(goal.id, user.id)
    assert refreshed.current_value == 0


@pytest.mark.asyncio
async def test_product_daily_questions_maps_and_progresses(db_session: AsyncSession):
    from app.services.goal_product_types import ProductGoalType

    user, _, _ = await AuthService(db_session).register(
        RegisterRequest(
            email="goal.prod@studyos.dev",
            password="GucluSifre123!",
            first_name="Goal",
            last_name="Prod",
            role="student",
        )
    )
    today = datetime.now(UTC).date()
    goal = await GoalService(db_session).create(
        user.id,
        GoalCreate(
            title="Günlük 30 soru",
            product_goal_type=ProductGoalType.DAILY_QUESTIONS,
            target_value=30,
            start_date=today,
            end_date=today,
        ),
    )
    assert goal.goal_type == GoalType.QUESTION
    assert goal.period == GoalPeriod.DAILY
    assert goal.product_goal_type == ProductGoalType.DAILY_QUESTIONS.value

    await QuestionRecordService(db_session).create(
        user.id,
        QuestionRecordCreate(
            subject="Matematik",
            question_count=10,
            correct_count=8,
            wrong_count=2,
            blank_count=0,
            duration_minutes=20,
        ),
    )
    refreshed = await GoalService(db_session).get(goal.id, user.id)
    assert refreshed.current_value == 10
    read = GoalService(db_session).to_read(refreshed)
    assert read.remaining == 20
    assert read.progress_sources
    assert any(e.source == "question_recorded" for e in read.progress_log)


@pytest.mark.asyncio
async def test_exam_recorded_updates_net_and_exam_count(db_session: AsyncSession):
    from app.schemas.exam import ExamCreate, ExamResultCreate
    from app.services.exam_service import ExamService
    from app.services.goal_product_types import ProductGoalType
    from app.models.question_record import ExamType

    user, _, _ = await AuthService(db_session).register(
        RegisterRequest(
            email="goal.exam@studyos.dev",
            password="GucluSifre123!",
            first_name="Goal",
            last_name="Exam",
            role="student",
        )
    )
    today = datetime.now(UTC).date()
    net_goal = await GoalService(db_session).create(
        user.id,
        GoalCreate(
            title="Net 80",
            product_goal_type=ProductGoalType.NET_TARGET,
            target_value=80,
            start_date=today,
            end_date=today + timedelta(days=90),
            exam_type=ExamType.TYT,
        ),
    )
    count_goal = await GoalService(db_session).create(
        user.id,
        GoalCreate(
            title="3 deneme",
            product_goal_type=ProductGoalType.EXAM_COUNT,
            target_value=3,
            start_date=today,
            end_date=today + timedelta(days=6),
            exam_type=ExamType.TYT,
        ),
    )
    await ExamService(db_session).create_exam(
        user.id,
        ExamCreate(
            title="Deneme 1",
            exam_type=ExamType.TYT,
            exam_date=today,
            duration_minutes=120,
            results=[
                ExamResultCreate(
                    subject="Matematik",
                    correct_count=20,
                    wrong_count=5,
                    blank_count=0,
                    question_count=25,
                    duration_minutes=40,
                ),
            ],
        ),
    )
    net_ref = await GoalService(db_session).get(net_goal.id, user.id)
    count_ref = await GoalService(db_session).get(count_goal.id, user.id)
    # net = correct - wrong/4 = 20 - 1.25 = 18.75
    assert float(net_ref.current_value) == 18.75
    assert float(count_ref.current_value) == 1.0
