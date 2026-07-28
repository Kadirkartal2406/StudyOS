"""
StudyOS — AI Settings + stream stub integration tests
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Ai",
        "last_name": "Set",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ai_settings_get_and_patch(client: AsyncClient):
    headers = await _auth_headers(client, "ai.settings@studyos.dev")

    got = await client.get("/api/v1/ai/settings", headers=headers)
    assert got.status_code == 200, got.text
    data = got.json()["data"]
    assert data["effective_provider"] in {"null", "gemini", "openai", "claude"}
    assert "null" in data["available_providers"]
    assert data["streaming_enabled"] is False

    patched = await client.patch(
        "/api/v1/ai/settings",
        headers=headers,
        json={"preferred_provider": "null", "preferred_model": "template"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["data"]["preferred_provider"] == "null"


@pytest.mark.asyncio
async def test_chat_stream_stub_501(client: AsyncClient):
    headers = await _auth_headers(client, "ai.stream@studyos.dev")
    res = await client.post("/api/v1/ai/chat/stream", headers=headers)
    assert res.status_code == 501
    assert res.json()["error"]["code"] == "STREAMING_NOT_IMPLEMENTED"


@pytest.mark.asyncio
async def test_chat_still_works_with_null(client: AsyncClient):
    headers = await _auth_headers(client, "ai.chat24@studyos.dev")
    chat = await client.post(
        "/api/v1/ai/chat",
        headers=headers,
        json={"message": "Bugün ne çalışayım?"},
    )
    assert chat.status_code == 200, chat.text
    meta = chat.json()["data"]["assistant_message"]["metadata"]
    assert "provider" in meta
