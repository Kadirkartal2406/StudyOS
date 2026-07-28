"""
StudyOS — Revision API
Sprint-2.8 — /api/v1/revisions
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.revision import RevisionItemStatus, RevisionSourceType
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.revision import (
    RevisionCreate,
    RevisionExplainResponse,
    RevisionGenerateRequest,
    RevisionGenerateResponse,
    RevisionHeatmapResponse,
    RevisionItemRead,
    RevisionPostponeRequest,
    RevisionReviewRequest,
    RevisionSkipRequest,
    RevisionStatisticsResponse,
    RevisionUpdate,
)
from app.services.revision_service import RevisionService

router = APIRouter()


@router.get("/today", response_model=SuccessResponse[list[RevisionItemRead]])
async def list_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[RevisionItemRead]]:
    data = await RevisionService(db).today(current_user.id)
    return SuccessResponse(data=data)


@router.get("/week", response_model=SuccessResponse[list[RevisionItemRead]])
async def list_week(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[RevisionItemRead]]:
    data = await RevisionService(db).week(current_user.id)
    return SuccessResponse(data=data)


@router.get("/overdue", response_model=SuccessResponse[list[RevisionItemRead]])
async def list_overdue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[RevisionItemRead]]:
    data = await RevisionService(db).overdue(current_user.id)
    return SuccessResponse(data=data)


@router.get("/statistics", response_model=SuccessResponse[RevisionStatisticsResponse])
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionStatisticsResponse]:
    data = await RevisionService(db).statistics(current_user.id)
    return SuccessResponse(data=data)


@router.get("/heatmap", response_model=SuccessResponse[RevisionHeatmapResponse])
async def get_heatmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionHeatmapResponse]:
    data = await RevisionService(db).heatmap(current_user.id)
    return SuccessResponse(data=data)


@router.post("/generate", response_model=SuccessResponse[RevisionGenerateResponse])
async def generate_revisions(
    body: RevisionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionGenerateResponse]:
    data = await RevisionService(db).generate(current_user.id, body)
    return SuccessResponse(data=data, message=data.message)


@router.get("", response_model=SuccessResponse[list[RevisionItemRead]])
async def list_revisions(
    status_filter: RevisionItemStatus | None = Query(None, alias="status"),
    subject: str | None = None,
    source_type: RevisionSourceType | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[RevisionItemRead]]:
    data = await RevisionService(db).list_items(
        current_user.id,
        status=status_filter,
        subject=subject,
        source_type=source_type,
    )
    return SuccessResponse(data=data)


@router.post("", response_model=SuccessResponse[RevisionItemRead], status_code=status.HTTP_201_CREATED)
async def create_revision(
    body: RevisionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionItemRead]:
    data = await RevisionService(db).create(current_user.id, body)
    return SuccessResponse(data=data, message="Tekrar kartı oluşturuldu")


@router.get("/{item_id}", response_model=SuccessResponse[RevisionItemRead])
async def get_revision(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionItemRead]:
    data = await RevisionService(db).get(item_id, current_user.id)
    return SuccessResponse(data=data)


@router.patch("/{item_id}", response_model=SuccessResponse[RevisionItemRead])
async def update_revision(
    item_id: uuid.UUID,
    body: RevisionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionItemRead]:
    data = await RevisionService(db).update(item_id, current_user.id, body)
    return SuccessResponse(data=data, message="Tekrar kartı güncellendi")


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_revision(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await RevisionService(db).soft_delete(item_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{item_id}/review", response_model=SuccessResponse[RevisionItemRead])
async def review_revision(
    item_id: uuid.UUID,
    body: RevisionReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionItemRead]:
    data = await RevisionService(db).review(item_id, current_user.id, body)
    return SuccessResponse(data=data, message="Tekrar kaydedildi")


@router.post("/{item_id}/skip", response_model=SuccessResponse[RevisionItemRead])
async def skip_revision(
    item_id: uuid.UUID,
    body: RevisionSkipRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionItemRead]:
    data = await RevisionService(db).skip(item_id, current_user.id, body)
    return SuccessResponse(data=data, message="Tekrar ertelendi")


@router.post("/{item_id}/postpone", response_model=SuccessResponse[RevisionItemRead])
async def postpone_revision(
    item_id: uuid.UUID,
    body: RevisionPostponeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionItemRead]:
    data = await RevisionService(db).postpone(item_id, current_user.id, body)
    return SuccessResponse(data=data, message="Tekrar ertelendi")


@router.post("/{item_id}/explain", response_model=SuccessResponse[RevisionExplainResponse])
async def explain_revision(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RevisionExplainResponse]:
    data = await RevisionService(db).explain(item_id, current_user.id)
    return SuccessResponse(data=data)
