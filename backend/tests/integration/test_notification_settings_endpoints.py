"""
StudyOS — Notification Settings endpoint entegrasyon testleri
"""

import pytest
from httpx import AsyncClient


def _register(email: str = "notif.api@studyos.dev") -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Notif",
        "last_name": "User",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_notification_settings_get_put_fcm(client: AsyncClient) -> None:
    reg = await client.post("/api/v1/auth/register", json=_register())
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    get_res = await client.get("/api/v1/notification-settings", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["pomodoro_enabled"] is True

    put_res = await client.put(
        "/api/v1/notification-settings",
        headers=headers,
        json={"streak_reminder_enabled": False, "widget_auto_update_enabled": False},
    )
    assert put_res.status_code == 200
    assert put_res.json()["data"]["streak_reminder_enabled"] is False
    assert put_res.json()["data"]["widget_auto_update_enabled"] is False

    fcm = await client.put(
        "/api/v1/notification-settings/fcm-token",
        headers=headers,
        json={"fcm_token": "device-fcm-token-1234567890"},
    )
    assert fcm.status_code == 200
    assert fcm.json()["data"]["has_fcm_token"] is True
