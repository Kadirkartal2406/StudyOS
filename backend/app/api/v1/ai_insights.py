"""
StudyOS — AI Insights Endpoint'leri
Sprint-2.0 — GET /api/v1/ai/*
LLM chat endpoint'leri sonraki sprint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.ai_insights import (
    AiExplainRequest,
    AiExplainResponse,
    AiOverviewResponse,
    AiPerformanceResponse,
    AiProductivityResponse,
    AiRecommendationsResponse,
    AiTrendsResponse,
)
from app.schemas.common import SuccessResponse
from app.services.ai_insights_service import AiInsightsService

router = APIRouter()


@router.get("/overview", response_model=SuccessResponse[AiOverviewResponse])
async def get_ai_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiOverviewResponse]:
    data = await AiInsightsService(db).get_overview(current_user.id)
    return SuccessResponse(data=data)


@router.get("/recommendations", response_model=SuccessResponse[AiRecommendationsResponse])
async def get_ai_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiRecommendationsResponse]:
    data = await AiInsightsService(db).get_recommendations(current_user.id)
    return SuccessResponse(data=data)


@router.get("/trends", response_model=SuccessResponse[AiTrendsResponse])
async def get_ai_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiTrendsResponse]:
    data = await AiInsightsService(db).get_trends(current_user.id)
    return SuccessResponse(data=data)


@router.get("/performance", response_model=SuccessResponse[AiPerformanceResponse])
async def get_ai_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiPerformanceResponse]:
    data = await AiInsightsService(db).get_performance(current_user.id)
    return SuccessResponse(data=data)


@router.get("/productivity", response_model=SuccessResponse[AiProductivityResponse])
async def get_ai_productivity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiProductivityResponse]:
    data = await AiInsightsService(db).get_productivity(current_user.id)
    return SuccessResponse(data=data)


@router.post("/explain", response_model=SuccessResponse[AiExplainResponse])
async def ai_explain(
    body: AiExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiExplainResponse]:
    """Sprint-12: Turkish 1-2 sentence explanation for a next_action or topic context."""
    from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
    from app.services.learning_profile_service import LearningProfileService
    from app.services.notification_settings_service import NotificationSettingsService
    from app.services.observation_mode import ObservationMode

    lp_svc = LearningProfileService(db)
    profile = await lp_svc.get_profile(current_user.id)

    obs = ObservationMode(db)
    obs_state = await obs.get_state(current_user.id)

    active_exam = profile.active_exam_type or profile.primary_exam_type or "bilinmiyor"
    context_parts: list[str] = [
        f"Sınav: {active_exam}",
        f"Gözlem durumu: {obs_state}",
    ]
    if body.subject_code:
        context_parts.append(f"Ders kodu: {body.subject_code}")
    if body.topic_code:
        context_parts.append(f"Konu kodu: {body.topic_code}")
    context_str = ", ".join(context_parts)

    system = (
        "Sen StudyOS çalışma koçusun. Kısa, içten ve motive edici Türkçe açıklamalar yaparsın. "
        "Yalnızca 1-2 cümle yaz. Sayı veya istatistik uydurma."
    )
    user_msg = (
        f"Bağlam: {context_str}.\n"
        f"Durum: {body.reason or 'Öneri gerekçesi belirtilmedi.'}\n"
        "Kullanıcıya bu konuda 1-2 cümle Türkçe açıklama yaz."
    )

    pref = await NotificationSettingsService(db).get_or_create(current_user.id)
    result = await generate_with_fallback(
        GenerateRequest(
            messages=[
                ChatMessageDTO(role="system", content=system),
                ChatMessageDTO(role="user", content=user_msg),
            ],
            context={
                "context_type": body.context_type,
                "subject_code": body.subject_code,
                "topic_code": body.topic_code,
            },
        ),
        preferred=pref.ai_preferred_provider,
        model=pref.ai_preferred_model,
    )
    return SuccessResponse(data=AiExplainResponse(explanation=result.text))
