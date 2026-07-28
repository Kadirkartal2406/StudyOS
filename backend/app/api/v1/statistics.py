"""
StudyOS — Statistics Endpoint'leri
Bkz. docs/architecture/api-design.md §2.9 (Sprint-1.6)
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.statistics import (
    ProductivityInsight,
    StatisticsDailyResponse,
    StatisticsDistributionResponse,
    StatisticsHeatmapResponse,
    StatisticsOverview,
    StatisticsPeriodResponse,
    StatisticsStreak,
)
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/overview", response_model=SuccessResponse[StatisticsOverview])
async def get_statistics_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsOverview]:
    data = await StatisticsService(db).get_overview(current_user.id)
    return SuccessResponse(data=data)


@router.get("/daily", response_model=SuccessResponse[StatisticsDailyResponse])
async def get_statistics_daily(
    target_date: date | None = Query(default=None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsDailyResponse]:
    data = await StatisticsService(db).get_daily(current_user.id, target_date)
    return SuccessResponse(data=data)


@router.get("/weekly", response_model=SuccessResponse[StatisticsPeriodResponse])
async def get_statistics_weekly(
    anchor: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsPeriodResponse]:
    data = await StatisticsService(db).get_weekly(current_user.id, anchor)
    return SuccessResponse(data=data)


@router.get("/monthly", response_model=SuccessResponse[StatisticsPeriodResponse])
async def get_statistics_monthly(
    anchor: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsPeriodResponse]:
    data = await StatisticsService(db).get_monthly(current_user.id, anchor)
    return SuccessResponse(data=data)


@router.get("/subjects", response_model=SuccessResponse[StatisticsDistributionResponse])
async def get_statistics_subjects(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsDistributionResponse]:
    data = await StatisticsService(db).get_subjects(
        current_user.id, date_from=date_from, date_to=date_to
    )
    return SuccessResponse(data=data)


@router.get("/topics", response_model=SuccessResponse[StatisticsDistributionResponse])
async def get_statistics_topics(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsDistributionResponse]:
    data = await StatisticsService(db).get_topics(
        current_user.id, date_from=date_from, date_to=date_to
    )
    return SuccessResponse(data=data)


@router.get("/productivity", response_model=SuccessResponse[ProductivityInsight])
async def get_statistics_productivity(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ProductivityInsight]:
    data = await StatisticsService(db).get_productivity(
        current_user.id, date_from=date_from, date_to=date_to
    )
    return SuccessResponse(data=data)


@router.get("/heatmap", response_model=SuccessResponse[StatisticsHeatmapResponse])
async def get_statistics_heatmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsHeatmapResponse]:
    data = await StatisticsService(db).get_heatmap(current_user.id)
    return SuccessResponse(data=data)


@router.get("/streak", response_model=SuccessResponse[StatisticsStreak])
async def get_statistics_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[StatisticsStreak]:
    data = await StatisticsService(db).get_streak(current_user.id)
    return SuccessResponse(data=data)
