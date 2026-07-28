"""
StudyOS — StudySession Endpoint'leri
Bkz. docs/architecture/api-design.md §2.7 (Sprint-1.5 / Sprint-1.7)
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import STUDY_SESSION_HISTORY_DEFAULT_PAGE_SIZE
from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.study_session import StudySessionStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.study_session import (
    StudySessionFinishRequest,
    StudySessionRead,
    StudySessionStartRequest,
    StudySessionStatistics,
    StudyTodaySummary,
)
from app.services.study_session_service import StudySessionService

router = APIRouter()


@router.post("/break/start", response_model=SuccessResponse[StudySessionRead])
async def start_break(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    service = StudySessionService(db)
    session = await service.start_break(current_user.id)
    return SuccessResponse(data=await service.to_read(session), message="Mola başladı")


@router.post("/break/end", response_model=SuccessResponse[StudySessionRead])
async def end_break(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    service = StudySessionService(db)
    session = await service.end_break(current_user.id)
    return SuccessResponse(data=await service.to_read(session), message="Mola bitti")


@router.get("/today-summary", response_model=SuccessResponse[StudyTodaySummary])
async def today_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudyTodaySummary]:
    data = await StudySessionService(db).today_summary(current_user.id)
    return SuccessResponse(data=data)


@router.post(
    "/start",
    response_model=SuccessResponse[StudySessionRead],
    status_code=status.HTTP_201_CREATED,
)
async def start_study_session(
    body: StudySessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    """Yeni Pomodoro oturumu başlatır. Aktif oturum varken 409 döner."""
    service = StudySessionService(db)
    session = await service.start(current_user.id, body)
    return SuccessResponse(
        data=await service.to_read(session),
        message="Oturum başlatıldı",
    )


@router.post("/pause", response_model=SuccessResponse[StudySessionRead])
async def pause_study_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    """Aktif oturumu duraklatır."""
    service = StudySessionService(db)
    session = await service.pause(current_user.id)
    return SuccessResponse(
        data=await service.to_read(session),
        message="Oturum duraklatıldı",
    )


@router.post("/resume", response_model=SuccessResponse[StudySessionRead])
async def resume_study_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    """Duraklatılmış oturumu devam ettirir."""
    service = StudySessionService(db)
    session = await service.resume(current_user.id)
    return SuccessResponse(
        data=await service.to_read(session),
        message="Oturum devam ediyor",
    )


@router.post("/finish", response_model=SuccessResponse[StudySessionRead])
async def finish_study_session(
    body: StudySessionFinishRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    """Aktif oturumu tamamlar; bağlı plana ilerleme yazar."""
    service = StudySessionService(db)
    session = await service.finish(current_user.id, body or StudySessionFinishRequest())
    return SuccessResponse(
        data=await service.to_read(session),
        message="Oturum tamamlandı",
    )


@router.get("/active", response_model=SuccessResponse[StudySessionRead | None])
async def get_active_study_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead | None]:
    """M25 — aktif (running/paused) oturum; yoksa data=null."""
    service = StudySessionService(db)
    session = await service.get_active(current_user.id)
    if session is None:
        return SuccessResponse(data=None, message="Aktif oturum yok")
    return SuccessResponse(data=await service.to_read(session))


@router.get("/today", response_model=SuccessResponse[list[StudySessionRead]])
async def get_today_study_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[StudySessionRead]]:
    """Bugün başlayan oturumları listeler."""
    service = StudySessionService(db)
    sessions = await service.get_today(current_user.id)
    return SuccessResponse(data=[await service.to_read(s) for s in sessions])


@router.get("/history", response_model=PaginatedResponse[StudySessionRead])
async def get_study_session_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=STUDY_SESSION_HISTORY_DEFAULT_PAGE_SIZE, ge=1, le=100),
    date_from: date | None = None,
    date_to: date | None = None,
    study_plan_id: uuid.UUID | None = None,
    status_filter: StudySessionStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, description="Plan başlığı araması"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[StudySessionRead]:
    """Sayfalı oturum geçmişi (filtre + plan adı araması)."""
    service = StudySessionService(db)
    sessions, meta = await service.get_history(
        current_user.id,
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        study_plan_id=study_plan_id,
        status=status_filter,
        q=q,
    )
    return PaginatedResponse(
        data=[await service.to_read(s) for s in sessions],
        pagination=meta,
    )


@router.get("/statistics", response_model=SuccessResponse[StudySessionStatistics])
async def get_study_session_statistics(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionStatistics]:
    """Oturum istatistik özeti."""
    stats = await StudySessionService(db).get_statistics(
        current_user.id, date_from=date_from, date_to=date_to
    )
    return SuccessResponse(data=stats)


@router.get("/{session_id}", response_model=SuccessResponse[StudySessionRead])
async def get_study_session_detail(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StudySessionRead]:
    """Tek oturum detayı."""
    service = StudySessionService(db)
    session = await service.get_by_id(session_id, current_user.id)
    return SuccessResponse(data=await service.to_read(session))
