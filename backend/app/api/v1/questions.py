"""
StudyOS — QuestionRecord Endpoint'leri
Sprint-1.9 — /api/v1/questions
"""

import math
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import QUESTION_RECORD_DEFAULT_PAGE_SIZE, QUESTION_RECORD_MAX_PAGE_SIZE
from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.question_record import ExamType, QuestionSource
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.question_record import (
    QuestionDailyResponse,
    QuestionDistributionResponse,
    QuestionRecordCreate,
    QuestionRecordRead,
    QuestionRecordUpdate,
    QuestionStatisticsOverview,
)
from app.schemas.question import AssetInteractiveQuestionDTO
from app.services.question_record_service import QuestionRecordService

router = APIRouter()

@router.get("/assets/{asset_id}", response_model=SuccessResponse[list[AssetInteractiveQuestionDTO]])
async def get_asset_questions(
    asset_id: uuid.UUID,
    limit: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[AssetInteractiveQuestionDTO]]:
    """Sprint A — Asset ID'ye göre interaktif soruları getir."""
    from app.services.ai_cost.pool import QuestionPoolService
    pool_svc = QuestionPoolService(db)
    
    # 1. Pool'dan çek
    cards = await pool_svc.get_by_asset_id(asset_id, limit=limit)
    
    # QIE AssetContextEngine tetiklemesi (AI katmanında yapılacak)
    
    data = [AssetInteractiveQuestionDTO.model_validate(c) for c in cards]
    return SuccessResponse(data=data)


@router.get("/statistics", response_model=SuccessResponse[QuestionStatisticsOverview])
async def get_question_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionStatisticsOverview]:
    data = await QuestionRecordService(db).get_statistics_overview(current_user.id)
    return SuccessResponse(data=data)


@router.get("/daily", response_model=SuccessResponse[QuestionDailyResponse])
async def get_question_daily(
    days: int = Query(default=14, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionDailyResponse]:
    data = await QuestionRecordService(db).get_daily(current_user.id, days=days)
    return SuccessResponse(data=data)


@router.get("/subjects", response_model=SuccessResponse[QuestionDistributionResponse])
async def get_question_subjects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionDistributionResponse]:
    data = await QuestionRecordService(db).get_subjects_distribution(current_user.id)
    return SuccessResponse(data=data)


@router.get("/topics", response_model=SuccessResponse[QuestionDistributionResponse])
async def get_question_topics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionDistributionResponse]:
    data = await QuestionRecordService(db).get_topics_distribution(current_user.id)
    return SuccessResponse(data=data)


@router.get("/exams", response_model=SuccessResponse[QuestionDistributionResponse])
async def get_question_exams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionDistributionResponse]:
    data = await QuestionRecordService(db).get_exams_distribution(current_user.id)
    return SuccessResponse(data=data)


@router.get("", response_model=PaginatedResponse[QuestionRecordRead])
async def list_questions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(
        default=QUESTION_RECORD_DEFAULT_PAGE_SIZE,
        ge=1,
        le=QUESTION_RECORD_MAX_PAGE_SIZE,
    ),
    date_from: date | None = None,
    date_to: date | None = None,
    subject: str | None = None,
    topic: str | None = None,
    exam_type: ExamType | None = None,
    source: QuestionSource | None = None,
    study_plan_id: uuid.UUID | None = None,
    study_session_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[QuestionRecordRead]:
    items, total = await QuestionRecordService(db).list_records(
        current_user.id,
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        subject=subject,
        topic=topic,
        exam_type=exam_type,
        source=source,
        study_plan_id=study_plan_id,
        study_session_id=study_session_id,
    )
    total_pages = max(1, math.ceil(total / page_size)) if total else 0
    return PaginatedResponse(
        data=[QuestionRecordRead.model_validate(i) for i in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{record_id}", response_model=SuccessResponse[QuestionRecordRead])
async def get_question(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionRecordRead]:
    record = await QuestionRecordService(db).get(record_id, current_user.id)
    return SuccessResponse(data=QuestionRecordRead.model_validate(record))


@router.post(
    "",
    response_model=SuccessResponse[QuestionRecordRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    body: QuestionRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionRecordRead]:
    record = await QuestionRecordService(db).create(current_user.id, body)
    return SuccessResponse(
        data=QuestionRecordRead.model_validate(record),
        message="Soru kaydı oluşturuldu",
    )


@router.put("/{record_id}", response_model=SuccessResponse[QuestionRecordRead])
async def update_question(
    record_id: uuid.UUID,
    body: QuestionRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuestionRecordRead]:
    record = await QuestionRecordService(db).update(record_id, current_user.id, body)
    return SuccessResponse(
        data=QuestionRecordRead.model_validate(record),
        message="Soru kaydı güncellendi",
    )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await QuestionRecordService(db).delete(record_id, current_user.id)
