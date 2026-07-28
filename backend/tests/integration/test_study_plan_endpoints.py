"""
StudyOS — StudyPlan Endpoint Entegrasyon Testleri
"""

import uuid
from datetime import date

import pytest
from httpx import AsyncClient

TODAY = str(date.today())


def _register_body(email: str) -> dict:
    return {
        "email": email,
        "password": "GucluSifre123!",
        "first_name": "Plan",
        "last_name": "Kullanıcı",
        "role": "student",
    }


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    res = await client.post("/api/v1/auth/register", json=_register_body(email))
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _plan_payload(**overrides: object) -> dict:
    payload = {
        "title": "Matematik Çalışması",
        "subject": "Matematik",
        "topic": "Türev",
        "target_question_count": 20,
        "estimated_minutes": 60,
        "study_date": TODAY,
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_create_study_plan_returns_201(client: AsyncClient):
    headers = await _auth_headers(client, "plan.create@studyos.dev")

    response = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "Matematik Çalışması"
    assert data["status"] == "planned"
    assert data["order_index"] == 0


@pytest.mark.asyncio
async def test_create_study_plan_without_auth_returns_401(client: AsyncClient):
    response = await client.post("/api/v1/study-plans", json=_plan_payload())

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_study_plan_rejects_empty_title(client: AsyncClient):
    headers = await _auth_headers(client, "plan.empty-title@studyos.dev")

    response = await client.post(
        "/api/v1/study-plans", json=_plan_payload(title=""), headers=headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_study_plan_rejects_zero_minutes(client: AsyncClient):
    headers = await _auth_headers(client, "plan.zero-minutes@studyos.dev")

    response = await client.post(
        "/api/v1/study-plans", json=_plan_payload(estimated_minutes=0), headers=headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_study_plan_rejects_end_before_start(client: AsyncClient):
    headers = await _auth_headers(client, "plan.bad-range@studyos.dev")

    response = await client.post(
        "/api/v1/study-plans",
        json=_plan_payload(planned_start_time="10:00:00", planned_end_time="09:00:00"),
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_study_plan_rejects_time_conflict(client: AsyncClient):
    headers = await _auth_headers(client, "plan.conflict@studyos.dev")
    await client.post(
        "/api/v1/study-plans",
        json=_plan_payload(planned_start_time="09:00:00", planned_end_time="10:00:00"),
        headers=headers,
    )

    response = await client.post(
        "/api/v1/study-plans",
        json=_plan_payload(
            title="Çakışan Plan",
            planned_start_time="09:30:00",
            planned_end_time="10:30:00",
        ),
        headers=headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_study_plans_filters_by_date_and_is_scoped_to_owner(client: AsyncClient):
    headers_a = await _auth_headers(client, "plan.owner-a@studyos.dev")
    headers_b = await _auth_headers(client, "plan.owner-b@studyos.dev")
    await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers_a)
    await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers_b)

    response = await client.get(
        "/api/v1/study-plans", params={"study_date": TODAY}, headers=headers_a
    )

    assert response.status_code == 200
    plans = response.json()["data"]
    assert len(plans) == 1


@pytest.mark.asyncio
async def test_get_study_plan_by_id(client: AsyncClient):
    headers = await _auth_headers(client, "plan.get@studyos.dev")
    create_res = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers)
    plan_id = create_res.json()["data"]["id"]

    response = await client.get(f"/api/v1/study-plans/{plan_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["id"] == plan_id


@pytest.mark.asyncio
async def test_get_other_users_plan_returns_404(client: AsyncClient):
    headers_a = await _auth_headers(client, "plan.owner-c@studyos.dev")
    headers_b = await _auth_headers(client, "plan.owner-d@studyos.dev")
    create_res = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers_a)
    plan_id = create_res.json()["data"]["id"]

    response = await client.get(f"/api/v1/study-plans/{plan_id}", headers=headers_b)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_unknown_plan_returns_404(client: AsyncClient):
    headers = await _auth_headers(client, "plan.unknown@studyos.dev")

    response = await client.get(f"/api/v1/study-plans/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_study_plan(client: AsyncClient):
    headers = await _auth_headers(client, "plan.update@studyos.dev")
    create_res = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers)
    plan_id = create_res.json()["data"]["id"]

    response = await client.put(
        f"/api/v1/study-plans/{plan_id}",
        json=_plan_payload(title="Güncellenmiş Plan", estimated_minutes=90),
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Güncellenmiş Plan"
    assert data["estimated_minutes"] == 90


@pytest.mark.asyncio
async def test_delete_study_plan_returns_204_and_soft_deletes(client: AsyncClient):
    headers = await _auth_headers(client, "plan.delete@studyos.dev")
    create_res = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers)
    plan_id = create_res.json()["data"]["id"]

    delete_response = await client.delete(f"/api/v1/study-plans/{plan_id}", headers=headers)
    get_response = await client.get(f"/api/v1/study-plans/{plan_id}", headers=headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_start_complete_and_skip_lifecycle(client: AsyncClient):
    headers = await _auth_headers(client, "plan.lifecycle@studyos.dev")
    create_res = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers)
    plan_id = create_res.json()["data"]["id"]

    start_res = await client.patch(f"/api/v1/study-plans/{plan_id}/start", headers=headers)
    assert start_res.json()["data"]["status"] == "in_progress"

    complete_res = await client.patch(
        f"/api/v1/study-plans/{plan_id}/complete",
        json={"completed_question_count": 10, "completed_minutes": 30},
        headers=headers,
    )
    assert complete_res.json()["data"]["status"] == "completed"
    assert complete_res.json()["data"]["completed_minutes"] == 30

    skip_res = await client.patch(f"/api/v1/study-plans/{plan_id}/skip", headers=headers)
    assert skip_res.status_code == 409


@pytest.mark.asyncio
async def test_skip_plan_endpoint(client: AsyncClient):
    headers = await _auth_headers(client, "plan.skip@studyos.dev")
    create_res = await client.post("/api/v1/study-plans", json=_plan_payload(), headers=headers)
    plan_id = create_res.json()["data"]["id"]

    response = await client.patch(f"/api/v1/study-plans/{plan_id}/skip", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "skipped"
