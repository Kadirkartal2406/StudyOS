"""
StudyOS — StudyPlanService Birim Testleri
CRUD, sahiplik, saat çakışması ve durum geçişi (start/complete/skip) mantığını doğrular.
"""

import uuid
from datetime import date, time, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.study_plan import StudyPlanStatus
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.study_plan import (
    StudyPlanCompleteRequest,
    StudyPlanCreate,
    StudyPlanUpdate,
)
from app.services.study_plan_service import StudyPlanService

TODAY = date.today()


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"plan.{uuid.uuid4()}@studyos.dev",
        hashed_password="irrelevant",
        first_name="Plan",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=False,
    )
    return await UserRepository(db).add(user)


def _create_payload(**overrides: object) -> StudyPlanCreate:
    defaults: dict[str, object] = {
        "title": "Matematik Çalışması",
        "subject": "Matematik",
        "topic": "Türev",
        "target_question_count": 20,
        "estimated_minutes": 60,
        "study_date": TODAY,
    }
    defaults.update(overrides)
    return StudyPlanCreate(**defaults)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_create_plan_persists_fields(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)

    plan = await service.create_plan(user.id, _create_payload())

    assert plan.id is not None
    assert plan.user_id == user.id
    assert plan.status == StudyPlanStatus.PLANNED
    assert plan.order_index == 0
    assert plan.completed_minutes == 0
    assert plan.completed_question_count == 0


@pytest.mark.asyncio
async def test_create_plan_auto_increments_order_index(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)

    first = await service.create_plan(user.id, _create_payload(title="Birinci"))
    second = await service.create_plan(user.id, _create_payload(title="İkinci"))

    assert first.order_index == 0
    assert second.order_index == 1


@pytest.mark.asyncio
async def test_create_plan_rejects_overlapping_time_range(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)

    payload_kwargs = {
        "planned_start_time": time(9, 0),
        "planned_end_time": time(10, 0),
    }
    await service.create_plan(user.id, _create_payload(**payload_kwargs))

    with pytest.raises(ValidationError):
        await service.create_plan(
            user.id,
            _create_payload(
                title="Çakışan Plan",
                planned_start_time=time(9, 30),
                planned_end_time=time(10, 30),
            ),
        )


@pytest.mark.asyncio
async def test_create_plan_allows_adjacent_non_overlapping_time_range(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)

    await service.create_plan(
        user.id,
        _create_payload(planned_start_time=time(9, 0), planned_end_time=time(10, 0)),
    )

    plan = await service.create_plan(
        user.id,
        _create_payload(
            title="Ardışık Plan",
            planned_start_time=time(10, 0),
            planned_end_time=time(11, 0),
        ),
    )

    assert plan is not None


def test_end_time_must_be_after_start_time() -> None:
    with pytest.raises(ValueError):
        _create_payload(planned_start_time=time(10, 0), planned_end_time=time(9, 0))


def test_both_times_required_together() -> None:
    with pytest.raises(ValueError):
        _create_payload(planned_start_time=time(10, 0))


@pytest.mark.asyncio
async def test_get_plan_raises_not_found_for_other_users_plan(db_session: AsyncSession) -> None:
    owner = await _make_user(db_session)
    other_user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(owner.id, _create_payload())

    with pytest.raises(NotFoundError):
        await service.get_plan(plan.id, other_user.id)


@pytest.mark.asyncio
async def test_update_plan_changes_fields(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())

    updated = await service.update_plan(
        plan.id,
        user.id,
        StudyPlanUpdate(
            title="Güncellenmiş Başlık",
            subject="Fizik",
            topic="Kuvvet",
            target_question_count=15,
            estimated_minutes=45,
            study_date=TODAY,
        ),
    )

    assert updated.title == "Güncellenmiş Başlık"
    assert updated.subject == "Fizik"
    assert updated.estimated_minutes == 45


@pytest.mark.asyncio
async def test_delete_plan_soft_deletes(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())

    await service.delete_plan(plan.id, user.id)

    assert plan.deleted_at is not None
    with pytest.raises(NotFoundError):
        await service.get_plan(plan.id, user.id)


@pytest.mark.asyncio
async def test_deleted_plan_excluded_from_list(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())
    await service.delete_plan(plan.id, user.id)

    plans = await service.list_plans(user.id, TODAY)

    assert plans == []


@pytest.mark.asyncio
async def test_start_plan_transitions_to_in_progress(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())

    started = await service.start_plan(plan.id, user.id)

    assert started.status == StudyPlanStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_complete_plan_defaults_to_target_values(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())

    completed = await service.complete_plan(plan.id, user.id, StudyPlanCompleteRequest())

    assert completed.status == StudyPlanStatus.COMPLETED
    assert completed.completed_question_count == plan.target_question_count
    assert completed.completed_minutes == plan.estimated_minutes


@pytest.mark.asyncio
async def test_complete_plan_accepts_partial_progress(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())

    completed = await service.complete_plan(
        plan.id,
        user.id,
        StudyPlanCompleteRequest(completed_question_count=5, completed_minutes=20),
    )

    assert completed.completed_question_count == 5
    assert completed.completed_minutes == 20


@pytest.mark.asyncio
async def test_skip_plan_transitions_to_skipped(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())

    skipped = await service.skip_plan(plan.id, user.id)

    assert skipped.status == StudyPlanStatus.SKIPPED


@pytest.mark.asyncio
async def test_cannot_transition_from_terminal_status(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    plan = await service.create_plan(user.id, _create_payload())
    await service.complete_plan(plan.id, user.id, StudyPlanCompleteRequest())

    with pytest.raises(ConflictError):
        await service.start_plan(plan.id, user.id)

    with pytest.raises(ConflictError):
        await service.skip_plan(plan.id, user.id)


@pytest.mark.asyncio
async def test_list_plans_ordered_by_order_index(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    await service.create_plan(user.id, _create_payload(title="A"))
    await service.create_plan(user.id, _create_payload(title="B"))
    await service.create_plan(user.id, _create_payload(title="C"))

    plans = await service.list_plans(user.id, TODAY)

    assert [p.title for p in plans] == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_list_plans_filters_by_date(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = StudyPlanService(db_session)
    await service.create_plan(user.id, _create_payload(study_date=TODAY))
    await service.create_plan(
        user.id, _create_payload(study_date=TODAY + timedelta(days=1), title="Yarın")
    )

    plans = await service.list_plans(user.id, TODAY)

    assert len(plans) == 1
