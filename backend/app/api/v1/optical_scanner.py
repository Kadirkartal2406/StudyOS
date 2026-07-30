"""
StudyOS — Optical Form Camera Scanner API (Sprint 35)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.optical_scanner_service import (
    OpticalScanRequest,
    OpticalScanResponse,
    OpticalScannerService,
)

router = APIRouter(prefix="/optical-scanner", tags=["optical-scanner"])


@router.post("/scan", response_model=SuccessResponse[OpticalScanResponse])
async def scan_optical_form(
    body: OpticalScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[OpticalScanResponse]:
    """Scan optical form camera image, detect marked bubbles, grade exam & calculate ÖSYM score."""
    data = await OpticalScannerService(db).scan_and_grade(current_user.id, body)
    return SuccessResponse(data=data, message="Optik form başarıyla tarandı ve puanlandı")
