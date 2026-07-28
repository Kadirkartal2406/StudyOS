"""Sprint 21 RC — Analytics + Beta Feedback API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_user_optional
from app.database.base import get_db
from app.models.user import User
from app.schemas.beta_ops import (
    AnalyticsBatchRequest,
    AnalyticsBatchResult,
    AnalyticsDashboardRead,
    AnalyticsTrackRequest,
    AnalyticsTrackResult,
    BetaFeedbackCreate,
    BetaFeedbackRead,
)
from app.schemas.common import SuccessResponse
from app.schemas.qie_eval import QieEvalCreate, QieEvalQueueItem, QieEvalRead
from app.services.beta_ops_service import AnalyticsService, BetaFeedbackService
from app.services.qie_eval_service import QieEvalService

router = APIRouter()


@router.post("/analytics/track", response_model=SuccessResponse[AnalyticsTrackResult])
async def track_event(
    body: AnalyticsTrackRequest,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AnalyticsTrackResult]:
    data = await AnalyticsService(db).track(
        body, user_id=current_user.id if current_user else None
    )
    await db.commit()
    return SuccessResponse(data=data)


@router.post("/analytics/batch", response_model=SuccessResponse[AnalyticsBatchResult])
async def track_batch(
    body: AnalyticsBatchRequest,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AnalyticsBatchResult]:
    data = await AnalyticsService(db).track_batch(
        body, user_id=current_user.id if current_user else None
    )
    await db.commit()
    return SuccessResponse(data=data)


@router.get(
    "/analytics/dashboard",
    response_model=SuccessResponse[AnalyticsDashboardRead],
)
async def analytics_dashboard(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AnalyticsDashboardRead]:
    """RC2 M22.4 — mevcut event aggregation (yeni event yok)."""
    _ = current_user  # auth required
    data = await AnalyticsService(db).dashboard(days=days)
    return SuccessResponse(data=data)


@router.post("/feedback", response_model=SuccessResponse[BetaFeedbackRead])
async def submit_feedback(
    body: BetaFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[BetaFeedbackRead]:
    data = await BetaFeedbackService(db).create(current_user.id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Geri bildiriminiz alındı")


@router.get("/qie-eval/queue", response_model=SuccessResponse[list[QieEvalQueueItem]])
async def qie_eval_queue(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[QieEvalQueueItem]]:
    _ = current_user
    data = await QieEvalService(db).queue(limit=limit)
    return SuccessResponse(data=data)


@router.post("/qie-eval", response_model=SuccessResponse[QieEvalRead])
async def qie_eval_submit(
    body: QieEvalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QieEvalRead]:
    data = await QieEvalService(db).create(current_user.id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Değerlendirme kaydedildi")
