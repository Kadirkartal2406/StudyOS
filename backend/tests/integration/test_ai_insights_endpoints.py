"""
StudyOS — AI Insights Integration + Insight Engine smoke
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegisterRequest
from app.schemas.question_record import QuestionRecordCreate
from app.schemas.study_session import StudySessionFinishRequest, StudySessionStartRequest
from app.services.ai.insight_engine import InsightEngine
from app.services.ai_insights_service import AiInsightsService
from app.services.auth_service import AuthService
from app.services.question_record_service import QuestionRecordService
from app.services.study_session_service import StudySessionService


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "AI",
        "last_name": "Test",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ai_endpoints_empty_user(client: AsyncClient):
    headers = await _auth_headers(client, "ai.empty@studyos.dev")
    for path in (
        "/api/v1/ai/overview",
        "/api/v1/ai/recommendations",
        "/api/v1/ai/trends",
        "/api/v1/ai/performance",
        "/api/v1/ai/productivity",
    ):
        res = await client.get(path, headers=headers)
        assert res.status_code == 200, path
        assert res.json()["success"] is True

    overview = (await client.get("/api/v1/ai/overview", headers=headers)).json()["data"]
    assert overview["has_enough_data"] is False
    assert overview["top_recommendation"]["code"] == "insufficient_data"


@pytest.mark.asyncio
async def test_ai_overview_after_session_and_questions(
    client: AsyncClient, db_session: AsyncSession
):
    user, _, _ = await AuthService(db_session).register(
        RegisterRequest(
            email="ai.data@studyos.dev",
            password="GucluSifre123!",
            first_name="AI",
            last_name="Data",
            role="student",
        )
    )
    await StudySessionService(db_session).start(
        user.id,
        StudySessionStartRequest(planned_duration_minutes=25, break_duration_minutes=5),
    )
    await StudySessionService(db_session).finish(
        user.id,
        StudySessionFinishRequest(completed_questions=5),
    )
    await QuestionRecordService(db_session).create(
        user.id,
        QuestionRecordCreate(
            subject="Matematik",
            question_count=20,
            correct_count=10,
            wrong_count=8,
            blank_count=2,
            duration_minutes=40,
            exam_type="tyt",
        ),
    )

    overview = await AiInsightsService(db_session).get_overview(user.id)
    assert overview.has_enough_data is True
    assert overview.correct_rate == 50.0
    # correct_rate from question records
    perf = await AiInsightsService(db_session).get_performance(user.id)
    assert perf.total_questions == 20
    assert perf.correct_rate == 50.0

    ctx = await InsightEngine(db_session).build_context(user.id)
    assert ctx.has_enough_data is True
    assert "Matematik" in [s[0] for s in ctx.low_accuracy_subjects] or ctx.correct_rate == 50.0


@pytest.mark.asyncio
async def test_dashboard_includes_ai_recommendation(client: AsyncClient):
    headers = await _auth_headers(client, "ai.dash@studyos.dev")
    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    data = dash.json()["data"]
    assert "today_ai_recommendation" in data
    assert data["today_ai_recommendation"] is not None
