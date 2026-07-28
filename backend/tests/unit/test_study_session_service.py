"""
StudyOS — StudySessionService Birim Testleri
start/pause/resume/finish, tek aktif oturum ve StudyPlan entegrasyonunu doğrular.
"""

import asyncio
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.study_plan import StudyPlanStatus
from app.models.study_session import StudySessionStatus
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.study_plan import StudyPlanCreate
from app.schemas.study_session import StudySessionFinishRequest, StudySessionStartRequest
from app.services.study_plan_service import StudyPlanService
from app.services.study_session_service import StudySessionService


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"session.{uuid.uuid4()}@studyos.dev",
        hashed_password="irrelevant",
        first_name="Session",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=False,
    )
    return await UserRepository(db).add(user)


def _start_payload(**overrides: object) -> StudySessionStartRequest:
    defaults: dict[str, object] = {
        "planned_duration_minutes": 25,
        "break_duration_minutes": 5,
    }
    defaults.update(overrides)
    return StudySessionStartRequest(**defaults)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_start_creates_running_session(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    session = await service.start(user.id, _start_payload())

    assert session.id is not None
    assert session.user_id == user.id
    assert session.status == StudySessionStatus.RUNNING
    assert session.planned_duration_minutes == 25
    assert session.break_duration_minutes == 5
    assert session.actual_duration_minutes == 0
    assert session.ended_at is None


@pytest.mark.asyncio
async def test_start_rejects_second_active_session(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())

    with pytest.raises(ConflictError):
        await service.start(user.id, _start_payload(planned_duration_minutes=50))


@pytest.mark.asyncio
async def test_pause_and_resume_cycle(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())
    paused = await service.pause(user.id)
    assert paused.status == StudySessionStatus.PAUSED
    assert paused.paused_at is not None

    await asyncio.sleep(0.05)
    resumed = await service.resume(user.id)
    assert resumed.status == StudySessionStatus.RUNNING
    assert resumed.paused_at is None
    assert resumed.paused_seconds >= 0


@pytest.mark.asyncio
async def test_pause_rejects_when_already_paused(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())
    await service.pause(user.id)

    with pytest.raises(ConflictError):
        await service.pause(user.id)


@pytest.mark.asyncio
async def test_resume_rejects_when_running(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())

    with pytest.raises(ConflictError):
        await service.resume(user.id)


@pytest.mark.asyncio
async def test_finish_completes_session_and_clears_active(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())
    await asyncio.sleep(0.05)
    finished = await service.finish(
        user.id,
        StudySessionFinishRequest(completed_questions=10, completed_topics=1),
    )

    assert finished.status == StudySessionStatus.COMPLETED
    assert finished.ended_at is not None
    assert finished.completed_questions == 10
    assert finished.completed_topics == 1
    assert finished.actual_duration_minutes >= 0

    # Aktif oturum kalmamalı — yeni start mümkün.
    again = await service.start(user.id, _start_payload())
    assert again.status == StudySessionStatus.RUNNING


@pytest.mark.asyncio
async def test_finish_without_active_raises_not_found(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    with pytest.raises(NotFoundError):
        await service.finish(user.id, StudySessionFinishRequest())


@pytest.mark.asyncio
async def test_finish_updates_linked_study_plan_incrementally(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    plan_service = StudyPlanService(db_session)
    session_service = StudySessionService(db_session)

    plan = await plan_service.create_plan(
        user.id,
        StudyPlanCreate(
            title="Matematik",
            subject="Matematik",
            topic="Türev",
            target_question_count=20,
            estimated_minutes=60,
            study_date=date.today(),
        ),
    )
    assert plan.status == StudyPlanStatus.PLANNED

    await session_service.start(
        user.id,
        _start_payload(study_plan_id=plan.id, planned_duration_minutes=25),
    )
    await asyncio.sleep(0.05)
    await session_service.finish(
        user.id,
        StudySessionFinishRequest(completed_questions=8, completed_topics=1),
    )

    refreshed = await plan_service.get_plan(plan.id, user.id)
    assert refreshed.status == StudyPlanStatus.IN_PROGRESS
    assert refreshed.completed_question_count == 8
    assert refreshed.completed_minutes >= 0


@pytest.mark.asyncio
async def test_start_with_unknown_plan_raises_not_found(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    with pytest.raises(NotFoundError):
        await service.start(user.id, _start_payload(study_plan_id=uuid.uuid4()))


@pytest.mark.asyncio
async def test_get_today_and_statistics(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())
    await asyncio.sleep(0.05)
    await service.finish(user.id, StudySessionFinishRequest(completed_questions=5))

    today = await service.get_today(user.id)
    assert len(today) == 1
    assert today[0].status == StudySessionStatus.COMPLETED

    stats = await service.get_statistics(user.id)
    assert stats.total_sessions == 1
    assert stats.completed_sessions == 1
    assert stats.total_questions == 5


@pytest.mark.asyncio
async def test_get_history_pagination(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    for _ in range(3):
        await service.start(user.id, _start_payload())
        await service.finish(user.id, StudySessionFinishRequest())

    page1, meta = await service.get_history(user.id, page=1, page_size=2)
    assert len(page1) == 2
    assert meta.total_items == 3
    assert meta.total_pages == 2

    page2, _ = await service.get_history(user.id, page=2, page_size=2)
    assert len(page2) == 1


@pytest.mark.asyncio
async def test_statistics_date_filter_excludes_other_days(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    service = StudySessionService(db_session)

    await service.start(user.id, _start_payload())
    await service.finish(user.id, StudySessionFinishRequest(completed_questions=3))

    tomorrow = date.today() + timedelta(days=1)
    stats = await service.get_statistics(user.id, date_from=tomorrow, date_to=tomorrow)
    assert stats.completed_sessions == 0
    assert stats.total_questions == 0
