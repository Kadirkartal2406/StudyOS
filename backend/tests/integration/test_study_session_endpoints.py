"""
StudyOS — StudySession Endpoint Entegrasyon Testleri
"""

from datetime import date

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Pomodoro",
        "last_name": "Kullanıcı",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    assert res.status_code == 201
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_start_pause_resume_finish_flow(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "session.flow@studyos.dev")

    start = await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 25, "break_duration_minutes": 5},
        headers=headers,
    )
    assert start.status_code == 201
    data = start.json()["data"]
    assert data["status"] == "running"
    assert data["planned_duration_minutes"] == 25

    pause = await client.post("/api/v1/study-sessions/pause", headers=headers)
    assert pause.status_code == 200
    assert pause.json()["data"]["status"] == "paused"

    resume = await client.post("/api/v1/study-sessions/resume", headers=headers)
    assert resume.status_code == 200
    assert resume.json()["data"]["status"] == "running"

    finish = await client.post(
        "/api/v1/study-sessions/finish",
        json={"completed_questions": 12, "completed_topics": 1},
        headers=headers,
    )
    assert finish.status_code == 200
    finished = finish.json()["data"]
    assert finished["status"] == "completed"
    assert finished["completed_questions"] == 12
    assert finished["ended_at"] is not None


@pytest.mark.asyncio
async def test_start_while_active_returns_409(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "session.conflict@studyos.dev")

    first = await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 25},
        headers=headers,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 50},
        headers=headers,
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_finish_without_active_returns_404(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "session.nofinish@studyos.dev")

    response = await client.post("/api/v1/study-sessions/finish", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_today_history_and_statistics(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "session.stats@studyos.dev")

    await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 25},
        headers=headers,
    )
    await client.post(
        "/api/v1/study-sessions/finish",
        json={"completed_questions": 7},
        headers=headers,
    )

    today = await client.get("/api/v1/study-sessions/today", headers=headers)
    assert today.status_code == 200
    assert len(today.json()["data"]) == 1

    history = await client.get(
        "/api/v1/study-sessions/history?page=1&page_size=10", headers=headers
    )
    assert history.status_code == 200
    body = history.json()
    assert len(body["data"]) == 1
    assert body["pagination"]["total_items"] == 1

    stats = await client.get("/api/v1/study-sessions/statistics", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["data"]["completed_sessions"] == 1
    assert stats.json()["data"]["total_questions"] == 7


@pytest.mark.asyncio
async def test_finish_updates_linked_plan_and_dashboard(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "session.planlink@studyos.dev")

    plan_res = await client.post(
        "/api/v1/study-plans",
        json={
            "title": "Fizik",
            "subject": "Fizik",
            "topic": "Kuvvet",
            "target_question_count": 20,
            "estimated_minutes": 50,
            "study_date": str(date.today()),
        },
        headers=headers,
    )
    plan_id = plan_res.json()["data"]["id"]

    await client.post(
        "/api/v1/study-sessions/start",
        json={
            "planned_duration_minutes": 25,
            "break_duration_minutes": 5,
            "study_plan_id": plan_id,
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/study-sessions/finish",
        json={"completed_questions": 9},
        headers=headers,
    )

    plan = await client.get(f"/api/v1/study-plans/{plan_id}", headers=headers)
    plan_data = plan.json()["data"]
    assert plan_data["status"] == "in_progress"
    assert plan_data["completed_question_count"] == 9

    dashboard = await client.get("/api/v1/dashboard", headers=headers)
    dash = dashboard.json()["data"]
    # B1: plan progress Session'dan; Dashboard soru sayısı QuestionRecord'dan.
    assert dash["today_questions_solved"] == 0
    assert dash["today_study_minutes"] >= 0
    assert dash["today_plan_count"] == 1
    assert dash["completed_plan_count"] == 0


@pytest.mark.asyncio
async def test_start_validation_rejects_zero_duration(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "session.validation@studyos.dev")

    response = await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 0},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_endpoints_require_auth(client: AsyncClient) -> None:
    assert (await client.post("/api/v1/study-sessions/start", json={})).status_code == 401
    assert (await client.post("/api/v1/study-sessions/pause")).status_code == 401
    assert (await client.get("/api/v1/study-sessions/today")).status_code == 401
