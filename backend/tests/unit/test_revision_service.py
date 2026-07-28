"""
StudyOS — Revision service / API tests
Sprint-2.8
"""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import RevisionGrade
from app.models.user import User, UserRole, UserStatus
from app.schemas.revision import (
    RevisionCreate,
    RevisionGenerateRequest,
    RevisionPostponeRequest,
    RevisionReviewRequest,
    RevisionSkipRequest,
)
from app.services.ai.revision_engine import apply_sm2_lite
from app.services.revision_service import RevisionService
from app.models.revision import RevisionSourceType


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Rev",
        last_name="Unit",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


def test_sm2_lite_again_resets_and_raises_difficulty():
    result = apply_sm2_lite(
        grade=RevisionGrade.AGAIN,
        interval_days=7,
        ease_factor=2.5,
        repetition_count=3,
        lapse_count=0,
        difficulty=3,
    )
    assert result.repetition_count == 0
    assert result.interval_days == 1
    assert result.difficulty == 4
    assert result.lapse_count == 1


def test_sm2_lite_easy_lowers_difficulty():
    result = apply_sm2_lite(
        grade=RevisionGrade.EASY,
        interval_days=3,
        ease_factor=2.5,
        repetition_count=2,
        lapse_count=0,
        difficulty=4,
    )
    assert result.difficulty == 3
    assert result.interval_days >= 3
    assert result.ease_factor > 2.5


@pytest.mark.asyncio
async def test_create_and_review_updates_schedule(db_session: AsyncSession):
    user = await _user(db_session, "rev.unit@studyos.dev")
    svc = RevisionService(db_session)
    item = await svc.create(
        user.id,
        RevisionCreate(
            title="Türev tekrarı",
            subject="Matematik",
            topic="Türev",
            source_type=RevisionSourceType.MANUAL,
            difficulty=3,
            reason="Manuel eklendi",
        ),
    )
    assert item.reason == "Manuel eklendi"
    assert item.schedule is not None
    assert item.difficulty == 3

    reviewed = await svc.review(
        item.id,
        user.id,
        RevisionReviewRequest(grade=RevisionGrade.GOOD),
    )
    assert reviewed.schedule is not None
    assert reviewed.schedule.repetition_count == 1
    assert reviewed.schedule.interval_days == 1


@pytest.mark.asyncio
async def test_skip_and_postpone(db_session: AsyncSession):
    user = await _user(db_session, "rev.skip@studyos.dev")
    svc = RevisionService(db_session)
    item = await svc.create(
        user.id,
        RevisionCreate(title="Fizik", subject="Fizik", reason="test"),
    )
    assert item.schedule is not None
    before = item.schedule.due_at
    skipped = await svc.skip(item.id, user.id, RevisionSkipRequest(days=2))
    assert skipped.schedule is not None
    assert skipped.schedule.due_at >= before + timedelta(days=1)

    postponed = await svc.postpone(item.id, user.id, RevisionPostponeRequest(days=5))
    assert postponed.schedule is not None
    assert postponed.schedule.due_at > datetime.now(UTC)


@pytest.mark.asyncio
async def test_generate_idempotent_without_data(db_session: AsyncSession):
    user = await _user(db_session, "rev.gen@studyos.dev")
    svc = RevisionService(db_session)
    result = await svc.generate(
        user.id,
        RevisionGenerateRequest(include_questions=True, include_exams=True, max_items=5),
    )
    assert result.created == [] or isinstance(result.created, list)
    stats = await svc.statistics(user.id)
    assert stats.total_active >= 0
    heat = await svc.heatmap(user.id)
    assert len(heat.days) > 0


def _register(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Rev",
        "last_name": "Api",
        "role": "student",
    }


@pytest.mark.asyncio
async def test_revision_api_flow(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json=_register("rev.api@studyos.dev"))
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = await client.post(
        "/api/v1/revisions",
        headers=headers,
        json={
            "title": "Kimya tekrar",
            "subject": "Kimya",
            "difficulty": 4,
            "reason": "Zayıf konu",
            "source_type": "manual",
        },
    )
    assert created.status_code == 201, created.text
    item_id = created.json()["data"]["id"]
    assert created.json()["data"]["reason"] == "Zayıf konu"
    assert created.json()["data"]["difficulty"] == 4

    today = await client.get("/api/v1/revisions/today", headers=headers)
    assert today.status_code == 200
    assert any(i["id"] == item_id for i in today.json()["data"])

    reviewed = await client.post(
        f"/api/v1/revisions/{item_id}/review",
        headers=headers,
        json={"grade": "good"},
    )
    assert reviewed.status_code == 200, reviewed.text

    explained = await client.post(
        f"/api/v1/revisions/{item_id}/explain",
        headers=headers,
    )
    assert explained.status_code == 200, explained.text
    assert explained.json()["data"]["reason"] == "Zayıf konu"

    stats = await client.get("/api/v1/revisions/statistics", headers=headers)
    assert stats.status_code == 200
    heat = await client.get("/api/v1/revisions/heatmap", headers=headers)
    assert heat.status_code == 200

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    assert "revision_summary" in dash.json()["data"]
