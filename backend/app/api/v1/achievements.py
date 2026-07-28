"""
StudyOS — Achievement API
Sprint-2.9 — /api/v1/achievements
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.achievement import (
    AchievementCheckRequest,
    AchievementCheckResponse,
    AchievementExplainResponse,
    AchievementProgressRead,
    AchievementRead,
    UserAchievementRead,
)
from app.schemas.common import SuccessResponse
from app.services.achievement_service import AchievementService

router = APIRouter()


@router.get("", response_model=SuccessResponse[list[AchievementRead]])
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[AchievementRead]]:
    data = await AchievementService(db).list_catalog()
    return SuccessResponse(data=data)


@router.get("/unlocked", response_model=SuccessResponse[list[UserAchievementRead]])
async def list_unlocked(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[UserAchievementRead]]:
    data = await AchievementService(db).list_unlocked(current_user.id)
    return SuccessResponse(data=data)


@router.get("/progress", response_model=SuccessResponse[list[AchievementProgressRead]])
async def list_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[AchievementProgressRead]]:
    data = await AchievementService(db).list_progress(current_user.id)
    return SuccessResponse(data=data)


@router.post("/check", response_model=SuccessResponse[AchievementCheckResponse])
async def check_achievements(
    body: AchievementCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AchievementCheckResponse]:
    data = await AchievementService(db).check(current_user.id, body)
    return SuccessResponse(data=data, message=f"{len(data.newly_unlocked)} yeni rozet")


@router.get("/{achievement_id}")
async def get_achievement(
    achievement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict[str, Any]]:
    data = await AchievementService(db).get(achievement_id, current_user.id)
    return SuccessResponse(data=data)


@router.post(
    "/{achievement_id}/explain",
    response_model=SuccessResponse[AchievementExplainResponse],
)
async def explain_achievement(
    achievement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AchievementExplainResponse]:
    data = await AchievementService(db).explain(achievement_id, current_user.id)
    return SuccessResponse(data=data)
