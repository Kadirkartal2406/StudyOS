"""
StudyOS — Notification Settings unit + service testleri (Sprint-1.8)
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.notification_settings import FcmTokenUpdate, NotificationSettingsUpdate
from app.services.notification_settings_service import NotificationSettingsService


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"notif.{uuid.uuid4()}@studyos.dev",
        hashed_password="x",
        first_name="Ayşe",
        last_name="Yılmaz",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    return await UserRepository(db).add(user)


@pytest.mark.asyncio
async def test_get_settings_creates_defaults(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    settings = await NotificationSettingsService(db_session).get_settings(user.id)
    assert settings.pomodoro_enabled is True
    assert settings.daily_reminder_enabled is True
    assert settings.has_fcm_token is False
    assert settings.reminder_time is not None


@pytest.mark.asyncio
async def test_update_settings_and_fcm_token(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    service = NotificationSettingsService(db_session)

    updated = await service.update_settings(
        user.id,
        NotificationSettingsUpdate(
            pomodoro_enabled=False,
            quiet_hours_enabled=True,
            quiet_hours_start=__import__("datetime").time(22, 0),
            quiet_hours_end=__import__("datetime").time(7, 0),
        ),
    )
    assert updated.pomodoro_enabled is False
    assert updated.quiet_hours_enabled is True

    with_token = await service.update_fcm_token(
        user.id, FcmTokenUpdate(fcm_token="fcm-test-token-abcdefghij")
    )
    assert with_token.has_fcm_token is True
