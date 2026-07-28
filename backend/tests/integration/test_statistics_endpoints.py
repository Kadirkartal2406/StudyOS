"""
StudyOS — Statistics Endpoint Entegrasyon Testleri
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Stats",
        "last_name": "User",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['data']['access_token']}"}


@pytest.mark.asyncio
async def test_statistics_endpoints_require_auth(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/statistics/overview")).status_code == 401
    assert (await client.get("/api/v1/statistics/daily")).status_code == 401
    assert (await client.get("/api/v1/statistics/heatmap")).status_code == 401


@pytest.mark.asyncio
async def test_statistics_overview_and_related(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "stats.endpoints@studyos.dev")

    start = await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 25, "break_duration_minutes": 5},
        headers=headers,
    )
    assert start.status_code == 201
    finish = await client.post(
        "/api/v1/study-sessions/finish",
        json={"completed_questions": 6},
        headers=headers,
    )
    assert finish.status_code == 200

    overview = await client.get("/api/v1/statistics/overview", headers=headers)
    assert overview.status_code == 200
    data = overview.json()["data"]
    assert data["total_pomodoros"] == 1
    assert data["today_questions"] == 6
    assert data["streak_days"] >= 1

    for path in (
        "/statistics/daily",
        "/statistics/weekly",
        "/statistics/monthly",
        "/statistics/subjects",
        "/statistics/topics",
        "/statistics/productivity",
        "/statistics/heatmap",
        "/statistics/streak",
    ):
        res = await client.get(f"/api/v1{path}", headers=headers)
        assert res.status_code == 200, path
        assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_dashboard_includes_statistics_fields(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "stats.dashboard@studyos.dev")

    await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 25},
        headers=headers,
    )
    await client.post(
        "/api/v1/study-sessions/finish",
        json={"completed_questions": 4},
        headers=headers,
    )

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    data = dash.json()["data"]
    assert data["today_questions_solved"] == 0
    assert data["streak_days"] >= 1
    assert data["total_pomodoros"] == 1
    assert "week_study_minutes" in data
    assert "average_session_minutes" in data
