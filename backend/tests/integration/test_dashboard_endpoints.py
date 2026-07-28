"""
StudyOS — Dashboard Endpoint Entegrasyon Testleri
"""

from datetime import date

import pytest
from httpx import AsyncClient

from app.core.constants import DEFAULT_DAILY_STUDY_GOAL_MINUTES


def _register_body(email: str = "dashboard.user@studyos.dev") -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Dashboard",
        "last_name": "Kullanıcı",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_get_dashboard_returns_summary_for_authenticated_user(client: AsyncClient):
    register_res = await client.post("/api/v1/auth/register", json=_register_body())
    access_token = register_res.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/dashboard", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["first_name"] == "Dashboard"
    assert data["daily_study_goal_minutes"] == DEFAULT_DAILY_STUDY_GOAL_MINUTES
    assert data["today_study_minutes"] == 0
    assert data["today_questions_solved"] == 0
    assert data["today_studied_topic"] is None
    assert data["daily_progress_percentage"] == 0.0
    assert data["today_plan_count"] == 0
    assert data["completed_plan_count"] == 0
    assert data["today_plans"] == []
    assert "last_login_at" in data
    assert data["recent_activities"] == []
    assert "today_ai_recommendation_reason" in data
    assert "primary_target" in data
    assert "active_target" in data
    assert data["next_action"] is not None
    assert data["next_action"]["cta_label"]
    assert data["next_action"]["action_type"] in {
        "revision",
        "study_plan",
        "focus",
    }
    assert "today_context_lines" in data
    assert "today_journey_line" in data


@pytest.mark.asyncio
async def test_get_dashboard_includes_primary_target_after_onboarding(
    client: AsyncClient,
):
    email = "dashboard.target@studyos.dev"
    register_res = await client.post("/api/v1/auth/register", json=_register_body(email))
    access_token = register_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    complete = await client.post(
        "/api/v1/learning-profile/onboarding/complete",
        headers=headers,
        json={
            "exam_targets": [
                {
                    "exam_type": "yks",
                    "is_primary": True,
                    "target_net": 95,
                    "target_university": "ODTÜ",
                    "target_department": "Bilgisayar",
                },
                {"exam_type": "yds", "is_primary": False, "target_score": 85},
            ],
            "available_days": [0, 1, 2, 3, 4],
            "available_hours": 2.5,
            "daily_study_minutes": 120,
            "baseline_level": "intermediate",
        },
    )
    assert complete.status_code == 200, complete.text

    response = await client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["primary_exam_type"] == "yks"
    assert data["primary_target"] is not None
    assert data["primary_target"]["target_university"] == "ODTÜ"
    assert data["primary_target"]["target_department"] == "Bilgisayar"
    assert data["primary_target"]["target_net"] == 95
    assert data["active_target"] is not None
    assert data["active_target"]["exam_type"] == "yks"
    # AI tip reason (RuleEngine) present when recommendation exists
    if data.get("today_ai_recommendation"):
        assert data.get("today_ai_recommendation_reason")


@pytest.mark.asyncio
async def test_get_dashboard_reflects_todays_plans_and_sessions(client: AsyncClient):
    register_res = await client.post(
        "/api/v1/auth/register", json=_register_body("dashboard.plan@studyos.dev")
    )
    access_token = register_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    create_res = await client.post(
        "/api/v1/study-plans",
        json={
            "title": "Geometri Tekrarı",
            "subject": "Matematik",
            "topic": "Üçgenler",
            "target_question_count": 20,
            "estimated_minutes": 50,
            "study_date": str(date.today()),
        },
        headers=headers,
    )
    plan_id = create_res.json()["data"]["id"]

    await client.patch(
        f"/api/v1/study-plans/{plan_id}/complete",
        json={"completed_question_count": 18, "completed_minutes": 45},
        headers=headers,
    )

    # Sprint-1.5: süre/soru tamamlanmış StudySession'dan gelir.
    start = await client.post(
        "/api/v1/study-sessions/start",
        json={"planned_duration_minutes": 25},
        headers=headers,
    )
    assert start.status_code == 201
    finish = await client.post(
        "/api/v1/study-sessions/finish",
        json={"completed_questions": 18},
        headers=headers,
    )
    assert finish.status_code == 200

    response = await client.get("/api/v1/dashboard", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["today_plan_count"] == 1
    assert data["completed_plan_count"] == 1
    # B1: Session completed_questions Dashboard'a yansımaz; QuestionRecord gerekir.
    assert data["today_questions_solved"] == 0
    assert data["daily_study_goal_minutes"] == 50
    assert len(data["today_plans"]) == 1
    # Plan complete + session start/finish → activities
    assert len(data["recent_activities"]) >= 2
    event_types = {a["event_type"] for a in data["recent_activities"]}
    assert "plan_completed" in event_types
    assert "session_completed" in event_types


@pytest.mark.asyncio
async def test_get_dashboard_without_token_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/dashboard")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_dashboard_with_invalid_token_returns_401(client: AsyncClient):
    response = await client.get(
        "/api/v1/dashboard", headers={"Authorization": "Bearer gecersiz.token.deger"}
    )

    assert response.status_code == 401
