"""
Sprint 19 — Knowledge Layer API
Index / Notebook / Citations — Decision üretmez.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.knowledge import (
    IndexResourceRequest,
    IndexResourceResult,
    KnowledgeCitationRead,
    KnowledgeNotebookRead,
    ReindexNotebookRequest,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.post(
    "/resources/{resource_id}/index",
    response_model=SuccessResponse[IndexResourceResult],
)
async def index_resource(
    resource_id: uuid.UUID,
    body: IndexResourceRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[IndexResourceResult]:
    req = body or IndexResourceRequest()
    data = await KnowledgeService(db).index_resource(
        current_user.id, resource_id, force=req.force
    )
    await db.commit()
    return SuccessResponse(data=data, message=data.message)


@router.post(
    "/notebook/reindex",
    response_model=SuccessResponse[KnowledgeNotebookRead],
)
async def reindex_notebook(
    body: ReindexNotebookRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[KnowledgeNotebookRead]:
    data = await KnowledgeService(db).reindex_topic(
        current_user.id,
        body.subject_code,
        body.topic_code,
        force=body.force,
    )
    await db.commit()
    return SuccessResponse(data=data, message="Konu kaynakları yenilendi")


@router.get(
    "/topics/{subject_code}/{topic_code}/notebook",
    response_model=SuccessResponse[KnowledgeNotebookRead],
)
async def get_topic_knowledge_notebook(
    subject_code: str,
    topic_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[KnowledgeNotebookRead]:
    data = await KnowledgeService(db).get_notebook(
        current_user.id, subject_code, topic_code
    )
    return SuccessResponse(data=data)


@router.get(
    "/notebook/{notebook_id}",
    response_model=SuccessResponse[KnowledgeNotebookRead],
)
async def get_notebook(
    notebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[KnowledgeNotebookRead]:
    data = await KnowledgeService(db).get_notebook_by_id(
        current_user.id, notebook_id
    )
    return SuccessResponse(data=data)


@router.get(
    "/notebook/{notebook_id}/citations",
    response_model=SuccessResponse[list[KnowledgeCitationRead]],
)
async def list_notebook_citations(
    notebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[KnowledgeCitationRead]]:
    data = await KnowledgeService(db).list_citations(
        current_user.id, notebook_id
    )
    return SuccessResponse(data=data)
