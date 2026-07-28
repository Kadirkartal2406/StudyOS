"""
StudyOS — Memory API integration tests
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Mem",
        "last_name": "Api",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_memory_crud_search_privacy(client: AsyncClient):
    headers = await _auth_headers(client, "memory.api@studyos.dev")

    created = await client.post(
        "/api/v1/memory",
        headers=headers,
        json={
            "category": "weak_subject",
            "content": "Fizikte zorlanıyorum",
            "importance": 0.8,
            "source": "manual",
        },
    )
    assert created.status_code == 201, created.text
    mem_id = created.json()["data"]["id"]
    assert created.json()["data"]["metadata"]["embedding_ready"] is False

    listed = await client.get("/api/v1/memory", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) >= 1

    patched = await client.patch(
        f"/api/v1/memory/{mem_id}",
        headers=headers,
        json={"content": "Fizik mekanikte zorlanıyorum", "importance": 0.9},
    )
    assert patched.status_code == 200
    assert "mekanik" in patched.json()["data"]["content"]

    searched = await client.post(
        "/api/v1/memory/search",
        headers=headers,
        json={"q": "fizik", "category": "weak_subject"},
    )
    assert searched.status_code == 200
    assert len(searched.json()["data"]["items"]) >= 1

    settings = await client.get("/api/v1/memory/settings", headers=headers)
    assert settings.status_code == 200
    assert settings.json()["data"]["ai_memory_enabled"] is True

    disabled = await client.patch(
        "/api/v1/memory/settings",
        headers=headers,
        json={"ai_memory_enabled": False},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["ai_memory_enabled"] is False

    exported = await client.get("/api/v1/memory/export", headers=headers)
    assert exported.status_code == 200
    assert exported.json()["data"]["count"] >= 1

    cleared = await client.delete("/api/v1/memory/clear", headers=headers)
    assert cleared.status_code == 200
    assert cleared.json()["data"]["deleted"] >= 1

    empty = await client.get("/api/v1/memory", headers=headers)
    assert empty.status_code == 200
    assert empty.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_chat_writes_memory_when_enabled(client: AsyncClient):
    headers = await _auth_headers(client, "memory.chat@studyos.dev")

    chat = await client.post(
        "/api/v1/ai/chat",
        headers=headers,
        json={"message": "YKS sınavına çalışıyorum ve matematikte zorlanıyorum"},
    )
    assert chat.status_code == 200, chat.text

    listed = await client.get("/api/v1/memory", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_chat_skips_memory_when_disabled(client: AsyncClient):
    headers = await _auth_headers(client, "memory.off@studyos.dev")

    await client.patch(
        "/api/v1/memory/settings",
        headers=headers,
        json={"ai_memory_enabled": False},
    )

    chat = await client.post(
        "/api/v1/ai/chat",
        headers=headers,
        json={"message": "YKS sınavına çalışıyorum ve matematikte zorlanıyorum"},
    )
    assert chat.status_code == 200

    listed = await client.get("/api/v1/memory", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["data"]["items"] == []
