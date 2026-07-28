"""Sprint 21 RC — Beta feedback + analytics unit tests."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.beta_ops import AnalyticsTrackRequest, BetaFeedbackCreate
from app.services.beta_ops_service import AnalyticsService, BetaFeedbackService


async def _user(db: AsyncSession) -> User:
    return await UserRepository(db).add(
        User(
            email=f"beta.{uuid.uuid4()}@studyos.dev",
            hashed_password="x",
            first_name="Beta",
            last_name="User",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            is_verified=False,
        )
    )


@pytest.mark.asyncio
async def test_analytics_track(db_session: AsyncSession) -> None:
    user = await _user(db_session)
    result = await AnalyticsService(db_session).track(
        AnalyticsTrackRequest(name="today_viewed", platform="android"),
        user_id=user.id,
    )
    assert result.name == "today_viewed"


@pytest.mark.asyncio
async def test_feedback_create(db_session: AsyncSession) -> None:
    user = await _user(db_session)
    row = await BetaFeedbackService(db_session).create(
        user.id,
        BetaFeedbackCreate(kind="bug", message="Today kartı boş kalıyor"),
    )
    assert row.kind == "bug"


@pytest.mark.asyncio
async def test_feedback_rejects_bad_kind(db_session: AsyncSession) -> None:
    user = await _user(db_session)
    with pytest.raises(ValidationError):
        await BetaFeedbackService(db_session).create(
            user.id,
            BetaFeedbackCreate(kind="spam", message="geçersiz tür denemesi"),
        )
