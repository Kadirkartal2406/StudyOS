"""Sprint-3.1.C — Subject Hub API tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_record import ExamType
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.learning_profile import OnboardingCompleteRequest, OnboardingExamTargetInput
from app.models.learning_profile import BaselineLevel
from app.services.learning_profile_service import LearningProfileService


async def _user(db: AsyncSession) -> User:
    user = User(
        email=f"hub.{uuid.uuid4().hex[:8]}@studyos.dev",
        hashed_password="x",
        first_name="Hub",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    return await UserRepository(db).add(user)


@pytest.mark.asyncio
async def test_subject_hub_detail_by_code(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.YKS,
                    is_primary=True,
                    target_net=90,
                    target_university="ODTÜ",
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=2.5,
            daily_study_minutes=120,
            baseline_level=BaselineLevel.BEGINNER,
        ),
    )
    subjects = await svc.list_my_subjects(user.id)
    assert subjects
    code = subjects[0].subject_code

    hub = await svc.get_subject_hub(user.id, code)
    assert hub.subject.subject_code == code
    assert hub.progress is not None
    assert hub.today is not None
    assert hub.revision is not None
    assert hub.plans is not None
    assert hub.exam_summary.placeholder is True or hub.exam_summary.available is True
    assert hub.resources.placeholder is True
    assert hub.flashcards.placeholder is True
    assert hub.ai.explain_available is False
    assert "Explain" in hub.ai.explain_placeholder


@pytest.mark.asyncio
async def test_subject_hub_unknown_code(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    await svc.ensure_student(user.id)
    from app.core.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await svc.get_subject_hub(user.id, "no_such_code")


@pytest.mark.asyncio
async def test_subject_hub_api(client: AsyncClient):
    email = f"hub.api.{uuid.uuid4().hex[:8]}@studyos.dev"
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "GucluSifre123!",
            "first_name": "Hub",
            "last_name": "Api",
            "role": "student",
        },
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    complete = await client.post(
        "/api/v1/learning-profile/onboarding/complete",
        headers=headers,
        json={
            "exam_targets": [
                {
                    "exam_type": "yks",
                    "is_primary": True,
                    "target_net": 90,
                }
            ],
            "available_days": [0, 2, 4],
            "available_hours": 2.5,
            "daily_study_minutes": 120,
            "baseline_level": "intermediate",
        },
    )
    assert complete.status_code == 200, complete.text

    listed = await client.get(
        "/api/v1/learning-profile/subjects/me", headers=headers
    )
    assert listed.status_code == 200
    items = listed.json()["data"]
    assert items
    code = items[0]["subject_code"]

    detail = await client.get(
        f"/api/v1/learning-profile/subjects/{code}", headers=headers
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()["data"]
    assert body["subject"]["subject_code"] == code
    assert "progress" in body
    assert "today" in body
    assert "revision" in body
    assert "plans" in body
    assert "exam_summary" in body
    assert "resources" in body
    assert "flashcards" in body
    assert "ai" in body
    assert body["ai"]["explain_available"] is False
    assert body["flashcards"]["placeholder"] is True
