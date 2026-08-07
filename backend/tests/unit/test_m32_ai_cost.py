"""M32 — production readiness / cost optimization unit tests."""

from __future__ import annotations

import asyncio

from app.core.config import settings
from app.providers.ai.gemini_provider import GeminiProvider
from app.services.ai_cost.budget import DailyAiBudget
from app.services.ai_cost.dedup import RequestDeduplicator
from app.services.ai_cost.flags import (
    auto_booklet_enabled,
    catchup_enabled,
    midnight_scheduler_enabled,
)
from app.services.ai_cost.metrics import AiCostMetrics
from app.services.ai_cost.pool import pool_fingerprint
from app.services.booklet_scheduler import midnight_booklet_loop


def test_m32_auto_ai_flags_default_off():
    assert settings.ENABLE_AUTO_BOOKLET is False
    assert settings.ENABLE_BACKGROUND_AI is False
    assert settings.ENABLE_MIDNIGHT_SCHEDULER is False
    assert settings.ENABLE_CATCHUP is False
    assert settings.ENABLE_AI_WARMUP is False
    assert midnight_scheduler_enabled() is False
    assert catchup_enabled() is False
    assert auto_booklet_enabled() is False


def test_m32_gemini_fallback_limit_one():
    p = GeminiProvider(model="gemini-flash-latest")
    models = p._candidate_models()
    assert len(models) <= 1 + max(0, int(settings.AI_GEMINI_MAX_FALLBACKS))
    assert models[0] == "gemini-flash-latest"


def test_m32_pool_fingerprint_stable():
    a = pool_fingerprint(
        exam="kpss",
        subject_code="kpss_mat",
        topic_code="kpss_mat__temel",
        difficulty_band="medium",
        skill="logic",
        index=0,
    )
    b = pool_fingerprint(
        exam="KPSS",
        subject_code="kpss_mat",
        topic_code="kpss_mat__temel",
        difficulty_band="medium",
        skill="logic",
        index=0,
    )
    c = pool_fingerprint(
        exam="kpss",
        subject_code="kpss_mat",
        topic_code="kpss_mat__temel",
        difficulty_band="hard",
        skill="logic",
        index=0,
    )
    assert a == b
    assert a != c


def test_m32_fingerprint_for_card_differs_by_content():
    """Same plan index + different stems must not collide (pool fill bug)."""
    from app.services.ai_cost.pool import fingerprint_for_card, fingerprint_for_plan
    from app.services.qie.types import GenerateContext, QualityBreakdown, QuestionCard, QuestionPlan

    ctx = GenerateContext(
        exam="yks",
        subject_code="tyt_matematik",
        subject_name="Matematik",
        topic_code="tyt_matematik__temel_kavramlar",
        topic_name="Temel Kavramlar",
        count=10,
        difficulty_band="medium",
    )
    plan = QuestionPlan(
        exam="yks",
        subject_code="tyt_matematik",
        subject_name="Matematik",
        topic_code="tyt_matematik__temel_kavramlar",
        topic_name="Temel Kavramlar",
        skill="logic",
        bloom="apply",
        stem_type="mcq",
        choice_count=5,
        index=0,
        difficulty=70,
    )
    q = QualityBreakdown()
    c1 = QuestionCard(
        stem="Soru A nedir?",
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="A",
        explanation=None,
        plan=plan,
        difficulty_score=70,
        quality=q,
    )
    c2 = QuestionCard(
        stem="Soru B nedir?",
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="B",
        explanation=None,
        plan=plan,
        difficulty_score=70,
        quality=q,
    )
    assert fingerprint_for_plan(c1.plan, ctx) == fingerprint_for_plan(c2.plan, ctx)
    assert fingerprint_for_card(c1, ctx) != fingerprint_for_card(c2, ctx)


def test_m32_request_dedup_single_flight():
    dedup = RequestDeduplicator()
    calls = {"n": 0}

    async def factory():
        calls["n"] += 1
        await asyncio.sleep(0.05)
        return "ok"

    async def run():
        results = await asyncio.gather(
            dedup.do("k1", factory),
            dedup.do("k1", factory),
            dedup.do("k1", factory),
        )
        return results

    out = asyncio.run(run())
    assert out == ["ok", "ok", "ok"]
    assert calls["n"] == 1


def test_m32_metrics_cache_pct():
    m = AiCostMetrics()
    m.record_pool_hit()
    m.record_pool_hit()
    m.record_pool_miss()
    snap = m.snapshot()
    assert snap["pool_hits"] == 2
    assert snap["cache_hit_pct"] == round(100.0 * 2 / 3, 2)


def test_m32_budget_limit_config():
    assert settings.AI_DAILY_REQUEST_BUDGET == 1000
    b = DailyAiBudget()
    assert b.limit == 1000
    assert b.remaining() >= 0


def test_m32_scheduler_exits_when_disabled():
    async def run():
        await midnight_booklet_loop()

    asyncio.run(run())  # should return immediately


def test_m32_null_provider_blocks_author_kinds():
    from app.core.exceptions import AIUnavailableError
    from app.providers.ai.base import ChatMessageDTO, GenerateRequest, NullAIProvider

    async def run():
        n = NullAIProvider()
        try:
            await n.generate(
                GenerateRequest(
                    messages=[ChatMessageDTO(role="user", content="x")],
                    context={"kind": "author_writer"},
                )
            )
            return False
        except AIUnavailableError:
            return True

    assert asyncio.run(run()) is True
