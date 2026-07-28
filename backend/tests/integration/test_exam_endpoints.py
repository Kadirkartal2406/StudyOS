"""
StudyOS — Exam endpoints integration tests
"""

import pytest
from httpx import AsyncClient


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Exam",
        "last_name": "Test",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_exam_crud_stats_trends(client: AsyncClient):
    headers = await _auth_headers(client, "exam.api@studyos.dev")

    created = await client.post(
        "/api/v1/exams",
        headers=headers,
        json={
            "title": "AYT Deneme",
            "exam_type": "ayt",
            "exam_date": "2026-07-12",
            "duration_minutes": 180,
            "notes": "İlk deneme",
            "results": [
                {
                    "subject": "Matematik",
                    "correct_count": 25,
                    "wrong_count": 10,
                    "blank_count": 5,
                    "question_count": 40,
                    "duration_minutes": 90,
                },
                {
                    "subject": "Fizik",
                    "correct_count": 10,
                    "wrong_count": 3,
                    "blank_count": 1,
                    "question_count": 14,
                    "duration_minutes": 40,
                },
            ],
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()["data"]
    assert "first_exam" in body["milestones"]
    exam_id = body["exam"]["id"]
    assert body["exam"]["result_count"] == 2

    listed = await client.get("/api/v1/exams", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) >= 1

    detail = await client.get(f"/api/v1/exams/{exam_id}", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["data"]["results"]) == 2

    patched = await client.patch(
        f"/api/v1/exams/{exam_id}",
        headers=headers,
        json={"title": "AYT Deneme Güncel"},
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["title"] == "AYT Deneme Güncel"

    replaced = await client.put(
        f"/api/v1/exams/{exam_id}/results",
        headers=headers,
        json={
            "results": [
                {
                    "subject": "Kimya",
                    "correct_count": 8,
                    "wrong_count": 2,
                    "blank_count": 0,
                    "question_count": 10,
                    "duration_minutes": 30,
                }
            ]
        },
    )
    assert replaced.status_code == 200
    assert replaced.json()["data"]["result_count"] == 1

    stats = await client.get("/api/v1/exams/statistics", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["data"]["total_exams"] >= 1

    trends = await client.get("/api/v1/exams/trends", headers=headers)
    assert trends.status_code == 200
    assert "net_over_time" in trends.json()["data"]

    dash = await client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    assert dash.json()["data"]["last_exam_title"] is not None
    assert dash.json()["data"]["today_ai_exam_summary"] is not None

    deleted = await client.delete(f"/api/v1/exams/{exam_id}", headers=headers)
    assert deleted.status_code == 200
