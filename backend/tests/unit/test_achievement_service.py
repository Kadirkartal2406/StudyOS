"""
StudyOS — Achievement service tests
Sprint-2.9
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.schemas.achievement import AchievementCheckRequest
from app.services.achievement_service import AchievementService
from app.services.ai.achievement_rule_engine import evaluate_criteria


def test_evaluate_criteria_gte():
    assert evaluate_criteria(
        {"metric": "total_pomodoros", "op": "gte", "value": 10},
        {"total_pomodoros": 10},
        event="session_completed",
    )
    assert not evaluate_criteria(
        {"metric": "total_pomodoros", "op": "gte", "value": 10, "events": ["session_completed"]},
        {"total_pomodoros": 10},
        event="exam_completed",
    )


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Ach",
        last_name="Unit",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_catalog_seeded(db_session: AsyncSession):
    user = await _user(db_session, "ach.catalog@studyos.dev")
    svc = AchievementService(db_session)
    catalog = await svc.list_catalog()
    assert len(catalog) >= 24
    codes = {a.code for a in catalog}
    assert "pomodoro_first" in codes
    assert "streak_7" in codes
    _ = user


@pytest.mark.asyncio
async def test_check_idempotent(db_session: AsyncSession):
    user = await _user(db_session, "ach.check@studyos.dev")
    svc = AchievementService(db_session)
    # Force metrics via context override for pomodoro_first
    first = await svc.check(
        user.id,
        AchievementCheckRequest(
            event="session_completed",
            context={"total_pomodoros": 1, "total_study_minutes": 30, "streak_days": 3},
        ),
    )
    # Context overrides only work for keys in loop - total_pomodoros is set from overview
    # then overridden. Good.
    second = await svc.check(
        user.id,
        AchievementCheckRequest(
            event="session_completed",
            context={"total_pomodoros": 1, "total_study_minutes": 30, "streak_days": 3},
        ),
    )
    unlocked = await svc.list_unlocked(user.id)
    ids = {u.achievement_id for u in unlocked}
    # second run must not duplicate
    assert len(unlocked) == len(ids)
    assert second.newly_unlocked == [] or all(
        u.achievement_id in ids for u in second.newly_unlocked
    )
    _ = first


def _register(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Ach",
        "last_name": "Api",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_achievement_api(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=_register("ach.api@studyos.dev"))
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    catalog = await client.get("/api/v1/achievements", headers=headers)
    assert catalog.status_code == 200, catalog.text
    assert len(catalog.json()["data"]) >= 24

    progress = await client.get("/api/v1/achievements/progress", headers=headers)
    assert progress.status_code == 200

    checked = await client.post(
        "/api/v1/achievements/check",
        headers=headers,
        json={"event": "session_completed"},
    )
    assert checked.status_code == 200, checked.text

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    assert "achievement_summary" in dash.json()["data"]

    ach_id = catalog.json()["data"][0]["id"]
    explained = await client.post(
        f"/api/v1/achievements/{ach_id}/explain",
        headers=headers,
    )
    assert explained.status_code == 200, explained.text
    assert explained.json()["data"]["reason"]
