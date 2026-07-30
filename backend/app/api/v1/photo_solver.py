"""
StudyOS — Photo Question Solver API (Sprint 34)
Upload photo of wrong question, get AI solution & 3-5 similar practice questions.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.photo_question_service import (
    PhotoQuestionService,
    PhotoSolveRequest,
    PhotoSolveResponse,
)

router = APIRouter(prefix="/photo-solver", tags=["photo-solver"])


@router.post("/solve", response_model=SuccessResponse[PhotoSolveResponse])
async def solve_photo_question(
    body: PhotoSolveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[PhotoSolveResponse]:
    """Upload photo of a wrong question, analyze solution, update profile & generate similar questions."""
    data = await PhotoQuestionService(db).solve_and_generate_similar(
        current_user.id, body
    )
    return SuccessResponse(data=data, message="Soru çözüldü ve benzer sorular üretildi")
