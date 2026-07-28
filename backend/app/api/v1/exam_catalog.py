"""Exam Intelligence Catalog API (Sprint X) — read-only."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.exam_catalog import (
    EiExamRead,
    EiExamSummary,
    EiImportanceItem,
    EiPackRead,
    EiSubjectRead,
    EiTopicRead,
)
from app.services.exam_catalog_service import ExamCatalogService

router = APIRouter()


@router.get("", response_model=SuccessResponse[list[EiExamSummary]])
async def list_exams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[EiExamSummary]]:
    data = await ExamCatalogService(db).list_exams()
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/topics/{topic}", response_model=SuccessResponse[EiTopicRead])
async def get_topic(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[EiTopicRead]:
    data = await ExamCatalogService(db).get_topic(topic)
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/{exam}", response_model=SuccessResponse[EiExamRead])
async def get_exam(
    exam: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[EiExamRead]:
    data = await ExamCatalogService(db).get_exam_tree(exam)
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/{exam}/packs", response_model=SuccessResponse[list[EiPackRead]])
async def list_packs(
    exam: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[EiPackRead]]:
    data = await ExamCatalogService(db).list_packs(exam)
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/{exam}/packs/{pack}", response_model=SuccessResponse[EiPackRead])
async def get_pack(
    exam: str,
    pack: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[EiPackRead]:
    data = await ExamCatalogService(db).get_pack(exam, pack)
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/{exam}/subjects", response_model=SuccessResponse[list[EiSubjectRead]])
async def list_subjects(
    exam: str,
    pack: str | None = Query(None),
    branch: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[EiSubjectRead]]:
    data = await ExamCatalogService(db).list_subjects(
        exam, pack_code=pack, branch_key=branch
    )
    await db.commit()
    return SuccessResponse(data=data)


@router.get(
    "/{exam}/subjects/{subject}/topics",
    response_model=SuccessResponse[list[EiTopicRead]],
)
async def list_subject_topics(
    exam: str,
    subject: str,
    pack: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[EiTopicRead]]:
    data = await ExamCatalogService(db).list_topics(
        exam, subject, pack_code=pack
    )
    await db.commit()
    return SuccessResponse(data=data)


@router.get(
    "/{exam}/importance",
    response_model=SuccessResponse[list[EiImportanceItem]],
)
async def importance(
    exam: str,
    pack: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[EiImportanceItem]]:
    data = await ExamCatalogService(db).importance_ranking(
        exam, pack_code=pack, limit=limit
    )
    await db.commit()
    return SuccessResponse(data=data)
