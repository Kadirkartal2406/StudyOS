"""Seed script safety: quota must not crash release; full seed gated."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import AIQuotaExceededError
from app.services.topic_test_release_service import TopicTestReleaseService


@pytest.mark.asyncio
async def test_ensure_pool_stock_swallows_quota():
    """Quota failure returns 0 and must not touch the release session."""
    db = AsyncMock()
    svc = TopicTestReleaseService(db)
    fill_db = AsyncMock()

    @asynccontextmanager
    async def _session():
        yield fill_db

    with (
        patch(
            "app.database.base.AsyncSessionLocal",
            MagicMock(side_effect=lambda: _session()),
        ),
        patch(
            "app.services.question_pool_manager.QuestionPoolManagerService"
        ) as mgr_cls,
    ):
        mgr = mgr_cls.return_value
        mgr._count_topic = AsyncMock(return_value=0)
        mgr.fill_topic_to_target = AsyncMock(
            side_effect=AIQuotaExceededError("quota")
        )
        accepted = await svc.ensure_pool_stock(
            exam="tyt",
            subject_code="tyt_matematik",
            topic_code="tyt_mat_problemler",
            subject_name="Matematik",
            topic_name="Problemler",
            difficulty="easy",
            need=10,
        )
    assert accepted == 0
    db.rollback.assert_not_awaited()


def test_seed_script_refuses_full_without_confirm(tmp_path):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(".").resolve()))
    from scripts import seed_topic_test_catalog as mod

    audit = mod.build_audit_report()
    assert audit["audit"]["topic_count"] == 328
    assert audit["target"]["total_questions"] == 328 * 30
    pilot = mod.select_topics(exam=None, limit=None, pilot=True, topic_codes=None)
    assert len(pilot) == 9
    exams = {p[0] for p in pilot}
    assert exams == {"kpss_lisans", "tyt", "ayt_sayisal"}
    assert all("uncertain" not in p[2] for p in pilot)
