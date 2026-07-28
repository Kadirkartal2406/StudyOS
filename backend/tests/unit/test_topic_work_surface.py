"""Alignment Sprint-3 — Topic Work Surface projection unit tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.services.learning_profile_service import LearningProfileService


@pytest.mark.asyncio
async def test_work_surface_applies_decision_does_not_invent():
    """Work Surface primary_action Decision Engine'den; yüzey karar üretmez."""
    topic = MagicMock()
    topic.code = "tyt_mat_problemler"
    topic.name = "Problemler"
    topic.subject_code = "tyt_matematik"

    catalog = MagicMock()
    catalog.name = "TYT Matematik"

    svc = LearningProfileService(MagicMock())
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.get_topic_by_code = AsyncMock(return_value=topic)
    svc.repo.get_catalog_by_code = AsyncMock(return_value=catalog)
    svc._topic_revision_due = AsyncMock(return_value=False)

    surface = await svc.get_topic_work_surface(
        uuid.uuid4(), "tyt_matematik", "tyt_mat_problemler"
    )

    assert surface.learning_state.topic_code == "tyt_mat_problemler"
    assert surface.learning_state.revision_due is False
    assert surface.learning_state.summary_line is not None
    assert surface.primary_action.title == "Bu konu üzerinde çalış"
    assert surface.primary_action.purpose == "study"
    assert surface.primary_action.tool_hint == "pomodoro"
    assert surface.primary_action.deep_link_hint == (
        "/subjects/tyt_matematik/topics/tyt_mat_problemler"
    )
    tool_ids = [t.id for t in surface.secondary_tools]
    assert tool_ids == ["pomodoro", "resources", "questions", "revision"]
    assert "explain" not in tool_ids
    assert "notebooklm" not in tool_ids


@pytest.mark.asyncio
async def test_work_surface_review_when_revision_due():
    topic = MagicMock()
    topic.code = "tyt_mat_turev"
    topic.name = "Türev"
    topic.subject_code = "tyt_matematik"

    svc = LearningProfileService(MagicMock())
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.get_topic_by_code = AsyncMock(return_value=topic)
    catalog = MagicMock()
    catalog.name = "TYT Matematik"
    svc.repo.get_catalog_by_code = AsyncMock(return_value=catalog)
    svc._topic_revision_due = AsyncMock(return_value=True)

    surface = await svc.get_topic_work_surface(
        uuid.uuid4(), "tyt_matematik", "tyt_mat_turev"
    )
    assert surface.learning_state.revision_due is True
    assert surface.primary_action.purpose == "review"
    assert surface.primary_action.tool_hint == "revision"
    assert surface.primary_action.title == "Bu konu üzerinde tekrar yap"


@pytest.mark.asyncio
async def test_work_surface_unknown_topic():
    svc = LearningProfileService(MagicMock())
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.get_topic_by_code = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await svc.get_topic_work_surface(uuid.uuid4(), "tyt_matematik", "missing")
