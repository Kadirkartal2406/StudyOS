"""
StudyOS — Study Resources Endpoint'leri
Sprint-2.5 — /api/v1/resources
"""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.study_resource import ResourceStatus, ResourceType
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.study_resource import (
    ResourceStatistics,
    StudyResourceCreate,
    StudyResourceListResponse,
    StudyResourceRead,
    StudyResourceUpdate,
)
from app.services.study_resource_service import StudyResourceService

router = APIRouter()

# Yüklenen dosyalar main.py'de /uploads altında statik olarak sunulur.
UPLOADS_DIR = Path(__file__).resolve().parents[4] / "data" / "uploads" / "resources"


@router.get("/statistics", response_model=SuccessResponse[ResourceStatistics])
async def resource_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ResourceStatistics]:
    data = await StudyResourceService(db).get_statistics(current_user.id)
    return SuccessResponse(data=data)


@router.get("", response_model=SuccessResponse[StudyResourceListResponse])
async def list_resources(
    study_plan_id: uuid.UUID | None = None,
    subject_code: str | None = Query(default=None),
    topic_code: str | None = Query(default=None),
    status_filter: ResourceStatus | None = Query(default=None, alias="status"),
    resource_type: ResourceType | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceListResponse]:
    data = await StudyResourceService(db).list_resources(
        current_user.id,
        study_plan_id=study_plan_id,
        subject_code=subject_code,
        topic_code=topic_code,
        status=status_filter,
        resource_type=resource_type,
    )
    return SuccessResponse(data=data)


@router.post("", response_model=SuccessResponse[StudyResourceRead], status_code=status.HTTP_201_CREATED)
async def create_resource(
    body: StudyResourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceRead]:
    data = await StudyResourceService(db).create_resource(current_user.id, body)
    return SuccessResponse(data=data, message="Kaynak oluşturuldu")


@router.post("/upload", response_model=SuccessResponse[dict])
async def upload_resource_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[dict]:
    """Cihazdan seçilen PDF/ses/video/doküman dosyasını sunucuya yükler."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    extension = os.path.splitext(file.filename or "")[1]
    stored_name = f"{uuid.uuid4()}{extension}"

    with open(UPLOADS_DIR / stored_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return SuccessResponse(
        data={"url": f"/uploads/resources/{stored_name}"},
        message="Dosya yüklendi",
    )


@router.get("/{resource_id}", response_model=SuccessResponse[StudyResourceRead])
async def get_resource(
    resource_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceRead]:
    data = await StudyResourceService(db).get_resource(resource_id, current_user.id)
    return SuccessResponse(data=data)


@router.patch("/{resource_id}", response_model=SuccessResponse[StudyResourceRead])
async def update_resource(
    resource_id: uuid.UUID,
    body: StudyResourceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceRead]:
    data = await StudyResourceService(db).update_resource(resource_id, current_user.id, body)
    return SuccessResponse(data=data, message="Kaynak güncellendi")


@router.delete("/{resource_id}", response_model=SuccessResponse[dict])
async def delete_resource(
    resource_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    await StudyResourceService(db).delete_resource(resource_id, current_user.id)
    return SuccessResponse(data={}, message="Kaynak silindi")


@router.post("/{resource_id}/open", response_model=SuccessResponse[StudyResourceRead])
async def open_resource(
    resource_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceRead]:
    """E1 — last_opened_at güncelle; not_started → in_progress."""
    data = await StudyResourceService(db).mark_opened(resource_id, current_user.id)
    return SuccessResponse(data=data, message="Kaynak açıldı")
