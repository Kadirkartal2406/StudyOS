"""
StudyOS — StudyResource service unit tests
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.schemas.study_resource import StudyResourceCreate, StudyResourceUpdate
from app.services.study_resource_service import StudyResourceService
from app.models.study_resource import ResourceStatus, ResourceType


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Res",
        last_name="Unit",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_create_detects_youtube(db_session: AsyncSession):
    user = await _user(db_session, "res.yt@studyos.dev")
    svc = StudyResourceService(db_session)
    row = await svc.create_resource(
        user.id,
        StudyResourceCreate(
            title="Video",
            url="https://youtu.be/abc123",
            resource_type=ResourceType.OTHER,
        ),
    )
    assert row.resource_type == ResourceType.YOUTUBE
    assert row.provider == "youtube"
    assert row.metadata.get("youtube_ready") is False


@pytest.mark.asyncio
async def test_complete_sets_completed_at(db_session: AsyncSession):
    user = await _user(db_session, "res.done@studyos.dev")
    svc = StudyResourceService(db_session)
    created = await svc.create_resource(
        user.id, StudyResourceCreate(title="Kitap", resource_type=ResourceType.BOOK)
    )
    updated = await svc.update_resource(
        created.id,
        user.id,
        StudyResourceUpdate(status=ResourceStatus.COMPLETED),
    )
    assert updated.completed_at is not None
