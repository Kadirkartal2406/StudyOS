"""
StudyOS — Casual Duel & Friends API (Sprint 37)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.casual_duel_service import (
    CasualDuelService,
    DuelInviteRequest,
    DuelMatchRead,
    FriendDTO,
)

router = APIRouter(prefix="/casual-duel", tags=["casual-duel"])


@router.get("/friends", response_model=SuccessResponse[list[FriendDTO]])
async def list_friends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[FriendDTO]]:
    """List available friends for duels."""
    data = await CasualDuelService(db).list_friends(current_user.id)
    return SuccessResponse(data=data)


@router.get("/search-friends", response_model=SuccessResponse[list[FriendDTO]])
async def search_friends(
    q: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[FriendDTO]]:
    """Search registered StudyOS users to add as friends and invite to duels."""
    data = await CasualDuelService(db).search_friends(current_user.id, q)
    return SuccessResponse(data=data)


@router.post("/invite", response_model=SuccessResponse[DuelMatchRead])
async def invite_to_duel(
    body: DuelInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[DuelMatchRead]:
    """Create a casual multiplayer duel match with a friend (isolated from AI profile)."""
    data = await CasualDuelService(db).create_duel(current_user.id, body)
    return SuccessResponse(data=data, message="Düello daveti gönderildi")
