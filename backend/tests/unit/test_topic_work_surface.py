"""Alignment Sprint-3 — Topic Work Surface projection unit tests."""

import itertools
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.services.learning_profile_service import LearningProfileService


def _make_async_db():
    """Create a MagicMock db that supports unlimited awaiting .execute() calls.

    get_topic_work_surface makes two sequential db.execute calls:
      1. topic_stats  → .one() returns (minutes, sessions)            [2 values]
      2. qr_stats     → .one() returns (correct, wrong, blank, total) [4 values]
    After that, LearningIntelligenceService may also call execute via the same db.
    We cycle through both result shapes so the mock never exhausts.
    """
    db = MagicMock()

    def _result(values):
        r = MagicMock()
        r.one.return_value = values
        r.scalars.return_value.all.return_value = []
        r.scalar.return_value = None
        return r

    results = itertools.cycle([
        _result((0, 0)),           # topic_stats: (total_minutes, session_count)
        _result((0, 0, 0, 0)),     # qr_stats:    (correct, wrong, blank, total)
    ])

    async def _async_execute(*args, **kwargs):
        return next(results)

    db.execute = _async_execute
    return db


def _intel_mock():
    """Minimal LearningIntelligenceService mock."""
    from app.schemas.learning_intelligence import TopicIntelligenceCard
    inst = MagicMock()
    inst.topic_intelligence = AsyncMock(return_value=TopicIntelligenceCard(
        topic_name="Test Konu",
        headline="Test Başlık",
        summary="Test özet",
        next_steps=[],
        strengths=[],

        weak_points=[],
        confidence_level="medium",
    ))
    inst.topic_timeline = AsyncMock(return_value=[])
    inst.topic_insights = AsyncMock(return_value=MagicMock(items=[]))
    inst.quiz_history = AsyncMock(return_value=[])
    inst.resource_intelligence = AsyncMock(return_value=MagicMock(items=[]))
    return inst


@pytest.mark.asyncio
async def test_work_surface_applies_decision_does_not_invent():
    """Work Surface primary_action Decision Engine'den; yüzey karar üretmez."""
    topic = MagicMock()
    topic.code = "tyt_mat_problemler"
    topic.name = "Problemler"
    topic.subject_code = "tyt_matematik"

    catalog = MagicMock()
    catalog.name = "TYT Matematik"

    svc = LearningProfileService(_make_async_db())
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.get_topic_by_code = AsyncMock(return_value=topic)
    svc.repo.get_catalog_by_code = AsyncMock(return_value=catalog)
    svc._topic_revision_due = AsyncMock(return_value=False)

    # LearningIntelligenceService is imported locally inside the method —
    # patch at the module where the local import lives.
    with patch(
        "app.services.learning_intelligence_service.LearningIntelligenceService",
        return_value=_intel_mock(),
    ):
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
    assert tool_ids == ["pomodoro", "resources", "questions", "topic_quiz", "revision"]
    assert "explain" not in tool_ids
    assert "notebooklm" not in tool_ids


@pytest.mark.asyncio
async def test_work_surface_review_when_revision_due():
    topic = MagicMock()
    topic.code = "tyt_mat_turev"
    topic.name = "Türev"
    topic.subject_code = "tyt_matematik"

    svc = LearningProfileService(_make_async_db())
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.get_topic_by_code = AsyncMock(return_value=topic)
    catalog = MagicMock()
    catalog.name = "TYT Matematik"
    svc.repo.get_catalog_by_code = AsyncMock(return_value=catalog)
    svc._topic_revision_due = AsyncMock(return_value=True)

    with patch(
        "app.services.learning_intelligence_service.LearningIntelligenceService",
        return_value=_intel_mock(),
    ):
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


