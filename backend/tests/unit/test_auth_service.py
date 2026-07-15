"""
StudyOS — AuthService Birim Testleri
Servis katmanının register/login/refresh/logout iş mantığını doğrular.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import verify_password
from app.models.user import UserRole
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


def _register_payload(email: str = "unit.test@studyos.dev") -> RegisterRequest:
    return RegisterRequest(
        email=email,
        password="GucluSifre123!",
        first_name="Unit",
        last_name="Test",
        role=UserRole.STUDENT,
    )


@pytest.mark.asyncio
async def test_register_creates_user_with_hashed_password(db_session: AsyncSession):
    service = AuthService(db_session)

    user, access_token, refresh_token = await service.register(_register_payload())

    assert user.email == "unit.test@studyos.dev"
    assert user.hashed_password != "GucluSifre123!"
    assert verify_password("GucluSifre123!", user.hashed_password)
    assert access_token
    assert refresh_token


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(db_session: AsyncSession):
    service = AuthService(db_session)
    await service.register(_register_payload("duplicate@studyos.dev"))

    with pytest.raises(ConflictError):
        await service.register(_register_payload("duplicate@studyos.dev"))


@pytest.mark.asyncio
async def test_login_succeeds_with_correct_credentials(db_session: AsyncSession):
    service = AuthService(db_session)
    await service.register(_register_payload("login.ok@studyos.dev"))

    user, access_token, refresh_token = await service.login(
        LoginRequest(email="login.ok@studyos.dev", password="GucluSifre123!")
    )

    assert user.email == "login.ok@studyos.dev"
    assert access_token
    assert refresh_token


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(db_session: AsyncSession):
    service = AuthService(db_session)
    await service.register(_register_payload("login.fail@studyos.dev"))

    with pytest.raises(AuthenticationError):
        await service.login(LoginRequest(email="login.fail@studyos.dev", password="yanlis"))


@pytest.mark.asyncio
async def test_login_fails_for_unknown_email(db_session: AsyncSession):
    service = AuthService(db_session)

    with pytest.raises(AuthenticationError):
        await service.login(LoginRequest(email="yok@studyos.dev", password="GucluSifre123!"))


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_invalidates_old_one(db_session: AsyncSession):
    service = AuthService(db_session)
    _, _, refresh_token = await service.register(_register_payload("refresh.ok@studyos.dev"))

    new_access, new_refresh = await service.refresh(refresh_token)

    assert new_access
    assert new_refresh != refresh_token

    with pytest.raises(AuthenticationError):
        await service.refresh(refresh_token)


@pytest.mark.asyncio
async def test_refresh_fails_for_unknown_token(db_session: AsyncSession):
    service = AuthService(db_session)

    with pytest.raises(AuthenticationError):
        await service.refresh("gecersiz-refresh-token")


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(db_session: AsyncSession):
    service = AuthService(db_session)
    _, _, refresh_token = await service.register(_register_payload("logout.ok@studyos.dev"))

    await service.logout(refresh_token)

    with pytest.raises(AuthenticationError):
        await service.refresh(refresh_token)


@pytest.mark.asyncio
async def test_logout_is_idempotent_for_unknown_token(db_session: AsyncSession):
    service = AuthService(db_session)
    await service.logout("bilinmeyen-token")
