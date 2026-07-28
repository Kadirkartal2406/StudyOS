"""
StudyOS — Dashboard Endpoint'leri
Bkz. docs/architecture/api-design.md §2.16
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("", response_model=SuccessResponse[DashboardResponse])
async def get_dashboard(
    exam_type: str | None = Query(
        default=None,
        description="Sprint-3.1.A — Active bağlamı; verilmezse Active/Primary",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[DashboardResponse]:
    """Giriş yapan kullanıcı için ana ekran (Dashboard) özet verisini döner."""
    data = await DashboardService(db).get_dashboard(current_user, exam_type=exam_type)
    return SuccessResponse(data=data)
