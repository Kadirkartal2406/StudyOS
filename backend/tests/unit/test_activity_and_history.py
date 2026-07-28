"""
StudyOS — Activity + Session History (Sprint-1.7) unit testleri
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityEventType
from app.models.study_session import StudySessionStatus
from app.models.user import User, UserRole, UserStatus
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_repository import UserRepository
from app.schemas.study_plan import StudyPlanCompleteRequest, StudyPlanCreate
from app.schemas.study_session import StudySessionFinishRequest, StudySessionStartRequest
from app.services.dashboard_service import DashboardService
from app.services.study_plan_service import StudyPlanService
from app.services.study_session_service import StudySessionService


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"act.{uuid.uuid4()}@studyos.dev",
        hashed_password="x",
        first_name="Ali",
        last_name="Veli",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    return await UserRepository(db).add(user)


@pytest.mark.asyncio
async def test_session_lifecycle_writes_activities(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, StudySessionStartRequest(planned_duration_minutes=25))
    await service.pause(user.id)
    await service.resume(user.id)
    await service.finish(user.id, StudySessionFinishRequest())

    rows = await ActivityRepository(db_session).list_recent_for_user(user.id, limit=20)
    types = [r.event_type for r in rows]
    assert ActivityEventType.SESSION_STARTED in types
    assert ActivityEventType.SESSION_PAUSED in types
    assert ActivityEventType.SESSION_RESUMED in types
    assert ActivityEventType.SESSION_COMPLETED in types


@pytest.mark.asyncio
async def test_plan_complete_writes_activity(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    plan_svc = StudyPlanService(db_session)
    from datetime import date

    plan = await plan_svc.create_plan(
        user.id,
        StudyPlanCreate(
            title="Matematik Planı",
            subject="Matematik",
            topic="Türev",
            target_question_count=10,
            estimated_minutes=40,
            study_date=date.today(),
        ),
    )
    await plan_svc.start_plan(plan.id, user.id)
    await plan_svc.complete_plan(plan.id, user.id, StudyPlanCompleteRequest())

    rows = await ActivityRepository(db_session).list_recent_for_user(user.id, limit=5)
    assert any(r.event_type == ActivityEventType.PLAN_COMPLETED for r in rows)

    dash = await DashboardService(db_session).get_dashboard(user)
    assert any(a.event_type == "plan_completed" for a in dash.recent_activities)


@pytest.mark.asyncio
async def test_history_filters_status_plan_and_search(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    plan_svc = StudyPlanService(db_session)
    session_svc = StudySessionService(db_session)
    from datetime import date

    plan = await plan_svc.create_plan(
        user.id,
        StudyPlanCreate(
            title="Fizik Tekrar",
            subject="Fizik",
            target_question_count=10,
            estimated_minutes=30,
            study_date=date.today(),
        ),
    )

    await session_svc.start(
        user.id,
        StudySessionStartRequest(
            planned_duration_minutes=25, study_plan_id=plan.id
        ),
    )
    await session_svc.finish(user.id, StudySessionFinishRequest())

    await session_svc.start(user.id, StudySessionStartRequest(planned_duration_minutes=25))
    # leave running

    completed, meta = await session_svc.get_history(
        user.id, status=StudySessionStatus.COMPLETED, page=1, page_size=10
    )
    assert meta.total_items == 1
    assert completed[0].status == StudySessionStatus.COMPLETED

    by_plan, _ = await session_svc.get_history(
        user.id, study_plan_id=plan.id, page=1, page_size=10
    )
    assert len(by_plan) == 1

    by_search, _ = await session_svc.get_history(user.id, q="Fizik", page=1, page_size=10)
    assert len(by_search) == 1

    empty, empty_meta = await session_svc.get_history(
        user.id, q="YokBoyleBirPlan", page=1, page_size=10
    )
    assert empty == []
    assert empty_meta.total_items == 0


@pytest.mark.asyncio
async def test_get_session_detail(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)
    started = await service.start(user.id, StudySessionStartRequest(planned_duration_minutes=25))
    detail = await service.get_by_id(started.id, user.id)
    assert detail.id == started.id
    read = await service.to_read(detail)
    assert read.plan_title is None
