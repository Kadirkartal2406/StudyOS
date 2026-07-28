"""
Sprint 14 — Topic Quiz API
POST generate → GET → POST submit (Evidence)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import ValidationError
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.learning_intelligence import QuizHistoryItem
from app.schemas.topic_quiz import (
    QuizGenerateRequest,
    QuizGenerationRead,
    QuizSubmitRequest,
    QuizSubmitResult,
)
from app.services.learning_intelligence_service import LearningIntelligenceService
from app.services.topic_quiz_service import TopicQuizService

router = APIRouter()


@router.get(
    "/subjects/{subject_code}/topics/{topic_code}/history",
    response_model=SuccessResponse[list[QuizHistoryItem]],
)
async def list_topic_quiz_history(
    subject_code: str,
    topic_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[QuizHistoryItem]]:
    """Sprint 15 — Topic quiz geçmişi."""
    data = await LearningIntelligenceService(db).quiz_history(
        current_user.id, topic_code.strip(), limit=30
    )
    return SuccessResponse(data=data)


@router.post(
    "/subjects/{subject_code}/topics/{topic_code}/generate",
    response_model=SuccessResponse[QuizGenerationRead],
)
async def generate_topic_quiz(
    subject_code: str,
    topic_code: str,
    body: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuizGenerationRead]:
    """Intent → LLM → Quality Gate → READY quiz (doğru cevaplar gizli)."""
    try:
        data = await TopicQuizService(db).generate(
            current_user.id, subject_code, topic_code, body
        )
    except ValidationError:
        await db.commit()
        raise
    await db.commit()
    return SuccessResponse(
        data=data,
        message=f"{data.valid_item_count} soru üretildi",
    )


@router.get(
    "/{generation_id}",
    response_model=SuccessResponse[QuizGenerationRead],
)
async def get_topic_quiz(
    generation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuizGenerationRead]:
    data = await TopicQuizService(db).get(current_user.id, generation_id)
    return SuccessResponse(data=data)


@router.post(
    "/{generation_id}/submit",
    response_model=SuccessResponse[QuizSubmitResult],
)
async def submit_topic_quiz(
    generation_id: uuid.UUID,
    body: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuizSubmitResult]:
    """Cevapları kaydet → Evidence (Living Plan tetiklenmez)."""
    data = await TopicQuizService(db).submit(current_user.id, generation_id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Quiz gönderildi")
