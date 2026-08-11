"""QIE pool put must match QuestionPoolService.put_card signature."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.qie.types import (
    GenerateContext,
    QualityBreakdown,
    QuestionCard,
    QuestionPlan,
)


@pytest.mark.asyncio
async def test_generate_batch_pool_put_passes_required_kwargs(monkeypatch) -> None:
    from app.services.ai_cost import pool as pool_mod
    from app.services.qie.orchestrator import QieOrchestrator

    plan = QuestionPlan(
        exam="tyt",
        subject_code="matematik",
        subject_name="Matematik",
        topic_code="turev",
        topic_name="Türev",
        skill="apply",
        index=0,
    )
    card = QuestionCard(
        stem="2+2?",
        choices={"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
        correct_key="B",
        explanation="4",
        plan=plan,
        difficulty_score=70,
        quality=QualityBreakdown(),
    )
    ctx = GenerateContext(
        exam="tyt",
        subject_code="matematik",
        subject_name="Matematik",
        topic_code="turev",
        topic_name="Türev",
        count=1,
        difficulty_band="medium",
        pool_type="general",
    )

    put = AsyncMock()
    pool = SimpleNamespace(
        get_unused_for_topic=AsyncMock(return_value=[]),
        put_card=put,
        mark_used=AsyncMock(),
    )
    monkeypatch.setattr(pool_mod, "QuestionPoolService", lambda _db: pool)

    async def _dedup_do(_key, fn):
        return await fn()

    monkeypatch.setattr(
        "app.services.ai_cost.dedup.get_deduplicator",
        lambda: SimpleNamespace(do=_dedup_do),
    )
    monkeypatch.setattr(
        "app.services.ai_cost.flags.pool_only_mode",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.services.ai_cost.flags.compact_author_enabled",
        lambda: False,
    )
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
        lambda dna, _c: dna,
    )
    monkeypatch.setattr(
        "app.services.ai_cost.measurement_flags.measurement_soft_review",
        lambda: False,
    )

    orch = QieOrchestrator(MagicMock())
    orch.style = SimpleNamespace(dna=AsyncMock(return_value={}))
    orch.planner = SimpleNamespace(plan_batch=lambda _ctx, style=None: [plan])
    orch.use_question_author = False
    orch._generate_via_legacy_llm = AsyncMock(
        return_value=([card], "fp-legacy", None)
    )

    cards, _, _ = await orch.generate_batch(ctx)
    assert len(cards) == 1
    put.assert_awaited()
    kwargs = put.await_args.kwargs
    for key in (
        "fingerprint",
        "card",
        "exam",
        "subject_code",
        "topic_code",
        "difficulty_band",
        "pool_type",
    ):
        assert key in kwargs, f"missing put_card kwarg: {key}"
    assert "ctx" not in kwargs
    assert kwargs["exam"] == "tyt"
    assert kwargs["topic_code"] == "turev"
    assert kwargs["pool_type"] == "general"


def test_put_card_signature_has_no_ctx_kwarg() -> None:
    import inspect

    from app.services.ai_cost.pool import QuestionPoolService

    params = inspect.signature(QuestionPoolService.put_card).parameters
    assert "ctx" not in params
    assert "fingerprint" in params
