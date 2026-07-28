"""
StudyOS — AI Chat integration tests
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Chat",
        "last_name": "Test",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ai_chat_create_list_get_delete(client: AsyncClient):
    headers = await _auth_headers(client, "chat.api@studyos.dev")

    chat = await client.post(
        "/api/v1/ai/chat",
        headers=headers,
        json={"message": "Bugün ne çalışmalıyım?"},
    )
    assert chat.status_code == 200, chat.text
    body = chat.json()["data"]
    conv_id = body["conversation"]["id"]
    assert body["user_message"]["role"] == "user"
    assert body["assistant_message"]["role"] == "assistant"
    assert len(body["assistant_message"]["content"]) > 0

    listed = await client.get("/api/v1/ai/conversations", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) >= 1

    detail = await client.get(f"/api/v1/ai/conversations/{conv_id}", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["data"]["messages"]) >= 2

    follow = await client.post(
        "/api/v1/ai/chat",
        headers=headers,
        json={"message": "Hedeflerime ne dersin?", "conversation_id": conv_id},
    )
    assert follow.status_code == 200

    deleted = await client.delete(f"/api/v1/ai/conversations/{conv_id}", headers=headers)
    assert deleted.status_code == 200

    gone = await client.get(f"/api/v1/ai/conversations/{conv_id}", headers=headers)
    assert gone.status_code == 404
