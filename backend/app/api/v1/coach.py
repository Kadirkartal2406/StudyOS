"""
Sprint 20 — Adaptive AI Coach API
Experience layer — Decision üretmez.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.coach import (
    AssessmentCoachSummary,
    CoachTimelineBundle,
    CoachTodayBundle,
    CoachWeeklyBundle,
)
from app.schemas.common import SuccessResponse
from app.services.coach_service import CoachService

router = APIRouter()


@router.get("/today", response_model=SuccessResponse[CoachTodayBundle])
async def coach_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CoachTodayBundle]:
    data = await CoachService(db).today(current_user.id)
    return SuccessResponse(data=data)


@router.get("/weekly", response_model=SuccessResponse[CoachWeeklyBundle])
async def coach_weekly(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CoachWeeklyBundle]:
    data = await CoachService(db).weekly(current_user.id)
    return SuccessResponse(data=data)


@router.get("/timeline", response_model=SuccessResponse[CoachTimelineBundle])
async def coach_timeline(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CoachTimelineBundle]:
    data = await CoachService(db).timeline(current_user.id)
    return SuccessResponse(data=data)


@router.get(
    "/assessment-summary",
    response_model=SuccessResponse[AssessmentCoachSummary],
)
async def coach_assessment_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentCoachSummary]:
    data = await CoachService(db).assessment_summary(current_user.id)
    return SuccessResponse(data=data)
