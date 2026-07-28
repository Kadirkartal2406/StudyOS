"""Sprint 19 — KnowledgeService index + retrieve."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_resource import ResourceStatus, ResourceType, StudyResource
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.services.knowledge_service import KnowledgeService


async def _make_user(db: AsyncSession) -> User:
    user = User(
        email=f"know.{uuid.uuid4()}@studyos.dev",
        hashed_password="irrelevant",
        first_name="Know",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=False,
    )
    return await UserRepository(db).add(user)


@pytest.mark.asyncio
async def test_index_resource_and_retrieve(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    resource = StudyResource(
        user_id=user.id,
        subject_code="kpss_turkce",
        topic_code="paragraf",
        title="Pegem Paragraf",
        description=(
            "Ana fikir tüm paragrafı kapsar. Destekleyici cümleler örnek verir. "
            "Çeldiriciler kısmi doğrular içerir."
        ),
        resource_type=ResourceType.PDF,
        status=ResourceStatus.NOT_STARTED,
        metadata_={"notes": "Sayfa 42 — ana fikir stratejisi"},
    )
    db_session.add(resource)
    await db_session.flush()

    svc = KnowledgeService(db_session)
    result = await svc.index_resource(user.id, resource.id, force=True)
    assert result.source.health == "ready"
    assert result.source.chunk_count >= 1

    nb = await svc.get_notebook(user.id, "kpss_turkce", "paragraf")
    assert nb.chunk_count >= 1
    assert nb.source_count >= 1

    passages = await svc.retrieve_for_topic(
        user.id, "kpss_turkce", "paragraf", "ana fikir", top_k=3
    )
    assert passages
    assert passages[0].source_title == "Pegem Paragraf"
