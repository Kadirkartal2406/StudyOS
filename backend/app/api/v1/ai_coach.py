"""
StudyOS — AI Coach API (Sprint 33)
Daily personalized coaching analysis, target progress, and question recommendations.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.ai_coach_service import AICoachDailyRead, AICoachService

router = APIRouter(prefix="/ai-coach", tags=["ai-coach"])


@router.get("/daily", response_model=SuccessResponse[AICoachDailyRead])
async def get_daily_coaching(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AICoachDailyRead]:
    """Get personalized daily AI coaching analysis and recommendations."""
    data = await AICoachService(db).get_daily_coaching(current_user.id)
    return SuccessResponse(data=data)
