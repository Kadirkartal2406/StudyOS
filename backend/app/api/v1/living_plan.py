"""
StudyOS — Living Plan API (LOS Hizalama)
LOS § 9 — observe → suggest → accept → adapt

Kullanıcı:
  POST /living-plan/accept  → PENDING draft'ı kabul eder
  POST /living-plan/reject  → PENDING draft'ı reddeder (cooldown + Memory)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.living_plan_service import LivingPlanService

router = APIRouter(prefix="/living-plan", tags=["living-plan"])


class LivingPlanActionRequest(BaseModel):
    draft_id: str | None = None  # None → aktif PENDING draft'ı bul


class LivingPlanActionResponse(BaseModel):
    action: str       # accepted | rejected | no_pending
    draft_id: str | None = None
    reason: str


@router.post("/accept", response_model=SuccessResponse[LivingPlanActionResponse])
async def accept_living_plan(
    body: LivingPlanActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LivingPlanActionResponse]:
    """
    LOS § 9.1 — Suggest → Accept.
    Kullanıcı Living Plan önerisini kabul eder.
    PENDING draft → ACCEPTED; plan blokları StudyPlan'a dönüşür.
    """
    result = await LivingPlanService(db).accept_suggestion(
        current_user.id,
        draft_id=uuid.UUID(body.draft_id) if body.draft_id else None,
    )
    return SuccessResponse(data=LivingPlanActionResponse(**result))


@router.post("/reject", response_model=SuccessResponse[LivingPlanActionResponse])
async def reject_living_plan(
    body: LivingPlanActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LivingPlanActionResponse]:
    """
    LOS § 9.4 — Reddetmek öğrenmektir.
    PENDING draft → REJECTED; cooldown başlar; Memory'ye yazılır.
    Plan değişmez; mevcut plan sözleşmesi devam eder.
    """
    result = await LivingPlanService(db).reject_suggestion(
        current_user.id,
        draft_id=uuid.UUID(body.draft_id) if body.draft_id else None,
    )
    return SuccessResponse(data=LivingPlanActionResponse(**result))
