"""
Alignment Sprint-1 — Today Projection HTTP entegrasyon testleri.

Mevcut test_dashboard_endpoints.py'ye dokunmaz.
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Today",
        "last_name": "Proj",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_dashboard_http_always_returns_single_next_action(
    client: AsyncClient,
):
    register_res = await client.post(
        "/api/v1/auth/register",
        json=_register_body("today.http.empty@studyos.dev"),
    )
    token = register_res.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert "next_action" in data
    assert data["next_action"] is not None
    assert "next_actions" not in data
    assert data["next_action"]["reason"].strip()
    assert data["next_action"]["action_type"] == "focus"
    assert data["next_action"]["confidence_tone"] == "low"
    assert isinstance(data["today_context_lines"], list)
    assert len(data["today_context_lines"]) <= 3
    # Journey line ikincil alan — Primary Action değil
    assert "today_journey_line" in data
    if data["today_journey_line"] is not None:
        assert isinstance(data["today_journey_line"], str)


@pytest.mark.asyncio
async def test_dashboard_http_plan_becomes_study_plan_next_action(
    client: AsyncClient,
):
    from datetime import UTC, datetime

    register_res = await client.post(
        "/api/v1/auth/register",
        json=_register_body("today.http.plan@studyos.dev"),
    )
    token = register_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    today = datetime.now(UTC).date().isoformat()

    create = await client.post(
        "/api/v1/study-plans",
        headers=headers,
        json={
            "title": "Geometri",
            "subject": "Matematik",
            "topic": "Üçgen",
            "target_question_count": 15,
            "estimated_minutes": 30,
            "study_date": today,
        },
    )
    assert create.status_code in {200, 201}, create.text

    response = await client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    action = data["next_action"]
    assert action["action_type"] == "study_plan"
    assert action["reason"].strip()
    assert action["title"] == "Bu konu üzerinde çalış"
    assert action["deep_link_hint"].startswith("/subjects")
    assert action["deep_link_hint"] != "/study-plan"
    assert len(data["today_context_lines"]) <= 3
