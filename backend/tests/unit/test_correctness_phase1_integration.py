"""Phase 1 production-path integration: correctness + M34 + pool serve."""

from __future__ import annotations

import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.providers.ai.base import GenerateResult
from app.services.correctness.constants import CORRECTNESS_VERSION
from app.services.correctness.gate import run_correctness_gate
from app.services.qie.types import (
    GenerateContext,
    QualityBreakdown,
    QuestionCard,
    QuestionPlan,
)
from tests.unit.test_correctness_gate import LGS_Q5, TURKCE_PARAGRAF, VALID_MATH


def _plan(**kwargs) -> QuestionPlan:
    base = dict(
        exam="ayt_sayisal",
        subject_code="ayt_matematik",
        subject_name="Matematik",
        topic_code="turev",
        topic_name="Türev",
        skill="apply",
        index=0,
        choice_count=5,
        difficulty=70,
        paragraph_length=40,
    )
    base.update(kwargs)
    return QuestionPlan(**base)


def _ctx(plan: QuestionPlan) -> GenerateContext:
    return GenerateContext(
        exam=plan.exam,
        subject_code=plan.subject_code,
        subject_name=plan.subject_name,
        topic_code=plan.topic_code,
        topic_name=plan.topic_name,
        count=1,
        difficulty_band="medium",
        pool_type="general",
        kind="batch_generate",
    )


def _quality() -> QualityBreakdown:
    return QualityBreakdown(
        style=90,
        difficulty=90,
        similarity=90,
        grammar=90,
        option_balance=90,
        distractor_quality=90,
        blueprint_match=90,
        reading_time=90,
        exam_feel=90,
    )


def _m34_pass(q, *a, **k):
    return {
        "accepted": True,
        "question": {
            "stem": q.get("stem"),
            "choices": dict(q.get("choices") or {}),
            "correct_key": q.get("correct_key"),
            "explanation": q.get("explanation"),
        },
        "reject_reason": None,
    }


def _m34_fail(q, *a, **k):
    return {"accepted": False, "question": q, "reject_reason": "blueprint_low:test"}


def _patch_downstream_gates(monkeypatch, module: str) -> None:
    monkeypatch.setattr(
        f"{module}.analyze_for_plan",
        lambda *a, **k: SimpleNamespace(score=80, reasons=[]),
    )
    monkeypatch.setattr(f"{module}.score_quality", lambda *a, **k: _quality())
    monkeypatch.setattr(f"{module}.passes_quality_gate", lambda *_a, **_k: True)
    monkeypatch.setattr(f"{module}.is_similar_question", lambda *a, **k: False)


def _patch_measurement_off(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.ai.measurement_integration.load_contract_for_context",
        lambda **_k: None,
    )
    monkeypatch.setattr(
        "app.services.ai.measurement_integration.prompt_block_from_contract",
        lambda _c: "",
    )
    monkeypatch.setattr(
        "app.services.ai.measurement_integration.inject_measurement_into_style",
        lambda dna, _c: dna or {},
    )
    monkeypatch.setattr(
        "app.services.ai_cost.measurement_flags.measurement_soft_review",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.services.ai_cost.measurement_flags.measurement_mode",
        lambda: "off",
    )
    monkeypatch.setattr(
        "app.services.ai_cost.measurement_flags.measurement_enabled",
        lambda: False,
    )


async def _run_batch(monkeypatch, question: dict, *, m34, plan: QuestionPlan | None = None):
    from app.services.ai_cost.batch_generate import generate_batch_one_call

    plan = plan or _plan()
    _patch_measurement_off(monkeypatch)
    _patch_downstream_gates(monkeypatch, "app.services.ai_cost.batch_generate")

    class FakeStyle:
        def __init__(self, _db):
            pass

        async def dna(self, *a, **k):
            return {"choice_count": 5}

    payload = json.dumps({"questions": [{**question, "plan_index": 0}]})

    async def fake_gen(_req, **_k):
        return GenerateResult(text=payload, provider="test", model="m")

    monkeypatch.setattr("app.services.ai_cost.batch_generate.StyleIntelligence", FakeStyle)
    monkeypatch.setattr(
        "app.services.ai_cost.batch_generate.QuestionPlanner.plan_batch",
        lambda self, ctx, style=None: [plan],
    )
    monkeypatch.setattr("app.services.ai_cost.batch_generate.generate_with_fallback", fake_gen)
    monkeypatch.setattr(
        "app.services.question_intelligence.pipeline.evaluate_question",
        m34,
    )
    cards, _fp, _res = await generate_batch_one_call(MagicMock(), _ctx(plan), count=1)
    return cards


def _orch_pool(monkeypatch, *, unused=None, put=None):
    from app.services.ai_cost import pool as pool_mod

    put = put or AsyncMock()
    unused = unused if unused is not None else []
    pool = SimpleNamespace(
        get_unused_for_topic=AsyncMock(return_value=unused),
        try_serve_row=AsyncMock(return_value=None),
        put_card=put,
        mark_used=AsyncMock(),
        mark_quarantined=AsyncMock(),
        update_correctness_metadata=AsyncMock(),
        to_question_card=MagicMock(),
    )
    monkeypatch.setattr(pool_mod, "QuestionPoolService", lambda _db: pool)
    return pool


def _patch_orch_common(monkeypatch, plan: QuestionPlan) -> None:
    _patch_measurement_off(monkeypatch)
    _patch_downstream_gates(monkeypatch, "app.services.qie.orchestrator")
    monkeypatch.setattr("app.services.ai_cost.flags.pool_only_mode", lambda: False)
    monkeypatch.setattr("app.services.ai_cost.flags.compact_author_enabled", lambda: True)

    async def _dedup_do(_key, fn):
        return await fn()

    monkeypatch.setattr(
        "app.services.ai_cost.dedup.get_deduplicator",
        lambda: SimpleNamespace(do=_dedup_do),
    )
    async def _no_llm(*_a, **_k):
        raise AssertionError("LLM must not be called in PI orchestrator tests")

    monkeypatch.setattr("app.providers.ai.base.generate_with_fallback", _no_llm)
    monkeypatch.setattr("app.services.qie.orchestrator.generate_with_fallback", _no_llm)


def _authored(question: dict, plan: QuestionPlan):
    from app.services.question_author.types import AuthoredQuestion, AuthorPlan

    return AuthoredQuestion(
        stem=question["stem"],
        choices=dict(question["choices"]),
        correct_key=question["correct_key"],
        explanation=question.get("explanation"),
        author_plan=AuthorPlan(
            measured_outcome="x",
            reasoning_type="inference",
            distractor_type="x",
            paragraph_length=40,
            option_strategy="x",
            bloom_level="apply",
            difficulty_target=70,
            reading_duration_sec=60,
            trap_type="x",
            qie_plan_index=plan.index,
        ),
        provider="test",
        model="m",
    )


async def _run_orch_fresh(monkeypatch, question: dict, *, m34, plan: QuestionPlan | None = None):
    from app.services.qie.orchestrator import QieOrchestrator

    plan = plan or _plan()
    _patch_orch_common(monkeypatch, plan)
    put = AsyncMock()
    pool = _orch_pool(monkeypatch, unused=[], put=put)

    async def fake_author(*_a, **_k):
        return [_authored(question, plan)]

    monkeypatch.setattr(
        "app.services.ai_cost.compact_author.author_batch_compact",
        fake_author,
    )
    monkeypatch.setattr(
        "app.services.question_review.QuestionReviewEngine.review",
        lambda self, *a, **k: SimpleNamespace(passed=True, internal_metadata=lambda: {}),
    )
    monkeypatch.setattr(
        "app.services.question_virtual_student.VirtualStudentEngine.simulate",
        lambda self, *a, **k: SimpleNamespace(passed=True, internal_metadata=lambda: {}),
    )
    monkeypatch.setattr(
        "app.services.question_intelligence.pipeline.evaluate_question",
        m34,
    )

    orch = QieOrchestrator(MagicMock())
    orch.style = SimpleNamespace(dna=AsyncMock(return_value={"choice_count": 5}))
    orch.planner = SimpleNamespace(plan_batch=lambda _ctx, style=None: [plan])
    orch._generate_via_author = AsyncMock(return_value=([], "fp-author", None))
    orch._generate_via_legacy_llm = AsyncMock(return_value=([], "fp-legacy", None))
    cards, _fp, _res = await orch.generate_batch(_ctx(plan))
    return cards, pool


# ── PI-01 / PI-02 / PI-09 / PI-10 / PI-11 batch ─────────────────────


@pytest.mark.asyncio
async def test_pi01_batch_equivalent_options_rejected_no_pool_write(monkeypatch) -> None:
    m34_calls: list[dict] = []

    def m34(q, *a, **k):
        m34_calls.append(q)
        return _m34_pass(q)

    cards = await _run_batch(monkeypatch, LGS_Q5, m34=m34)
    assert cards == []
    assert m34_calls == []


@pytest.mark.asyncio
async def test_pi02_batch_valid_numeric_accepted(monkeypatch) -> None:
    cards = await _run_batch(monkeypatch, VALID_MATH, m34=_m34_pass)
    assert len(cards) == 1
    assert cards[0].correct_key == "B"
    assert cards[0].correctness_meta is not None
    assert cards[0].correctness_meta["verdict"] == "pass"
    assert cards[0].correctness_meta["version"] == CORRECTNESS_VERSION


@pytest.mark.asyncio
async def test_pi09_batch_m34_reject(monkeypatch) -> None:
    cards = await _run_batch(monkeypatch, VALID_MATH, m34=_m34_fail)
    assert cards == []


@pytest.mark.asyncio
async def test_pi10_m34_pass_correctness_fail_after_repair(monkeypatch) -> None:
    def m34_repairs_to_equivalent(q, *a, **k):
        return {"accepted": True, "question": dict(LGS_Q5), "reject_reason": None}

    cards = await _run_batch(monkeypatch, VALID_MATH, m34=m34_repairs_to_equivalent)
    assert cards == []


@pytest.mark.asyncio
async def test_pi11_correctness_pass_m34_fail_no_pool_write(monkeypatch) -> None:
    cards = await _run_batch(monkeypatch, VALID_MATH, m34=_m34_fail)
    assert cards == []


# ── PI-03 / PI-04 / PI-12 orchestrator fresh ────────────────────────


@pytest.mark.asyncio
async def test_pi03_orchestrator_fresh_equivalent_options_reject(monkeypatch) -> None:
    cards, pool = await _run_orch_fresh(monkeypatch, LGS_Q5, m34=_m34_pass)
    assert cards == []
    pool.put_card.assert_not_called()


@pytest.mark.asyncio
async def test_pi04_orchestrator_fresh_valid_accepted(monkeypatch) -> None:
    cards, pool = await _run_orch_fresh(monkeypatch, VALID_MATH, m34=_m34_pass)
    assert len(cards) == 1
    assert cards[0].correctness_meta["verdict"] == "pass"
    pool.put_card.assert_awaited()


@pytest.mark.asyncio
async def test_pi12_only_final_accepted_card_put_to_pool(monkeypatch) -> None:
    cards, pool = await _run_orch_fresh(monkeypatch, VALID_MATH, m34=_m34_pass)
    assert len(cards) == 1
    assert pool.put_card.await_count == 1
    kwargs = pool.put_card.await_args.kwargs
    assert kwargs["card"] is cards[0]
    assert kwargs["card"].correctness_meta["verdict"] == "pass"

    cards_fail, pool_fail = await _run_orch_fresh(monkeypatch, LGS_Q5, m34=_m34_pass)
    assert cards_fail == []
    pool_fail.put_card.assert_not_called()


# ── PI-05 / PI-06 / PI-07 / PI-08 pool serve ────────────────────────


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


@pytest.mark.asyncio
async def test_pi05_pool_pass_metadata_skips_recheck(monkeypatch) -> None:
    from app.services.ai_cost.pool import QuestionPoolService

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

    pool = QuestionPoolService(MagicMock())
    pool.update_correctness_metadata = AsyncMock()
    pool.mark_quarantined = AsyncMock()
    card = await pool.try_serve_row(row, plan)
    assert card is not None
    assert card.correct_key == "B"
    assert calls == []
    pool.mark_quarantined.assert_not_called()


@pytest.mark.asyncio
async def test_pi06_pool_legacy_equivalent_options_quarantine(monkeypatch) -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan()
    row = _pool_row(LGS_Q5, qie_card={}, plan=plan)
    pool = QuestionPoolService(MagicMock())
    pool.update_correctness_metadata = AsyncMock()
    pool.mark_quarantined = AsyncMock()
    card = await pool.try_serve_row(row, plan)
    assert card is None
    pool.mark_quarantined.assert_awaited()


@pytest.mark.asyncio
async def test_pi06_orchestrator_legacy_fail_falls_back_without_mark_used(monkeypatch) -> None:
    from app.services.qie.orchestrator import QieOrchestrator

    plan = _plan()
    _patch_orch_common(monkeypatch, plan)
    row = _pool_row(LGS_Q5, qie_card={}, plan=plan)
    put = AsyncMock()
    pool = SimpleNamespace(
        get_unused_for_topic=AsyncMock(return_value=[row]),
        try_serve_row=AsyncMock(return_value=None),
        put_card=put,
        mark_used=AsyncMock(),
    )
    monkeypatch.setattr("app.services.ai_cost.pool.QuestionPoolService", lambda _db: pool)
    monkeypatch.setattr(
        "app.services.ai_cost.compact_author.author_batch_compact",
        AsyncMock(return_value=[]),
    )

    orch = QieOrchestrator(MagicMock(), use_question_author=True)
    orch.style = SimpleNamespace(dna=AsyncMock(return_value={}))
    orch.planner = SimpleNamespace(plan_batch=lambda _ctx, style=None: [plan])
    orch._generate_via_author = AsyncMock(return_value=([], "fp", None))
    orch._generate_via_legacy_llm = AsyncMock(return_value=([], "fp", None))

    cards, _fp, _res = await orch.generate_batch(_ctx(plan))
    assert cards == []
    pool.mark_used.assert_not_called()
    put.assert_not_called()


@pytest.mark.asyncio
async def test_pi07_pool_legacy_valid_served(monkeypatch) -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan()
    row = _pool_row(VALID_MATH, qie_card={}, plan=plan)
    pool = QuestionPoolService(MagicMock())
    pool.update_correctness_metadata = AsyncMock()
    pool.mark_quarantined = AsyncMock()
    card = await pool.try_serve_row(row, plan)
    assert card is not None
    assert card.correct_key == "B"
    assert card.correctness_meta["verdict"] == "pass"
    pool.update_correctness_metadata.assert_awaited()
    pool.mark_quarantined.assert_not_called()


@pytest.mark.asyncio
async def test_pi08_unsupported_passthrough(monkeypatch) -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="paragraf",
        topic_name="Paragraf",
        skill="inference",
    )
    cards = await _run_batch(monkeypatch, TURKCE_PARAGRAF, m34=_m34_pass, plan=plan)
    assert len(cards) == 1
    assert cards[0].correctness_meta["verdict"] == "unsupported"

    row = _pool_row(TURKCE_PARAGRAF, qie_card={}, plan=plan)
    pool = QuestionPoolService(MagicMock())
    pool.update_correctness_metadata = AsyncMock()
    pool.mark_quarantined = AsyncMock()
    served = await pool.try_serve_row(row, plan)
    assert served is not None
    assert served.correctness_meta["verdict"] == "unsupported"
    pool.mark_quarantined.assert_not_called()


@pytest.mark.asyncio
async def test_put_card_refuses_correctness_fail() -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan()
    card = QuestionCard(
        stem=LGS_Q5["stem"],
        choices=dict(LGS_Q5["choices"]),
        correct_key=LGS_Q5["correct_key"],
        explanation=LGS_Q5.get("explanation"),
        plan=plan,
        difficulty_score=80,
        quality=_quality(),
        correctness_meta={"version": CORRECTNESS_VERSION, "verdict": "fail"},
    )
    pool = QuestionPoolService(MagicMock())
    with pytest.raises(ValueError, match="correctness_fail_not_pooled"):
        await pool.put_card(
            fingerprint="fp",
            card=card,
            exam=plan.exam,
            subject_code=plan.subject_code,
            topic_code=plan.topic_code,
            difficulty_band="medium",
        )
