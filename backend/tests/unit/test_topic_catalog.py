"""Sprint-3.2.A — Topic Catalog foundation tests."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_profile import BaselineLevel
from app.models.question_record import ExamType
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.learning_profile import OnboardingCompleteRequest, OnboardingExamTargetInput
from app.services.ai.topic_catalog_seed import TOPIC_CATALOG_SEED
from app.services.learning_profile_service import LearningProfileService


async def _user(db: AsyncSession) -> User:
    user = User(
        email=f"topic.{uuid.uuid4().hex[:8]}@studyos.dev",
        hashed_password="x",
        first_name="Topic",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    return await UserRepository(db).add(user)


def test_topic_seed_codes_are_subject_scoped():
    assert TOPIC_CATALOG_SEED
    for item in TOPIC_CATALOG_SEED:
        code = item["code"]
        subject = item["subject_code"]
        assert code.startswith(f"{subject}__")
        assert item["name"]


@pytest.mark.asyncio
async def test_topic_catalog_sync_and_list(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                    branch="sayisal",
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=2,
            daily_study_minutes=100,
            baseline_level=BaselineLevel.BEGINNER,
        ),
    )
    topics = await svc.list_topics_for_subject("tyt_matematik")
    codes = {t.code for t in topics}
    names = {t.name for t in topics}
    assert "tyt_matematik__temel_kavramlar" in codes
    assert "Temel Kavramlar" in names
    assert all(t.subject_code == "tyt_matematik" for t in topics)


@pytest.mark.asyncio
async def test_subject_hub_includes_topics(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                    branch="sayisal",
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=2,
            daily_study_minutes=100,
            baseline_level=BaselineLevel.BEGINNER,
        ),
    )
    hub = await svc.get_subject_hub(user.id, "tyt_matematik")
    assert hub.topics.count >= 5
    assert hub.topics.items[0].code.startswith("tyt_matematik__")
