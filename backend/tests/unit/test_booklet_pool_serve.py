"""Booklet pool-serve correctness parity (Phase 1)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.correctness.constants import CORRECTNESS_VERSION
from app.services.correctness.gate import run_correctness_gate
from app.services.qie.types import QuestionPlan
from tests.unit.test_correctness_gate import LGS_Q5, TURKCE_PARAGRAF, VALID_MATH


def _plan(**kwargs) -> QuestionPlan:
    base = dict(
        exam="lgs_sayisal",
        subject_code="lgs_matematik",
        subject_name="Matematik",
        topic_code="geometri",
        topic_name="Geometri",
        skill="apply",
        index=0,
        choice_count=5,
        difficulty=70,
    )
    base.update(kwargs)
    return QuestionPlan(**base)


def _pool_row(question: dict, *, qie_card: dict | None = None, plan: QuestionPlan | None = None):
    plan = plan or _plan()
    return SimpleNamespace(
        id=uuid.uuid4(),
        stem=question["stem"],
        choices=dict(question["choices"]),
        correct_key=question["correct_key"],
        explanation=question.get("explanation"),
        qie_card=qie_card if qie_card is not None else {},
        subject_code=plan.subject_code,
        exam=plan.exam,
        topic_code=plan.topic_code,
        difficulty_band="medium",
        skill=plan.skill,
        use_count=0,
    )


def _pool_svc(candidates: list) -> object:
    from app.services.ai_cost.pool import QuestionPoolService

    pool = QuestionPoolService(MagicMock())
    pool.get_unused_for_topic = AsyncMock(return_value=list(candidates))
    pool.update_correctness_metadata = AsyncMock()
    pool.mark_quarantined = AsyncMock()
    pool.mark_used = AsyncMock()
    return pool


async def _serve(pool, *, plan: QuestionPlan | None = None, limit: int = 10):
    plan = plan or _plan()
    return await pool.serve_unused_for_topic(
        exam=plan.exam,
        subject_code=plan.subject_code,
        topic_code=plan.topic_code,
        difficulty_band="medium",
        limit=limit,
        pool_type="general",
    )


@pytest.mark.asyncio
async def test_booklet_01_fresh_pass_skips_recheck_and_increments_use_count(monkeypatch) -> None:
    plan = _plan()
    row = _pool_row(
        VALID_MATH,
        qie_card={
            "correctness": {
                "version": CORRECTNESS_VERSION,
                "verdict": "pass",
                "checked_at": "2026-01-01T00:00:00+00:00",
            }
        },
        plan=plan,
    )
    calls: list[str] = []
    real = run_correctness_gate

    def spy(inp, *a, **k):
        calls.append("gate")
        return real(inp, *a, **k)

    monkeypatch.setattr("app.services.correctness.gate.run_correctness_gate", spy)
    monkeypatch.setattr("app.services.correctness.apply.run_correctness_gate", spy)

    pool = _pool_svc([row])
    cards = await _serve(pool, plan=plan, limit=1)
    assert len(cards) == 1
    assert cards[0].correct_key == "B"
    assert calls == []
    pool.mark_used.assert_awaited_once_with(row.id)
    pool.mark_quarantined.assert_not_called()


@pytest.mark.asyncio
async def test_booklet_02_legacy_equivalent_options_not_served() -> None:
    plan = _plan()
    row = _pool_row(LGS_Q5, qie_card={}, plan=plan)
    pool = _pool_svc([row])
    cards = await _serve(pool, plan=plan, limit=1)
    assert cards == []
    pool.mark_used.assert_not_called()
    pool.mark_quarantined.assert_awaited()


@pytest.mark.asyncio
async def test_booklet_03_skip_fail_then_serve_valid_candidate() -> None:
    plan = _plan()
    bad = _pool_row(LGS_Q5, qie_card={}, plan=plan)
    good = _pool_row(VALID_MATH, qie_card={}, plan=plan)
    pool = _pool_svc([bad, good])
    cards = await _serve(pool, plan=plan, limit=1)
    assert len(cards) == 1
    assert cards[0].stem == VALID_MATH["stem"]
    pool.mark_quarantined.assert_awaited()
    pool.mark_used.assert_awaited_once_with(good.id)
    used_ids = [c.args[0] for c in pool.mark_used.await_args_list]
    assert bad.id not in used_ids


@pytest.mark.asyncio
async def test_booklet_04_legacy_valid_numeric_served() -> None:
    plan = _plan()
    row = _pool_row(VALID_MATH, qie_card={}, plan=plan)
    pool = _pool_svc([row])
    cards = await _serve(pool, plan=plan, limit=1)
    assert len(cards) == 1
    assert cards[0].correct_key == "B"
    assert cards[0].correctness_meta["verdict"] == "pass"
    pool.mark_used.assert_awaited_once_with(row.id)
    pool.mark_quarantined.assert_not_called()


@pytest.mark.asyncio
async def test_booklet_05_unsupported_passthrough_served() -> None:
    plan = _plan(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="paragraf",
        topic_name="Paragraf",
        skill="inference",
    )
    row = _pool_row(TURKCE_PARAGRAF, qie_card={}, plan=plan)
    pool = _pool_svc([row])
    cards = await _serve(pool, plan=plan, limit=1)
    assert len(cards) == 1
    assert cards[0].correctness_meta["verdict"] == "unsupported"
    pool.mark_used.assert_awaited_once_with(row.id)
    pool.mark_quarantined.assert_not_called()


@pytest.mark.asyncio
async def test_booklet_06_all_fail_candidates_not_served() -> None:
    plan = _plan()
    rows = [_pool_row(LGS_Q5, qie_card={}, plan=plan) for _ in range(3)]
    pool = _pool_svc(rows)
    cards = await _serve(pool, plan=plan, limit=3)
    assert cards == []
    pool.mark_used.assert_not_called()
    assert pool.mark_quarantined.await_count == 3


@pytest.mark.asyncio
async def test_booklet_07_empty_pool_keeps_bank_fallback(monkeypatch) -> None:
    from app.services.assessment_service import AssessmentService

    booklet_id = uuid.uuid4()
    booklet = SimpleNamespace(
        id=booklet_id,
        exam_type="lgs",
        branch_key="sayisal",
        difficulty="medium",
        section_plan={
            "sections": [
                {
                    "subject_code": "lgs_matematik",
                    "topics": [{"topic_code": "geometri", "count": 2}],
                }
            ]
        },
        requested_count=0,
        generation_progress=0,
        status="pending",
        error_message=None,
        questions=[],
    )
    added: list[object] = []
    db = SimpleNamespace(
        execute=AsyncMock(),
        flush=AsyncMock(),
        add=lambda obj: added.append(obj),
    )
    svc = AssessmentService(db)
    svc.repo = SimpleNamespace(get_shared_booklet_by_id=AsyncMock(return_value=booklet))
    pool = SimpleNamespace(serve_unused_for_topic=AsyncMock(return_value=[]))
    monkeypatch.setattr(
        "app.services.ai_cost.pool.QuestionPoolService",
        lambda _db: pool,
    )

    result = await svc.fill_shared_booklet_from_bank(booklet)
    assert added == []
    assert result.status == "pending"
    assert result.requested_count == 0
    assert pool.serve_unused_for_topic.await_count >= 1


@pytest.mark.asyncio
async def test_booklet_fill_does_not_write_fail_cards(monkeypatch) -> None:
    from app.services.assessment_service import AssessmentService
    from app.services.qie.types import QualityBreakdown, QuestionCard

    plan = _plan()
    good = QuestionCard(
        stem=VALID_MATH["stem"],
        choices=dict(VALID_MATH["choices"]),
        correct_key=VALID_MATH["correct_key"],
        explanation=VALID_MATH.get("explanation"),
        plan=plan,
        difficulty_score=80,
        quality=QualityBreakdown(),
        correctness_meta={"version": CORRECTNESS_VERSION, "verdict": "pass"},
    )
    booklet = SimpleNamespace(
        id=uuid.uuid4(),
        exam_type="lgs",
        branch_key="sayisal",
        difficulty="medium",
        section_plan={
            "sections": [
                {
                    "subject_code": "lgs_matematik",
                    "topics": [{"topic_code": "geometri", "count": 2}],
                }
            ]
        },
        requested_count=0,
        generation_progress=0,
        status="pending",
        error_message=None,
        questions=[],
    )
    added: list[object] = []
    db = SimpleNamespace(
        execute=AsyncMock(),
        flush=AsyncMock(),
        add=lambda obj: added.append(obj),
    )
    svc = AssessmentService(db)
    svc.repo = SimpleNamespace(get_shared_booklet_by_id=AsyncMock(return_value=booklet))

    async def fake_serve(*, pool_type: str, **_k):
        if pool_type == "trial":
            return [good]
        return []

    pool = SimpleNamespace(serve_unused_for_topic=AsyncMock(side_effect=fake_serve))
    monkeypatch.setattr(
        "app.services.ai_cost.pool.QuestionPoolService",
        lambda _db: pool,
    )
    result = await svc.fill_shared_booklet_from_bank(booklet)
    assert result.status == "ready"
    assert len(added) == 1
    assert added[0].stem == VALID_MATH["stem"]
    assert added[0].correct_key == "B"
