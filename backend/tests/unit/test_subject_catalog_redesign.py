"""Sprint-3.1.C.x — Subject catalog redesign tests."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_profile import BaselineLevel
from app.models.question_record import ExamType
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.learning_profile import OnboardingCompleteRequest, OnboardingExamTargetInput
from app.services.ai.subject_catalog_seed import (
    KPSS_SUBJECT_CODES,
    TYT_SUBJECT_CODES,
    YKS_AYT_BY_BRANCH,
    codes_for_exam,
)
from app.services.learning_profile_service import LearningProfileService


async def _user(db: AsyncSession) -> User:
    user = User(
        email=f"cat.{uuid.uuid4().hex[:8]}@studyos.dev",
        hashed_password="x",
        first_name="Cat",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    return await UserRepository(db).add(user)


def test_codes_for_exam_yks_tyt_common_ayt_by_branch():
    sayisal = codes_for_exam("yks", "sayisal")
    assert sayisal is not None
    assert set(TYT_SUBJECT_CODES).issubset(sayisal)
    assert "tyt_tarih" in sayisal
    assert set(YKS_AYT_BY_BRANCH["sayisal"]).issubset(sayisal)
    assert "ayt_edebiyat" not in sayisal

    ea = codes_for_exam("yks", "ea")
    assert "ayt_edebiyat" in ea
    assert "ayt_fizik" not in ea
    assert "tyt_fizik" in ea


def test_codes_for_exam_kpss_ders_not_gy_gk():
    codes = codes_for_exam("kpss", "lisans")
    assert codes == set(KPSS_SUBJECT_CODES)
    assert "kpss_gy" not in codes
    assert "kpss_gk" not in codes


@pytest.mark.asyncio
async def test_catalog_sync_and_yks_sayisal_seed(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    await svc.ensure_catalog_synced()

    profile = await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                    branch="sayisal",
                    target_net=90,
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=2.5,
            daily_study_minutes=120,
            baseline_level=BaselineLevel.BEGINNER,
        ),
    )
    codes = {s.subject_code for s in profile.subjects}
    names = {s.subject_name for s in profile.subjects}
    assert "tyt_tarih" in codes
    assert "tyt_sosyal" not in codes
    assert "ayt_matematik" in codes
    assert "ayt_edebiyat" not in codes
    assert "Sosyal Bilimler" not in names
    assert "Genel Yetenek" not in names

    subjects = await svc.list_my_subjects(user.id)
    list_codes = {s.subject_code for s in subjects}
    assert "tyt_geometri" in list_codes
    assert "ayt_fizik" in list_codes
    assert "ayt_tarih_1" not in list_codes


@pytest.mark.asyncio
async def test_kpss_seeds_ders_subjects(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    profile = await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.KPSS_LISANS,
                    is_primary=True,
                    branch="lisans",
                )
            ],
            available_days=[0, 1, 2],
            available_hours=2,
            daily_study_minutes=90,
            baseline_level=BaselineLevel.UNKNOWN,
        ),
    )
    codes = {s.subject_code for s in profile.subjects}
    names = {s.subject_name for s in profile.subjects}
    assert codes == set(KPSS_SUBJECT_CODES)
    assert "Genel Yetenek" not in names
    assert "Genel Kültür" not in names
    assert "Türkçe" in names
    assert "Vatandaşlık" in names


@pytest.mark.asyncio
async def test_yks_without_branch_seeds_tyt_only(db_session: AsyncSession):
    user = await _user(db_session)
    svc = LearningProfileService(db_session)
    profile = await svc.complete_onboarding(
        user.id,
        OnboardingCompleteRequest(
            exam_targets=[
                OnboardingExamTargetInput(
                    exam_type=ExamType.TYT,
                    is_primary=True,
                )
            ],
            available_days=[0, 1, 2, 3, 4],
            available_hours=2,
            daily_study_minutes=100,
            baseline_level=BaselineLevel.UNKNOWN,
        ),
    )
    codes = {s.subject_code for s in profile.subjects}
    assert set(TYT_SUBJECT_CODES).issubset(codes)
    assert not any(c.startswith("ayt_") for c in codes)
