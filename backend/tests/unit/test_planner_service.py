"""
StudyOS — Planner service unit / integration helpers
"""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.schemas.planner import PlannerAcceptRequest, PlannerGenerateRequest
from app.services.planner_service import PlannerService
from app.models.question_record import ExamType


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Plan",
        last_name="Unit",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_generate_includes_item_reasons(db_session: AsyncSession):
    user = await _user(db_session, "planner.unit@studyos.dev")
    svc = PlannerService(db_session)
    draft = await svc.generate(
        user.id,
        PlannerGenerateRequest(
            target_exam=ExamType.TYT,
            target_net=90,
            available_days=[0, 2, 4],
            available_hours=2.0,
        ),
    )
    assert draft.status.value == "draft"
    assert len(draft.items) >= 1
    assert all(i.reason for i in draft.items)
    assert draft.rationale.get("overview")
    assert draft.summary.get("used_fallback_template") is True


@pytest.mark.asyncio
async def test_accept_creates_study_plans(db_session: AsyncSession):
    user = await _user(db_session, "planner.accept@studyos.dev")
    svc = PlannerService(db_session)
    draft = await svc.generate(
        user.id,
        PlannerGenerateRequest(
            target_exam=ExamType.TYT,
            target_net=85,
            available_days=[1, 3],
            available_hours=1.5,
        ),
    )
    result = await svc.accept(draft.id, user.id, PlannerAcceptRequest(force=False))
    assert result.draft.status.value == "accepted"
    assert len(result.created_plans) >= 1
    assert all(p.source == "planner" for p in result.created_plans)
    assert all(p.planner_draft_id == draft.id for p in result.created_plans)


def _register(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Plan",
        "last_name": "Api",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_planner_api_flow(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=_register("planner.api@studyos.dev"))
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    gen = await client.post(
        "/api/v1/planner/generate",
        headers=headers,
        json={
            "target_exam": "tyt",
            "target_net": 90,
            "available_days": [0, 1, 2],
            "available_hours": 2,
        },
    )
    assert gen.status_code == 200, gen.text
    draft_id = gen.json()["data"]["id"]
    assert gen.json()["data"]["items"][0]["reason"]

    got = await client.get(f"/api/v1/planner/{draft_id}", headers=headers)
    assert got.status_code == 200

    explained = await client.post(f"/api/v1/planner/{draft_id}/explain", headers=headers)
    assert explained.status_code == 200, explained.text
    assert explained.json()["data"]["explanation"]
    assert explained.json()["data"]["item_reasons"]

    accepted = await client.post(
        f"/api/v1/planner/{draft_id}/accept",
        headers=headers,
        json={"force": False},
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["data"]["draft"]["status"] == "accepted"

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
