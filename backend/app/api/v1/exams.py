"""
StudyOS — Exams Endpoint'leri
Sprint-2.6 — /api/v1/exams (B2 — öğrenci deneme takibi)
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.question_record import ExamType
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.exam import (
    ExamCreate,
    ExamDetailRead,
    ExamListResponse,
    ExamResultsReplace,
    ExamStatistics,
    ExamTrends,
    ExamUpdate,
    ExamWriteResponse,
)
from app.services.exam_service import ExamService

router = APIRouter()


@router.get("/statistics", response_model=SuccessResponse[ExamStatistics])
async def exam_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamStatistics]:
    data = await ExamService(db).get_statistics(current_user.id)
    return SuccessResponse(data=data)


@router.get("/trends", response_model=SuccessResponse[ExamTrends])
async def exam_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamTrends]:
    data = await ExamService(db).get_trends(current_user.id)
    return SuccessResponse(data=data)


@router.get("", response_model=SuccessResponse[ExamListResponse])
async def list_exams(
    exam_type: ExamType | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamListResponse]:
    data = await ExamService(db).list_exams(current_user.id, exam_type=exam_type)
    return SuccessResponse(data=data)


@router.post(
    "",
    response_model=SuccessResponse[ExamWriteResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_exam(
    body: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamWriteResponse]:
    data = await ExamService(db).create_exam(current_user.id, body)
    return SuccessResponse(data=data, message="Deneme kaydedildi")


@router.get("/{exam_id}", response_model=SuccessResponse[ExamDetailRead])
async def get_exam(
    exam_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamDetailRead]:
    data = await ExamService(db).get_exam(exam_id, current_user.id)
    return SuccessResponse(data=data)


@router.patch("/{exam_id}", response_model=SuccessResponse[ExamDetailRead])
async def update_exam(
    exam_id: uuid.UUID,
    body: ExamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamDetailRead]:
    data = await ExamService(db).update_exam(exam_id, current_user.id, body)
    return SuccessResponse(data=data, message="Deneme güncellendi")


@router.put("/{exam_id}/results", response_model=SuccessResponse[ExamDetailRead])
async def replace_exam_results(
    exam_id: uuid.UUID,
    body: ExamResultsReplace,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamDetailRead]:
    data = await ExamService(db).replace_results(exam_id, current_user.id, body)
    return SuccessResponse(data=data, message="Sonuçlar güncellendi")


@router.delete("/{exam_id}", response_model=SuccessResponse[dict])
async def delete_exam(
    exam_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    await ExamService(db).delete_exam(exam_id, current_user.id)
    return SuccessResponse(data={}, message="Deneme silindi")
