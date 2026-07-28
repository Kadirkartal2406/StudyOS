"""
StudyOS — Goal Endpoint'leri
Sprint-2.1 — /api/v1/goals
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.goal import (
    GoalCreate,
    GoalExplainResponse,
    GoalListResponse,
    GoalProgressResponse,
    GoalRead,
    GoalUpdate,
)
from app.services.goal_service import GoalService

router = APIRouter()


@router.get("/active", response_model=SuccessResponse[GoalListResponse])
async def list_active_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalListResponse]:
    service = GoalService(db)
    goals = await service.list_active(current_user.id)
    return SuccessResponse(data=service.as_list_response(goals))


@router.get("/completed", response_model=SuccessResponse[GoalListResponse])
async def list_completed_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalListResponse]:
    service = GoalService(db)
    goals = await service.list_completed(current_user.id)
    return SuccessResponse(data=service.as_list_response(goals))


@router.get("/progress", response_model=SuccessResponse[GoalProgressResponse])
async def get_goals_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalProgressResponse]:
    data = await GoalService(db).get_progress(current_user.id)
    return SuccessResponse(data=data)


@router.get("/weekly", response_model=SuccessResponse[GoalListResponse])
async def list_weekly_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalListResponse]:
    service = GoalService(db)
    goals = await service.list_weekly(current_user.id)
    return SuccessResponse(data=service.as_list_response(goals))


@router.get("/monthly", response_model=SuccessResponse[GoalListResponse])
async def list_monthly_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalListResponse]:
    service = GoalService(db)
    goals = await service.list_monthly(current_user.id)
    return SuccessResponse(data=service.as_list_response(goals))


@router.get("", response_model=SuccessResponse[GoalListResponse])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalListResponse]:
    service = GoalService(db)
    goals = await service.list_all(current_user.id)
    return SuccessResponse(data=service.as_list_response(goals))


@router.post("", response_model=SuccessResponse[GoalRead], status_code=status.HTTP_201_CREATED)
async def create_goal(
    body: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalRead]:
    service = GoalService(db)
    goal = await service.create(current_user.id, body)
    return SuccessResponse(data=service.to_read(goal), message="Hedef oluşturuldu")


@router.get("/{goal_id}", response_model=SuccessResponse[GoalRead])
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalRead]:
    service = GoalService(db)
    goal = await service.get(goal_id, current_user.id)
    return SuccessResponse(data=service.to_read(goal))


@router.patch("/{goal_id}", response_model=SuccessResponse[GoalRead])
async def update_goal(
    goal_id: uuid.UUID,
    body: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalRead]:
    service = GoalService(db)
    goal = await service.update(goal_id, current_user.id, body)
    return SuccessResponse(data=service.to_read(goal), message="Hedef güncellendi")


@router.delete("/{goal_id}", response_model=SuccessResponse[dict])
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    await GoalService(db).delete(goal_id, current_user.id)
    return SuccessResponse(data={}, message="Hedef silindi")


@router.post("/{goal_id}/explain", response_model=SuccessResponse[GoalExplainResponse])
async def explain_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GoalExplainResponse]:
    """LLM yalnızca açıklar — hedef üretmez."""
    data = await GoalService(db).explain(goal_id, current_user.id)
    return SuccessResponse(data=data)