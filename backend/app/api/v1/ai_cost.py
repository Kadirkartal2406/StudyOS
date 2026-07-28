"""M32 — AI cost metrics + internal batch generation API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import ValidationError
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.ai_cost.batch_generate import generate_batch_one_call
from app.services.ai_cost.budget import get_daily_budget
from app.services.ai_cost.cost_logger import get_cost_logger
from app.services.ai_cost.flags import (
    auto_booklet_enabled,
    background_ai_enabled,
    catchup_enabled,
    compact_author_enabled,
    midnight_scheduler_enabled,
)
from app.services.ai_cost.metrics import get_metrics
from app.services.ai_cost.pool import QuestionPoolService
from app.services.qie.types import GenerateContext

router = APIRouter()


class BatchGenerateBody(BaseModel):
    exam: str = "kpss"
    subject_code: str
    subject_name: str = ""
    topic_code: str
    topic_name: str = ""
    count: int = Field(default=20, ge=1, le=20)
    difficulty: str = "medium"


@router.get("/cost/metrics", response_model=SuccessResponse[dict])
async def ai_cost_metrics(
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[dict]:
    snap = get_metrics().snapshot()
    budget = get_daily_budget()
    logger = get_cost_logger()
    data = {
        **snap,
        "daily_ai_requests": logger.daily_count,
        "weekly_ai_requests": logger.weekly_count,
        "daily_budget_limit": budget.limit,
        "daily_budget_remaining": budget.remaining(),
        "pool_only_mode": budget.is_exhausted(),
        "flags": {
            "ENABLE_AUTO_BOOKLET": auto_booklet_enabled(),
            "ENABLE_BACKGROUND_AI": background_ai_enabled(),
            "ENABLE_MIDNIGHT_SCHEDULER": midnight_scheduler_enabled(),
            "ENABLE_CATCHUP": catchup_enabled(),
            "ENABLE_COMPACT_AUTHOR": compact_author_enabled(),
        },
    }
    return SuccessResponse(data=data)


@router.post("/cost/batch-generate", response_model=SuccessResponse[dict])
async def ai_batch_generate(
    body: BatchGenerateBody,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    """Internal: one Gemini call → up to 20 QuestionCards; also fills question pool."""
    ctx = GenerateContext(
        exam=body.exam.lower(),
        subject_code=body.subject_code.strip(),
        subject_name=body.subject_name or body.subject_code,
        topic_code=body.topic_code.strip(),
        topic_name=body.topic_name or body.topic_code,
        count=body.count,
        difficulty_band=body.difficulty,
        user_id=current_user.id,
        kind="batch_generate",
    )
    if not ctx.subject_code or not ctx.topic_code:
        raise ValidationError("subject_code ve topic_code gerekli")

    cards, fingerprint, result = await generate_batch_one_call(db, ctx, count=body.count)
    pool = QuestionPoolService(db)
    stored = 0
    for i, card in enumerate(cards):
        from app.services.ai_cost.pool import fingerprint_for_plan

        fp = fingerprint_for_plan(card.plan, ctx)
        # uniquify by index in fingerprint already
        await pool.put_card(
            fingerprint=fp,
            card=card,
            exam=ctx.exam,
            subject_code=ctx.subject_code,
            topic_code=ctx.topic_code,
            difficulty_band=ctx.difficulty_band,
            skill=card.plan.skill,
        )
        stored += 1
    await db.commit()
    return SuccessResponse(
        data={
            "count": len(cards),
            "stored_in_pool": stored,
            "fingerprint": fingerprint,
            "provider": result.provider if result else None,
            "model": result.model if result else None,
            "questions": [
                {
                    "stem": c.stem,
                    "choices": c.choices,
                    "correct_key": c.correct_key,
                    "plan_index": c.plan.index,
                }
                for c in cards
            ],
        },
        message=f"{len(cards)} soru (tek LLM çağrısı)",
    )
