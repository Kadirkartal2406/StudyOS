import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.auth import get_current_user
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceRead,
    AnnotationLayerCreate, AnnotationLayerRead
)
from app.services.workspace_service import WorkspaceService
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[WorkspaceRead])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    return await service.get_user_workspaces(current_user.id)


@router.post("/", response_model=WorkspaceRead)
async def create_workspace(
    dto: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    ws = await service.create_workspace(current_user.id, dto)
    await db.commit()
    return ws


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: uuid.UUID,
    dto: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    ws = await service.update_workspace(workspace_id, current_user.id, dto)
    await db.commit()
    return ws


@router.get("/{workspace_id}/annotations", response_model=List[AnnotationLayerRead])
async def get_annotations(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    return await service.get_annotation_layers(workspace_id, current_user.id)


@router.put("/{workspace_id}/annotations", response_model=AnnotationLayerRead)
async def upsert_annotation(
    workspace_id: uuid.UUID,
    dto: AnnotationLayerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    layer = await service.upsert_annotation_layer(workspace_id, current_user.id, dto)
    await db.commit()
    return layer
