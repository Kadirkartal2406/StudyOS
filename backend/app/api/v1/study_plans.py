"""
StudyOS — StudyPlan Endpoint'leri
Bkz. docs/architecture/api-design.md §2.6
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.study_plan import (
    StudyPlanCompleteRequest,
    StudyPlanCreate,
    StudyPlanRead,
    StudyPlanUpdate,
)
from app.schemas.study_resource import (
    StudyResourceCreate,
    StudyResourceListResponse,
    StudyResourceRead,
)
from app.services.study_plan_service import StudyPlanService
from app.services.study_resource_service import StudyResourceService

router = APIRouter()


@router.get("", response_model=SuccessResponse[list[StudyPlanRead]])
async def list_study_plans(
    study_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[StudyPlanRead]]:
    """Kullanıcının çalışma planlarını (opsiyonel tarih filtresiyle) listeler."""
    plans = await StudyPlanService(db).list_plans(current_user.id, study_date)
    return SuccessResponse(data=[StudyPlanRead.model_validate(p) for p in plans])


@router.get("/{plan_id}", response_model=SuccessResponse[StudyPlanRead])
async def get_study_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyPlanRead]:
    """Tekil çalışma planı detayını döner."""
    plan = await StudyPlanService(db).get_plan(plan_id, current_user.id)
    return SuccessResponse(data=StudyPlanRead.model_validate(plan))


@router.post("", response_model=SuccessResponse[StudyPlanRead], status_code=status.HTTP_201_CREATED)
async def create_study_plan(
    body: StudyPlanCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyPlanRead]:
    """
    [DEPRECATED — LOS Hizalama]
    Kullanıcı artık manuel plan oluşturmaz.
    Living Plan sistemi planı otomatik üretir/önerir (POST /living-plan/accept).
    Bu endpoint backward-compatibility için korunmuştur; yeni akışta kullanılmaz.
    """
    response.headers["X-Deprecated"] = "true"
    response.headers["X-Deprecation-Reason"] = "Use Living Plan: POST /living-plan/accept"
    plan = await StudyPlanService(db).create_plan(current_user.id, body)
    return SuccessResponse(data=StudyPlanRead.model_validate(plan), message="Plan oluşturuldu")


@router.put("/{plan_id}", response_model=SuccessResponse[StudyPlanRead])
async def update_study_plan(
    plan_id: uuid.UUID,
    body: StudyPlanUpdate,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyPlanRead]:
    """
    [DEPRECATED — LOS Hizalama]
    Plan düzenlemesi Living Plan adapt döngüsüyle yapılır.
    Bu endpoint backward-compatibility için korunmuştur.
    """
    response.headers["X-Deprecated"] = "true"
    response.headers["X-Deprecation-Reason"] = "Use Living Plan adapt cycle"
    plan = await StudyPlanService(db).update_plan(plan_id, current_user.id, body)
    return SuccessResponse(data=StudyPlanRead.model_validate(plan), message="Plan güncellendi")


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_plan(
    plan_id: uuid.UUID,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    [DEPRECATED — LOS Hizalama]
    Living Plan sistemi planları yönetir; kullanıcı silmez.
    Bu endpoint backward-compatibility için korunmuştur.
    """
    response.headers["X-Deprecated"] = "true"
    response.headers["X-Deprecation-Reason"] = "Living Plan manages plan lifecycle"
    await StudyPlanService(db).delete_plan(plan_id, current_user.id)


@router.patch("/{plan_id}/start", response_model=SuccessResponse[StudyPlanRead])
async def start_study_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyPlanRead]:
    """Planı 'in_progress' durumuna geçirir."""
    plan = await StudyPlanService(db).start_plan(plan_id, current_user.id)
    return SuccessResponse(data=StudyPlanRead.model_validate(plan), message="Plan başlatıldı")


@router.patch("/{plan_id}/complete", response_model=SuccessResponse[StudyPlanRead])
async def complete_study_plan(
    plan_id: uuid.UUID,
    body: StudyPlanCompleteRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyPlanRead]:
    """Planı 'completed' durumuna geçirir; gerçekleşen ilerleme bilgisini kaydeder."""
    plan = await StudyPlanService(db).complete_plan(
        plan_id, current_user.id, body or StudyPlanCompleteRequest()
    )
    return SuccessResponse(data=StudyPlanRead.model_validate(plan), message="Plan tamamlandı")


@router.patch("/{plan_id}/skip", response_model=SuccessResponse[StudyPlanRead])
async def skip_study_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyPlanRead]:
    """Planı 'skipped' durumuna geçirir."""
    plan = await StudyPlanService(db).skip_plan(plan_id, current_user.id)
    return SuccessResponse(data=StudyPlanRead.model_validate(plan), message="Plan atlandı")


@router.get(
    "/{plan_id}/resources",
    response_model=SuccessResponse[StudyResourceListResponse],
)
async def list_plan_resources(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceListResponse]:
    """Plan'a bağlı kaynakları listeler (ownership plan üzerinden)."""
    await StudyPlanService(db).get_plan(plan_id, current_user.id)
    data = await StudyResourceService(db).list_resources(
        current_user.id, study_plan_id=plan_id
    )
    return SuccessResponse(data=data)


@router.post(
    "/{plan_id}/resources",
    response_model=SuccessResponse[StudyResourceRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_plan_resource(
    plan_id: uuid.UUID,
    body: StudyResourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyResourceRead]:
    """Plan'a yeni kaynak ekler."""
    await StudyPlanService(db).get_plan(plan_id, current_user.id)
    payload = body.model_copy(update={"study_plan_id": plan_id})
    data = await StudyResourceService(db).create_resource(current_user.id, payload)
    return SuccessResponse(data=data, message="Kaynak plana eklendi")
