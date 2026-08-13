"""Topic Test Catalog API — Gemini-free user path + admin release."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_system_admin
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.topic_test import (
    TopicTestAttemptRead,
    TopicTestCatalogRead,
    TopicTestReleaseRequest,
    TopicTestReleaseResult,
    TopicTestSubmitRequest,
    TopicTestSubmitResult,
)
from app.services.topic_test_catalog_service import TopicTestCatalogService
from app.services.topic_test_release_service import TopicTestReleaseService

router = APIRouter()


@router.get(
    "/catalog",
    response_model=SuccessResponse[TopicTestCatalogRead],
)
async def list_topic_test_catalog(
    exam: str = Query(...),
    subject_code: str = Query(...),
    topic_code: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicTestCatalogRead]:
    data = await TopicTestCatalogService(db).list_catalog(
        current_user.id,
        exam=exam,
        subject_code=subject_code,
        topic_code=topic_code,
    )
    return SuccessResponse(data=data)


@router.post(
    "/tests/{test_id}/start",
    response_model=SuccessResponse[TopicTestAttemptRead],
)
async def start_topic_test(
    test_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicTestAttemptRead]:
    """Start/resume published catalog test — DB only, no Gemini."""
    data = await TopicTestCatalogService(db).start_attempt(current_user.id, test_id)
    await db.commit()
    return SuccessResponse(data=data, message="Test başlatıldı")


@router.get(
    "/attempts/{attempt_id}",
    response_model=SuccessResponse[TopicTestAttemptRead | TopicTestSubmitResult],
)
async def get_topic_test_attempt(
    attempt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicTestAttemptRead | TopicTestSubmitResult]:
    data = await TopicTestCatalogService(db).get_attempt(
        current_user.id, attempt_id, include_answers=True
    )
    return SuccessResponse(data=data)


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=SuccessResponse[TopicTestSubmitResult],
)
async def submit_topic_test(
    attempt_id: uuid.UUID,
    body: TopicTestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicTestSubmitResult]:
    data = await TopicTestCatalogService(db).submit(current_user.id, attempt_id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Test gönderildi")


@router.post(
    "/admin/release",
    response_model=SuccessResponse[TopicTestReleaseResult],
)
async def admin_release_topic_week(
    body: TopicTestReleaseRequest,
    _: User = Depends(require_system_admin),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicTestReleaseResult]:
    """Idempotent weekly release for one topic (3 difficulties)."""
    data = await TopicTestReleaseService(db).release_topic_week(body)
    await db.commit()
    return SuccessResponse(data=data)
