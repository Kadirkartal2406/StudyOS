"""Admin API — system_admin only."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_system_admin
from app.database.base import get_db
from app.models.user import User
from app.schemas.admin import AdminOverview, AdminUserListItem, AdminUserUpdate
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/overview", response_model=SuccessResponse[AdminOverview])
async def admin_overview(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AdminOverview]:
    data = await AdminService(db).overview()
    return SuccessResponse(data=data)


@router.get("/users", response_model=PaginatedResponse[AdminUserListItem])
async def admin_list_users(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> PaginatedResponse[AdminUserListItem]:
    items, total = await AdminService(db).list_users(q=q, page=page, page_size=page_size)
    meta = AdminService.pagination_meta(page, page_size, total)
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(**meta),
    )


@router.get("/users/{user_id}", response_model=SuccessResponse[AdminUserListItem])
async def admin_get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AdminUserListItem]:
    data = await AdminService(db).get_user(user_id)
    return SuccessResponse(data=data)


@router.patch("/users/{user_id}", response_model=SuccessResponse[AdminUserListItem])
async def admin_update_user(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AdminUserListItem]:
    data = await AdminService(db).update_user(user_id, body)
    return SuccessResponse(data=data, message="Kullanıcı güncellendi")


@router.delete("/users/{user_id}", response_model=SuccessResponse[dict])
async def admin_delete_user(
    user_id: uuid.UUID,
    hard: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    if admin.id == user_id and hard:
        from app.core.exceptions import ValidationError

        raise ValidationError("Kendi hesabınızı kalıcı silemezsiniz")
    await AdminService(db).delete_user(user_id, hard=hard)
    return SuccessResponse(
        data={},
        message="Kullanıcı kalıcı silindi" if hard else "Kullanıcı pasife alındı",
    )


@router.get("/users/{user_id}/export")
async def admin_export_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> Response:
    payload = await AdminService(db).export_user_data(user_id)
    raw = AdminService.export_json_bytes(payload)
    filename = f"studyos-user-{user_id}.json"
    return Response(
        content=raw,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/questions")
async def admin_list_questions(
    source: str = Query(default="all"),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=40, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
):
    items, total = await AdminService(db).list_questions(
        source=source, q=q, page=page, page_size=page_size
    )
    meta = AdminService.pagination_meta(page, page_size, total)
    return {
        "success": True,
        "data": [i.model_dump(mode="json") for i in items],
        "pagination": meta,
        "message": "OK",
    }
