"""
StudyOS — Auth Endpoint Entegrasyon Testleri
Gerçek HTTP isteği (ASGITransport) üzerinden /auth ve /users/me akışlarını doğrular.
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str = "integration@studyos.dev") -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Integration",
        "last_name": "Test",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_register_returns_tokens_and_user(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json=_register_body())

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["data"]["user"]["email"] == "integration@studyos.dev"
    assert body["data"]["user"]["is_active"] is True


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=_register_body("dup@studyos.dev"))
    response = await client.post("/api/v1/auth/register", json=_register_body("dup@studyos.dev"))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_rejects_short_password(client: AsyncClient):
    body = _register_body("short.pw@studyos.dev")
    body["password"] = "short"

    response = await client.post("/api/v1/auth/register", json=body)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_returns_tokens_for_valid_credentials(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=_register_body("login@studyos.dev"))

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@studyos.dev", "password": "GucluSifre123!"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=_register_body("login.wrong@studyos.dev"))

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login.wrong@studyos.dev", "password": "yanlissifre"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_get_current_user_returns_profile(client: AsyncClient):
    register_res = await client.post("/api/v1/auth/register", json=_register_body("me@studyos.dev"))
    access_token = register_res.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["email"] == "me@studyos.dev"


@pytest.mark.asyncio
async def test_get_current_user_without_token_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token_returns_401(client: AsyncClient):
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer gecersiz.token.deger"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_tokens(client: AsyncClient):
    register_res = await client.post(
        "/api/v1/auth/register", json=_register_body("refresh@studyos.dev")
    )
    refresh_token = register_res.json()["data"]["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    new_refresh_token = response.json()["data"]["refresh_token"]
    assert new_refresh_token != refresh_token

    reuse_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert reuse_response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client: AsyncClient):
    register_res = await client.post(
        "/api/v1/auth/register", json=_register_body("logout@studyos.dev")
    )
    refresh_token = register_res.json()["data"]["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )
    assert logout_response.status_code == 204

    reuse_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert reuse_response.status_code == 401
