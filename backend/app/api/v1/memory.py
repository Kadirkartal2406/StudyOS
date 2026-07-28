"""
StudyOS — Memory Endpoint'leri
Sprint-2.3 — /api/v1/memory
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.memory import (
    MemoryCreate,
    MemoryExportResponse,
    MemoryListResponse,
    MemoryRead,
    MemorySearchRequest,
    MemorySettingsRead,
    MemorySettingsUpdate,
    MemoryUpdate,
)
from app.services.memory_service import MemoryService

router = APIRouter()


@router.get("", response_model=SuccessResponse[MemoryListResponse])
async def list_memories(
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemoryListResponse]:
    data = await MemoryService(db).list_memories(current_user.id, active_only=active_only)
    return SuccessResponse(data=data)


@router.post("", response_model=SuccessResponse[MemoryRead], status_code=status.HTTP_201_CREATED)
async def create_memory(
    body: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemoryRead]:
    data = await MemoryService(db).create_memory(current_user.id, body)
    return SuccessResponse(data=data, message="Bellek oluşturuldu")


@router.post("/search", response_model=SuccessResponse[MemoryListResponse])
async def search_memories(
    body: MemorySearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemoryListResponse]:
    data = await MemoryService(db).search(current_user.id, body)
    return SuccessResponse(data=data)


@router.get("/settings", response_model=SuccessResponse[MemorySettingsRead])
async def get_memory_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemorySettingsRead]:
    data = await MemoryService(db).get_settings(current_user.id)
    return SuccessResponse(data=data)


@router.patch("/settings", response_model=SuccessResponse[MemorySettingsRead])
async def update_memory_settings(
    body: MemorySettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemorySettingsRead]:
    data = await MemoryService(db).update_settings(current_user.id, body)
    return SuccessResponse(data=data, message="Bellek ayarları güncellendi")


@router.get("/export", response_model=SuccessResponse[MemoryExportResponse])
async def export_memories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemoryExportResponse]:
    data = await MemoryService(db).export_memories(current_user.id)
    return SuccessResponse(data=data)


@router.delete("/clear", response_model=SuccessResponse[dict])
async def clear_memories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    deleted = await MemoryService(db).clear_memories(current_user.id)
    return SuccessResponse(data={"deleted": deleted}, message="Tüm bellekler silindi")


@router.get("/{memory_id}", response_model=SuccessResponse[MemoryRead])
async def get_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemoryRead]:
    data = await MemoryService(db).get_memory(memory_id, current_user.id)
    return SuccessResponse(data=data)


@router.patch("/{memory_id}", response_model=SuccessResponse[MemoryRead])
async def update_memory(
    memory_id: uuid.UUID,
    body: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[MemoryRead]:
    data = await MemoryService(db).update_memory(memory_id, current_user.id, body)
    return SuccessResponse(data=data, message="Bellek güncellendi")


@router.delete("/{memory_id}", response_model=SuccessResponse[dict])
async def delete_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    await MemoryService(db).delete_memory(memory_id, current_user.id)
    return SuccessResponse(data={}, message="Bellek silindi")
