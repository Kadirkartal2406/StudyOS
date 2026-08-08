from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from datetime import datetime

from app.core.dependencies import verify_deneme_api_key, get_current_user
from app.database.base import get_db
from app.services.trial_exam_scheduler import generate_trial_exams_for_date

router = APIRouter()

@router.post("/generate", dependencies=[Depends(verify_deneme_api_key)])
async def trigger_trial_exam_generation(
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Manually trigger the 03:00 trial exam generation pass for today."""
    from app.services.trial_exam_scheduler import _now_istanbul
    
    challenge_date = _now_istanbul().date()
    done = await generate_trial_exams_for_date(challenge_date)
    return {
        "status": "success" if done else "incomplete",
        "date": str(challenge_date)
    }

@router.get("/history")
async def get_trial_exam_history(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    """Get the list of historical trial exams."""
    from app.services.assessment_service import AssessmentService
    svc = AssessmentService(db)
    # Re-using the same historical assessment endpoint format but we know they are ready.
    history = await svc.daily_history(current_user.id)
    return history
