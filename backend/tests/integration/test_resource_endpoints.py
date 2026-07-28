"""
StudyOS — Study Resources integration tests
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Res",
        "last_name": "Test",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_resource_crud_open_stats(client: AsyncClient):
    headers = await _auth_headers(client, "resource.api@studyos.dev")

    created = await client.post(
        "/api/v1/resources",
        headers=headers,
        json={
            "title": "TYT Matematik",
            "resource_type": "youtube",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "duration_seconds": 600,
            "provider": "youtube",
        },
    )
    assert created.status_code == 201, created.text
    rid = created.json()["data"]["id"]
    assert created.json()["data"]["metadata"]["youtube_ready"] is False

    listed = await client.get("/api/v1/resources", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) >= 1

    opened = await client.post(f"/api/v1/resources/{rid}/open", headers=headers)
    assert opened.status_code == 200
    assert opened.json()["data"]["status"] == "in_progress"
    assert opened.json()["data"]["last_opened_at"] is not None

    patched = await client.patch(
        f"/api/v1/resources/{rid}",
        headers=headers,
        json={"status": "completed", "order_index": 2},
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["status"] == "completed"
    assert patched.json()["data"]["completed_at"] is not None

    stats = await client.get("/api/v1/resources/statistics", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["data"]["total_count"] >= 1
    assert stats.json()["data"]["completed_count"] >= 1

    deleted = await client.delete(f"/api/v1/resources/{rid}", headers=headers)
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_plan_nested_resources(client: AsyncClient):
    headers = await _auth_headers(client, "resource.plan@studyos.dev")

    plan = await client.post(
        "/api/v1/study-plans",
        headers=headers,
        json={
            "title": "Fizik",
            "subject": "Fizik",
            "target_question_count": 10,
            "estimated_minutes": 45,
            "study_date": "2026-07-17",
        },
    )
    assert plan.status_code == 201, plan.text
    plan_id = plan.json()["data"]["id"]

    created = await client.post(
        f"/api/v1/study-plans/{plan_id}/resources",
        headers=headers,
        json={
            "title": "Newton",
            "resource_type": "website",
            "url": "https://example.com/newton",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["data"]["study_plan_id"] == plan_id

    listed = await client.get(
        f"/api/v1/study-plans/{plan_id}/resources", headers=headers
    )
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_dashboard_includes_resources(client: AsyncClient):
    headers = await _auth_headers(client, "resource.dash@studyos.dev")
    await client.post(
        "/api/v1/resources",
        headers=headers,
        json={"title": "Not", "resource_type": "note"},
    )
    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    body = dash.json()["data"]
    assert "today_resources_opened" in body
    assert "recent_resources" in body
