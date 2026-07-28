"""
StudyOS — Evidence Engine Endpoint'leri (LOS Module 1)
Debug / developer visibility endpoints.

Production'da bu endpoint'ler auth + admin gate ile korunabilir.
Şimdilik authenticated user kendi evidence'ını görebilir.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.topic_evidence import EvidenceCategory
from app.models.user import User
from app.repositories.topic_evidence_repository import TopicEvidenceRepository
from app.schemas.common import SuccessResponse
from app.services.evidence_service import EvidenceService

router = APIRouter()


@router.get("/topics/{topic_code}", response_model=SuccessResponse[dict])
async def list_topic_evidence(
    topic_code: str,
    category: EvidenceCategory | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    """Topic için evidence listesi (son N gün)."""
    repo = TopicEvidenceRepository(db)
    since = datetime.now(UTC) - timedelta(days=days)
    rows = await repo.list_for_topic(
        current_user.id,
        topic_code,
        category=category,
        since=since,
        limit=200,
    )
    return SuccessResponse(
        data={
            "topic_code": topic_code,
            "total": len(rows),
            "items": [
                {
                    "id": str(r.id),
                    "category": r.category,
                    "horizon": r.horizon,
                    "value": r.value,
                    "quality_weight": r.quality_weight,
                    "source_type": r.source_type,
                    "occurred_at": r.occurred_at.isoformat(),
                    "metadata": r.metadata_,
                }
                for r in rows
            ],
        }
    )


@router.get("/topics/{topic_code}/aggregate", response_model=SuccessResponse[dict])
async def topic_aggregate(
    topic_code: str,
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    """Topic'in quality-weighted aggregate özeti (Confidence Engine input)."""
    since = datetime.now(UTC) - timedelta(days=days)
    data = await EvidenceService(db).topic_aggregate(
        current_user.id,
        topic_code,
        since=since,
    )
    return SuccessResponse(data=data)


@router.get("/summary", response_model=SuccessResponse[dict])
async def evidence_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    """Kullanıcının genel evidence durumu."""
    repo = TopicEvidenceRepository(db)
    topic_count = await repo.distinct_topic_count(current_user.id)
    return SuccessResponse(
        data={
            "distinct_bound_topics": topic_count,
            "observation_ready": topic_count >= 3,
        }
    )
