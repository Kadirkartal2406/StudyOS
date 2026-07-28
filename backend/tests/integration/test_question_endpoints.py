"""
StudyOS — QuestionRecord Endpoint Entegrasyon Testleri
"""

from datetime import date

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Soru",
        "last_name": "Kullanıcı",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _payload(**overrides: object) -> dict:
    payload = {
        "subject": "Matematik",
        "topic": "Limit",
        "question_count": 20,
        "correct_count": 14,
        "wrong_count": 4,
        "blank_count": 2,
        "duration_minutes": 35,
        "exam_type": "tyt",
        "difficulty": "medium",
        "source": "book",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_create_list_get_update_delete_question(client: AsyncClient):
    headers = await _auth_headers(client, "q.crud@studyos.dev")

    create = await client.post("/api/v1/questions", json=_payload(), headers=headers)
    assert create.status_code == 201
    data = create.json()["data"]
    record_id = data["id"]
    assert data["net_score"] == "13.00" or float(data["net_score"]) == 13.0

    listed = await client.get("/api/v1/questions", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["pagination"]["total_items"] == 1

    detail = await client.get(f"/api/v1/questions/{record_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["subject"] == "Matematik"

    updated = await client.put(
        f"/api/v1/questions/{record_id}",
        json={
            "question_count": 10,
            "correct_count": 7,
            "wrong_count": 2,
            "blank_count": 1,
        },
        headers=headers,
    )
    assert updated.status_code == 200
    assert float(updated.json()["data"]["net_score"]) == 6.5

    deleted = await client.delete(f"/api/v1/questions/{record_id}", headers=headers)
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_question_statistics_endpoints(client: AsyncClient):
    headers = await _auth_headers(client, "q.stats@studyos.dev")
    await client.post("/api/v1/questions", json=_payload(), headers=headers)

    for path in (
        "/api/v1/questions/statistics",
        "/api/v1/questions/daily",
        "/api/v1/questions/subjects",
        "/api/v1/questions/topics",
        "/api/v1/questions/exams",
    ):
        res = await client.get(path, headers=headers)
        assert res.status_code == 200, path
        assert res.json()["success"] is True

    stats = (await client.get("/api/v1/questions/statistics", headers=headers)).json()["data"]
    assert stats["today_questions"] == 20
    assert stats["total_questions"] == 20


@pytest.mark.asyncio
async def test_filter_by_subject(client: AsyncClient):
    headers = await _auth_headers(client, "q.filter@studyos.dev")
    await client.post("/api/v1/questions", json=_payload(subject="Biyoloji"), headers=headers)
    await client.post("/api/v1/questions", json=_payload(subject="Tarih"), headers=headers)

    res = await client.get("/api/v1/questions", params={"subject": "Biyoloji"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["pagination"]["total_items"] == 1
    assert res.json()["data"][0]["subject"] == "Biyoloji"


@pytest.mark.asyncio
async def test_dashboard_today_questions_from_question_records(client: AsyncClient):
    """B1 — Dashboard bugünkü soru = QuestionRecord toplamı."""
    headers = await _auth_headers(client, "q.dash@studyos.dev")
    await client.post("/api/v1/questions", json=_payload(question_count=15, correct_count=10, wrong_count=3, blank_count=2), headers=headers)

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    assert dash.json()["data"]["today_questions_solved"] == 15


@pytest.mark.asyncio
async def test_create_without_auth_returns_401(client: AsyncClient):
    res = await client.post("/api/v1/questions", json=_payload())
    assert res.status_code == 401
