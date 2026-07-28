"""Sprint 18 — Score estimation & ranking snapshot unit tests."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import (
    AssessmentKind,
    AssessmentSession,
    AssessmentSessionStatus,
)
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.services.score_estimation_service import ScoreEstimationService


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"assess.{uuid.uuid4()}@studyos.dev",
        hashed_password="irrelevant",
        first_name="Assess",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=False,
    )
    return await UserRepository(db).add(user)


@pytest.mark.asyncio
async def test_score_estimation_empty(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    snap = await ScoreEstimationService(db_session).refresh(user.id, "kpss")
    assert snap.estimated_score == 0.0
    assert snap.estimated_success_pct == 0.0
    assert snap.peer_sample_size == 0
    assert "Henüz" in (snap.commentary or "")


@pytest.mark.asyncio
async def test_score_estimation_from_sessions(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    for acc, subject in ((0.8, "Türkçe"), (0.4, "Matematik")):
        s = AssessmentSession(
            user_id=user.id,
            exam_type="kpss",
            kind=AssessmentKind.INITIAL_CALIBRATION,
            subject_code=subject.lower(),
            subject_name=subject,
            topic_code="t1",
            status=AssessmentSessionStatus.SUBMITTED,
            difficulty="medium",
            requested_count=5,
            correct_count=int(acc * 5),
            wrong_count=5 - int(acc * 5),
            blank_count=0,
            accuracy=acc,
        )
        db_session.add(s)
    await db_session.flush()

    snap = await ScoreEstimationService(db_session).refresh(user.id, "kpss")
    assert snap.estimated_success_pct == pytest.approx(60.0, abs=0.1)
    assert snap.strongest_subject == "Türkçe"
    assert snap.weakest_subject == "Matematik"
    assert snap.peer_sample_size >= 1
