"""
StudyOS — Planner API
Sprint-2.7 — /api/v1/planner
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.planner import (
    PlannerAcceptRequest,
    PlannerAcceptResponse,
    PlannerDraftRead,
    PlannerExplainResponse,
    PlannerGenerateRequest,
    PlannerSuggestionListResponse,
)
from app.services.planner_service import PlannerService

router = APIRouter()


@router.get("/suggestions", response_model=SuccessResponse[PlannerSuggestionListResponse])
async def list_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerSuggestionListResponse]:
    """Sprint-9: list pending Living Plan suggestions for the current user."""
    items = await PlannerService(db).list_pending_suggestions(current_user.id)
    return SuccessResponse(data=PlannerSuggestionListResponse(suggestions=items, count=len(items)))


@router.post(
    "/suggestions/{draft_id}/accept",
    response_model=SuccessResponse[PlannerAcceptResponse],
)
async def accept_suggestion(
    draft_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerAcceptResponse]:
    """Sprint-9: accept a pending Living Plan suggestion."""
    data = await PlannerService(db).accept_suggestion(current_user.id, draft_id)
    return SuccessResponse(data=data, message="Öneri kabul edildi")


@router.post(
    "/suggestions/{draft_id}/reject",
    response_model=SuccessResponse[PlannerDraftRead],
)
async def reject_suggestion(
    draft_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerDraftRead]:
    """Sprint-9: reject a pending Living Plan suggestion."""
    data = await PlannerService(db).reject_suggestion(current_user.id, draft_id)
    return SuccessResponse(data=data, message="Öneri reddedildi")


@router.post("/generate", response_model=SuccessResponse[PlannerDraftRead])
async def generate_plan(
    body: PlannerGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerDraftRead]:
    data = await PlannerService(db).generate(current_user.id, body)
    return SuccessResponse(data=data, message="Plan taslağı oluşturuldu")


@router.get("/{draft_id}", response_model=SuccessResponse[PlannerDraftRead])
async def get_draft(
    draft_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerDraftRead]:
    data = await PlannerService(db).get_draft(draft_id, current_user.id)
    return SuccessResponse(data=data)


@router.post("/{draft_id}/accept", response_model=SuccessResponse[PlannerAcceptResponse])
async def accept_draft(
    draft_id: uuid.UUID,
    body: PlannerAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerAcceptResponse]:
    data = await PlannerService(db).accept(draft_id, current_user.id, body)
    return SuccessResponse(data=data, message="Plan kabul edildi")


@router.post("/{draft_id}/explain", response_model=SuccessResponse[PlannerExplainResponse])
async def explain_draft(
    draft_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PlannerExplainResponse]:
    data = await PlannerService(db).explain(draft_id, current_user.id)
    return SuccessResponse(data=data)
