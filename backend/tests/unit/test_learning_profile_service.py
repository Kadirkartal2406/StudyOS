"""
StudyOS — Learning Profile / Onboarding tests (Sprint-3.0)
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_profile import JourneyStage
from app.models.question_record import ExamType
from app.models.user import User, UserRole, UserStatus
from app.schemas.learning_profile import (
    BaselineLevel,
    OnboardingCompleteRequest,
    OnboardingExamTargetInput,
)
from app.services.ai.journey_stage_engine import evaluate_journey_stage
from app.services.learning_profile_service import LearningProfileService


def test_journey_stage_rules():
    assert (
        evaluate_journey_stage(
            onboarding_completed=False,
            onboarding_skipped=False,
            has_exam_targets=False,
            streak_days=0,
            total_study_minutes=0,
            exam_count=0,
            question_count=0,
        )
        == JourneyStage.NEW_USER
    )
    assert (
        evaluate_journey_stage(
            onboarding_completed=True,
            onboarding_skipped=False,
            has_exam_targets=True,
            streak_days=2,
            total_study_minutes=100,
            exam_count=0,
            question_count=10,
        )
        == JourneyStage.LEARNING
    )
    assert (
        evaluate_journey_stage(
            onboarding_completed=True,
            onboarding_skipped=False,
            has_exam_targets=True,
            streak_days=8,
            total_study_minutes=100,
            exam_count=1,
            question_count=10,
        )
        == JourneyStage.CONSISTENT
    )


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Learn",
        last_name="Profile",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_onboarding_complete_seeds_subjects(db_session: AsyncSession):
    user = await _user(db_session, f"lp.onboard.{uuid.uuid4().hex[:8]}@studyos.dev")
    svc = LearningProfileService(db_session)
    profile = await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                    target_net=95,
                    target_university="ODTÜ",
                    target_department="Bilgisayar",
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=3,
            daily_study_minutes=150,
            baseline_level=BaselineLevel.BEGINNER,
            baseline_reason="Self-assess",
        ),
    )
    assert profile.onboarding_completed is True
    assert profile.onboarding_required is False
    assert len(profile.exam_targets) == 1
    assert profile.exam_targets[0].target_university == "ODTÜ"
    assert len(profile.subjects) >= 5
    assert profile.journey_stage in {
        JourneyStage.LEARNING,
        JourneyStage.CONSISTENT,
        JourneyStage.ADVANCED,
    }


@pytest.mark.asyncio
async def test_onboarding_skip_still_requires_complete(db_session: AsyncSession):
    """Sprint-3.1.A — skip artık hard gate'i açmaz."""
    user = await _user(db_session, f"lp.skip.{uuid.uuid4().hex[:8]}@studyos.dev")
    svc = LearningProfileService(db_session)
    profile = await svc.skip_onboarding(user.id)
    assert profile.onboarding_skipped is True
    assert profile.onboarding_required is True


@pytest.mark.asyncio
async def test_active_exam_set_and_primary_unchanged(db_session: AsyncSession):
    user = await _user(db_session, f"lp.active.{uuid.uuid4().hex[:8]}@studyos.dev")
    svc = LearningProfileService(db_session)
    await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                    target_net=95,
                ),
                OnboardingExamTargetInput(
                    exam_type=ExamType.YDS_INGILIZCE,
                    is_primary=False,
                    target_score=80,
                ),
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=3,
            daily_study_minutes=150,
            baseline_level=BaselineLevel.BEGINNER,
        ),
    )
    profile = await svc.get_profile(user.id)
    assert profile.primary_exam_type == "tyt"
    assert profile.active_exam_type == "tyt"

    updated = await svc.set_active_exam(user.id, ExamType.YDS_INGILIZCE)
    assert updated.active_exam_type == "yds_ingilizce"
    assert updated.primary_exam_type == "tyt"
    primaries = [t for t in updated.exam_targets if t.is_primary]
    assert len(primaries) == 1
    assert primaries[0].exam_type == ExamType.TYT


def _register(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Learn",
        "last_name": "Api",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_learning_profile_api(client: AsyncClient):
    email = f"lp.api.{uuid.uuid4().hex[:8]}@studyos.dev"
    reg = await client.post("/api/v1/auth/register", json=_register(email))
    assert reg.status_code in (200, 201), reg.text
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    status = await client.get("/api/v1/learning-profile/onboarding/status", headers=headers)
    assert status.status_code == 200, status.text
    assert status.json()["data"]["onboarding_required"] is True
    assert status.json()["data"]["can_skip"] is False

    catalog = await client.get("/api/v1/learning-profile/subjects/catalog", headers=headers)
    assert catalog.status_code == 200
    assert len(catalog.json()["data"]) >= 20

    complete = await client.post(
        "/api/v1/learning-profile/onboarding/complete",
        headers=headers,
        json={
            "exam_targets": [
                {
                    "exam_type": "yks",
                    "is_primary": True,
                    "target_net": 90,
                    "target_university": "Boğaziçi",
                },
                {"exam_type": "yds", "is_primary": False, "target_score": 80},
            ],
            "available_days": [0, 2, 4],
            "available_hours": 2.5,
            "daily_study_minutes": 120,
            "baseline_level": "intermediate",
        },
    )
    assert complete.status_code == 200, complete.text
    body = complete.json()["data"]
    assert body["onboarding_completed"] is True
    assert len(body["exam_targets"]) == 2
    assert len(body["subjects"]) >= 5
    assert body["primary_exam_type"] == "yks"
    assert body["active_exam_type"] == "yks"
    stored_types = {t["exam_type"] for t in body["exam_targets"]}
    assert "yks" in stored_types
    assert "yds_ingilizce" in stored_types

    me = await client.get("/api/v1/learning-profile/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["primary_exam_type"] == "yks"
    assert me.json()["data"]["active_exam_type"] == "yks"

    active = await client.patch(
        "/api/v1/learning-profile/active-exam",
        headers=headers,
        json={"exam_type": "yds"},
    )
    assert active.status_code == 200, active.text
    assert active.json()["data"]["active_exam_type"] == "yds_ingilizce"
    assert active.json()["data"]["primary_exam_type"] == "yks"

    bad = await client.patch(
        "/api/v1/learning-profile/active-exam",
        headers=headers,
        json={"exam_type": "kpss"},
    )
    assert bad.status_code == 400

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    dash_body = dash.json()["data"]
    assert "journey_progress" in dash_body
    assert dash_body["journey_progress"]["journey_stage"]
    assert dash_body["active_exam_type"] == "yds_ingilizce"
    assert dash_body["primary_exam_type"] == "yks"

    dash_override = await client.get(
        "/api/v1/dashboard", headers=headers, params={"exam_type": "yks"}
    )
    assert dash_override.status_code == 200
    assert dash_override.json()["data"]["active_exam_type"] == "yks"

    planner = await client.post("/api/v1/planner/generate", headers=headers, json={})
    assert planner.status_code == 200, planner.text
    assert planner.json()["data"]["target_exam"] == "yks"
