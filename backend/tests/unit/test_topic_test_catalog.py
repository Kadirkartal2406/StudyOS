"""Topic Test Catalog — release idempotency, publish gates, no-Gemini start."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.constants import TOPIC_TEST_QUESTION_COUNT
from app.models.topic_test import (
    TopicTest,
    TopicTestAttemptStatus,
    TopicTestItem,
    TopicTestStatus,
)
from app.schemas.topic_test import TopicTestReleaseRequest, TopicTestSubmitRequest
from app.services.qie.planner import (
    QuestionPlanner,
    _difficulty_for_band,
    band_for_difficulty_score,
    difficulty_contract_for_band,
)
from app.services.qie.types import GenerateContext
from app.services.topic_test_catalog_service import TopicTestCatalogService, iso_week_id
from app.services.topic_test_release_service import TopicTestReleaseService


def _card(
    i: int,
    *,
    difficulty: str = "easy",
    exam: str = "kpss",
    subject_code: str = "tarih",
    topic_code: str = "osmanli",
    skill: str = "chronology",
    content_hash: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        content_hash=content_hash or f"hash-{difficulty}-{i}-{uuid.uuid4().hex[:8]}",
        stem=f"Soru {difficulty} {i}?",
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="A",
        explanation="açıklama",
        qie_card={"skill": skill},
        use_count=0,
        difficulty_band=difficulty,
        exam=exam,
        subject_code=subject_code,
        topic_code=topic_code,
    )


def _mock_db() -> AsyncMock:
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    db.refresh = AsyncMock()

    @asynccontextmanager
    async def _nested():
        yield

    db.begin_nested = MagicMock(side_effect=lambda: _nested())
    return db


@pytest.mark.asyncio
async def test_release_idempotent_same_week():
    db = _mock_db()
    svc = TopicTestReleaseService(db)

    published = TopicTest(
        id=uuid.uuid4(),
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="easy",
        ordinal=1,
        status=TopicTestStatus.PUBLISHED,
        question_count=10,
    )
    db.scalar = AsyncMock(return_value=published)

    outcome = await svc.release_or_skip_one(
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="easy",
        fill_pool_if_short=False,
    )
    assert outcome == "skipped:already_published"


@pytest.mark.asyncio
async def test_duplicate_weekly_release_skips_all_diffs():
    db = _mock_db()
    svc = TopicTestReleaseService(db)

    async def already_published(*_a, **_k):
        return "skipped:already_published"

    with patch.object(svc, "release_or_skip_one", AsyncMock(side_effect=already_published)):
        result = await svc.release_topic_week(
            TopicTestReleaseRequest(
                exam="kpss",
                subject_code="tarih",
                topic_code="osmanli",
                week_id="2026-W33",
                fill_pool_if_short=False,
            )
        )
    assert len(result.skipped) == 3
    assert result.created == []
    assert result.failed == []


@pytest.mark.asyncio
async def test_incomplete_test_not_published():
    db = _mock_db()
    svc = TopicTestReleaseService(db)

    with (
        patch.object(svc, "pick_cards", AsyncMock(return_value=[_card(i) for i in range(9)])),
        patch.object(svc, "next_ordinal", AsyncMock(return_value=1)),
    ):
        db.scalar = AsyncMock(return_value=None)

        outcome = await svc.release_or_skip_one(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            week_id="2026-W33",
            difficulty="easy",
            fill_pool_if_short=False,
        )
    assert outcome.startswith("failed:short:9")
    added = [c.args[0] for c in db.add.call_args_list]
    tests = [a for a in added if isinstance(a, TopicTest)]
    assert tests
    assert tests[0].status == TopicTestStatus.FAILED
    assert tests[0].published_at is None


@pytest.mark.asyncio
async def test_published_test_immutable():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    published = TopicTest(
        id=uuid.uuid4(),
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="medium",
        ordinal=1,
        status=TopicTestStatus.PUBLISHED,
        question_count=10,
        published_at=datetime.now(UTC),
    )
    db.scalar = AsyncMock(return_value=published)
    with patch.object(svc, "pick_cards", AsyncMock()) as pick:
        outcome = await svc.release_or_skip_one(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            week_id="2026-W33",
            difficulty="medium",
            fill_pool_if_short=True,
        )
    assert outcome == "skipped:already_published"
    pick.assert_not_called()
    assert published.status == TopicTestStatus.PUBLISHED


@pytest.mark.asyncio
async def test_publish_requires_exactly_10_and_locks_cards():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    cards = [_card(i, difficulty="medium") for i in range(10)]

    with (
        patch.object(svc, "pick_cards", AsyncMock(return_value=cards)),
        patch.object(svc, "next_ordinal", AsyncMock(return_value=2)),
    ):
        db.scalar = AsyncMock(return_value=None)

        outcome = await svc.release_or_skip_one(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            week_id="2026-W34",
            difficulty="medium",
            fill_pool_if_short=False,
        )
    assert outcome == "created:published"
    added = [c.args[0] for c in db.add.call_args_list]
    test = next(a for a in added if isinstance(a, TopicTest))
    items = [a for a in added if isinstance(a, TopicTestItem)]
    assert test.status == TopicTestStatus.PUBLISHED
    assert test.question_count == TOPIC_TEST_QUESTION_COUNT
    assert test.ordinal == 2
    assert len(items) == 10
    assert {it.pool_card_id for it in items} == {c.id for c in cards}


@pytest.mark.asyncio
async def test_wrong_difficulty_rejected_at_publish():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    cards = [_card(i, difficulty="medium") for i in range(10)]

    with (
        patch.object(svc, "pick_cards", AsyncMock(return_value=cards)),
        patch.object(svc, "next_ordinal", AsyncMock(return_value=1)),
    ):
        db.scalar = AsyncMock(return_value=None)
        outcome = await svc.release_or_skip_one(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            week_id="2026-W33",
            difficulty="easy",
            fill_pool_if_short=False,
        )
    assert outcome.startswith("failed:short")
    added = [c.args[0] for c in db.add.call_args_list]
    tests = [a for a in added if isinstance(a, TopicTest)]
    assert tests[0].status == TopicTestStatus.FAILED


@pytest.mark.asyncio
async def test_wrong_domain_rejected_at_publish():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    cards = [_card(i, difficulty="easy", skill="spelling") for i in range(10)]

    with (
        patch.object(svc, "pick_cards", AsyncMock(return_value=cards)),
        patch.object(svc, "next_ordinal", AsyncMock(return_value=1)),
    ):
        db.scalar = AsyncMock(return_value=None)
        outcome = await svc.release_or_skip_one(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            week_id="2026-W33",
            difficulty="easy",
            fill_pool_if_short=False,
        )
    assert outcome.startswith("failed:short")


@pytest.mark.asyncio
async def test_pick_cards_excludes_catalogued_pool_ids():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    used_id = uuid.uuid4()
    fresh = _card(1)
    dup = _card(2)
    dup.id = used_id

    with (
        patch.object(
            svc,
            "catalogued_pool_card_ids",
            AsyncMock(return_value={used_id}),
        ),
        patch.object(
            svc,
            "catalogued_content_hashes",
            AsyncMock(return_value=set()),
        ),
        patch.object(
            svc.pool,
            "get_unused_for_topic",
            AsyncMock(return_value=[dup, fresh]),
        ),
    ):
        picked = await svc.pick_cards(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            difficulty="easy",
            need=10,
        )
    assert all(c.id != used_id for c in picked)
    assert fresh in picked


@pytest.mark.asyncio
async def test_duplicate_pool_card_rejected_in_pick():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    used = uuid.uuid4()
    with (
        patch.object(svc, "catalogued_pool_card_ids", AsyncMock(return_value={used})),
        patch.object(svc, "catalogued_content_hashes", AsyncMock(return_value=set())),
        patch.object(
            svc.pool,
            "get_unused_for_topic",
            AsyncMock(
                return_value=[
                    SimpleNamespace(
                        id=used,
                        content_hash="h1",
                        difficulty_band="easy",
                    )
                ]
            ),
        ),
    ):
        picked = await svc.pick_cards(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            difficulty="easy",
            need=10,
        )
    assert picked == []


@pytest.mark.asyncio
async def test_duplicate_content_hash_rejected_in_pick():
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    with (
        patch.object(svc, "catalogued_pool_card_ids", AsyncMock(return_value=set())),
        patch.object(
            svc, "catalogued_content_hashes", AsyncMock(return_value={"dup-hash"})
        ),
        patch.object(
            svc.pool,
            "get_unused_for_topic",
            AsyncMock(
                return_value=[
                    _card(1, content_hash="dup-hash"),
                    _card(2, content_hash="fresh-hash"),
                ]
            ),
        ),
    ):
        picked = await svc.pick_cards(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            difficulty="easy",
            need=10,
        )
    assert len(picked) == 1
    assert picked[0].content_hash == "fresh-hash"


@pytest.mark.asyncio
async def test_failed_seed_can_resume():
    """Failed row is reused; second run with enough cards publishes."""
    db = _mock_db()
    svc = TopicTestReleaseService(db)
    failed = TopicTest(
        id=uuid.uuid4(),
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="hard",
        ordinal=1,
        status=TopicTestStatus.FAILED,
        question_count=3,
    )
    cards = [_card(i, difficulty="hard") for i in range(10)]

    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=exec_result)
    db.scalar = AsyncMock(return_value=failed)

    with patch.object(svc, "pick_cards", AsyncMock(return_value=cards)):
        outcome = await svc.release_or_skip_one(
            exam="kpss",
            subject_code="tarih",
            topic_code="osmanli",
            week_id="2026-W33",
            difficulty="hard",
            fill_pool_if_short=False,
        )
    assert outcome == "created:published"
    assert failed.status == TopicTestStatus.PUBLISHED


@pytest.mark.asyncio
async def test_start_attempt_never_calls_gemini():
    db = _mock_db()
    svc = TopicTestCatalogService(db)
    test_id = uuid.uuid4()
    items = [
        TopicTestItem(
            id=uuid.uuid4(),
            test_id=test_id,
            ord_index=i,
            pool_card_id=uuid.uuid4(),
            content_hash=f"h{i}",
            stem=f"S{i}",
            choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
            correct_key="A",
            explanation=None,
            qie_card={},
        )
        for i in range(10)
    ]
    test = TopicTest(
        id=test_id,
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="easy",
        ordinal=1,
        status=TopicTestStatus.PUBLISHED,
        question_count=10,
        items=items,
    )

    db.scalar = AsyncMock(side_effect=[test, None])

    with patch("app.services.topic_test_catalog_service.QieOrchestrator", create=True) as orch:
        read = await svc.start_attempt(uuid.uuid4(), test_id)
        orch.assert_not_called()

    assert read.question_count == 10
    assert len(read.items) == 10
    assert read.status == TopicTestAttemptStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_start_rejects_unpublished():
    db = _mock_db()
    svc = TopicTestCatalogService(db)
    draft = TopicTest(
        id=uuid.uuid4(),
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="easy",
        ordinal=1,
        status=TopicTestStatus.DRAFT,
        question_count=10,
        items=[],
    )
    db.scalar = AsyncMock(return_value=draft)
    from app.core.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await svc.start_attempt(uuid.uuid4(), draft.id)


@pytest.mark.asyncio
async def test_submit_scores_correct_wrong_blank():
    db = _mock_db()
    svc = TopicTestCatalogService(db)
    test_id = uuid.uuid4()
    attempt_id = uuid.uuid4()
    items = [
        TopicTestItem(
            id=uuid.uuid4(),
            test_id=test_id,
            ord_index=i,
            pool_card_id=uuid.uuid4(),
            content_hash=f"h{i}",
            stem=f"S{i}",
            choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
            correct_key="A",
            explanation="x",
            qie_card={},
        )
        for i in range(10)
    ]
    test = TopicTest(
        id=test_id,
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
        week_id="2026-W33",
        difficulty="hard",
        ordinal=1,
        status=TopicTestStatus.PUBLISHED,
        question_count=10,
        items=items,
    )
    from app.models.topic_test import TopicTestAttempt

    attempt = TopicTestAttempt(
        id=attempt_id,
        user_id=uuid.uuid4(),
        test_id=test_id,
        status=TopicTestAttemptStatus.IN_PROGRESS,
        answers=[],
    )
    attempt.test = test

    db.scalar = AsyncMock(return_value=attempt)

    body = TopicTestSubmitRequest(
        answers=[
            {"item_id": items[0].id, "selected_key": "A"},
            {"item_id": items[1].id, "selected_key": "B"},
        ]
    )
    result = await svc.submit(attempt.user_id, attempt_id, body)
    assert result.correct_count == 1
    assert result.wrong_count == 1
    assert result.blank_count == 8
    assert result.accuracy_pct == 10.0


@pytest.mark.asyncio
async def test_admin_status_shape():
    from app.services.topic_test_admin_service import TopicTestAdminService

    db = _mock_db()
    svc = TopicTestAdminService(db)

    t = TopicTest(
        id=uuid.uuid4(),
        exam="kpss_lisans",
        subject_code="tarih",
        topic_code="osmanli",
        subject_name="Tarih",
        topic_name="Osmanlı",
        week_id="2026-W33",
        difficulty="easy",
        ordinal=1,
        status=TopicTestStatus.PUBLISHED,
        question_count=10,
        published_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = [t]
    db.execute = AsyncMock(return_value=exec_res)
    db.scalar = AsyncMock(return_value=t.published_at)

    with patch.object(svc, "inventory_topic_count", return_value=2):
        data = await svc.status(week_id="2026-W33", limit_topics=10)

    assert data["current_week"] == "2026-W33"
    assert data["published_tests"] == 1
    assert data["easy_published"] == 1
    assert data["missing_tests"] == 2 * 3 - 1
    assert "weekly_progress" in data
    assert "topics" in data


def test_iso_week_id_istanbul_not_utc_edge():
    sun_utc = datetime(2026, 8, 9, 23, 30, tzinfo=UTC)  # Sunday
    wid = iso_week_id(sun_utc)
    assert wid == "2026-W33"


def test_iso_week_id_format():
    wid = iso_week_id(datetime(2026, 8, 13, tzinfo=UTC))
    assert wid.startswith("2026-W")
    assert len(wid) == 8


def test_difficulty_bands_do_not_overlap():
    for i in range(10):
        e = _difficulty_for_band("easy", i, 10)
        m = _difficulty_for_band("medium", i, 10)
        h = _difficulty_for_band("hard", i, 10)
        assert e <= 50
        assert 55 <= m <= 78
        assert h >= 80
        assert band_for_difficulty_score(e) == "easy"
        assert band_for_difficulty_score(m) == "medium"
        assert band_for_difficulty_score(h) == "hard"


def test_planner_preserves_difficulty_band():
    planner = QuestionPlanner()
    for band in ("easy", "medium", "hard"):
        plans = planner.plan_batch(
            GenerateContext(
                exam="kpss",
                subject_code="tarih",
                subject_name="Tarih",
                topic_code="osmanli",
                topic_name="Osmanlı",
                count=5,
                difficulty_band=band,
            )
        )
        assert len(plans) == 5
        for p in plans:
            assert band_for_difficulty_score(p.difficulty) == band
    assert "EASY" in difficulty_contract_for_band("easy")
    assert "HARD" in difficulty_contract_for_band("hard") or "çok adımlı" in difficulty_contract_for_band("hard")


def test_prompt_includes_difficulty_contract():
    from app.services.qie.prompt_builder_v3 import build_qie_messages
    from app.services.qie.types import QuestionPlan

    plan = QuestionPlan(
        exam="kpss",
        subject_code="tarih",
        subject_name="Tarih",
        topic_code="osmanli",
        topic_name="Osmanlı",
        skill="chronology",
        difficulty=38,
        bloom="understand",
        stem_type="factual_recall",
        index=0,
        choice_count=5,
    )
    messages, _fp = build_qie_messages([plan], style_dna={"exam_code": "kpss"})
    system = messages[0]["content"]
    assert "zorlaştırma YASAK" in system
    assert "EASY" in system.upper() or "easy" in system.lower()
    assert "EASY" in system or "düşük reasoning" in system


def test_cards_publishable_rejects_extra_count():
    svc = TopicTestReleaseService(AsyncMock())
    cards = [_card(i) for i in range(11)]
    ok, reason = svc._cards_publishable(
        cards[:11],
        difficulty="easy",
        exam="kpss",
        subject_code="tarih",
        topic_code="osmanli",
    )
    assert not ok
    assert reason.startswith("count:")
