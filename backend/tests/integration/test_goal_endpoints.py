"""
StudyOS — Goal API integration tests
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Goal",
        "last_name": "Api",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_goals_crud_and_filters(client: AsyncClient):
    headers = await _auth_headers(client, "goal.api@studyos.dev")
    create = await client.post(
        "/api/v1/goals",
        headers=headers,
        json={
            "title": "Haftalık 30 Pomodoro",
            "goal_type": "pomodoro",
            "target_value": 30,
            "period": "weekly",
            "priority": "high",
            "start_date": "2026-07-13",
            "end_date": "2026-07-19",
        },
    )
    assert create.status_code == 201, create.text
    goal_id = create.json()["data"]["id"]

    active = await client.get("/api/v1/goals/active", headers=headers)
    assert active.status_code == 200
    assert len(active.json()["data"]["items"]) >= 1

    progress = await client.get("/api/v1/goals/progress", headers=headers)
    assert progress.status_code == 200
    assert progress.json()["data"]["active_count"] >= 1

    weekly = await client.get("/api/v1/goals/weekly", headers=headers)
    assert weekly.status_code == 200

    detail = await client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["title"] == "Haftalık 30 Pomodoro"

    patched = await client.patch(
        f"/api/v1/goals/{goal_id}",
        headers=headers,
        json={"title": "Güncellendi"},
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["title"] == "Güncellendi"

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    assert "weekly_goals" in dash.json()["data"]

    deleted = await client.delete(f"/api/v1/goals/{goal_id}", headers=headers)
    assert deleted.status_code == 200
