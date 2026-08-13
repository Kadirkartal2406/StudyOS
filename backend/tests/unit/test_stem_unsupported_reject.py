"""STEM correctness UNSUPPORTED must not reach users; verbal pass-through kept."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.correctness.constants import requires_verified_correctness
from app.services.correctness.types import CorrectnessResult, CorrectnessVerdict
from app.services.qie.orchestrator import _correctness_or_reject
from app.services.qie.types import QuestionPlan


def _plan(**kwargs) -> QuestionPlan:
    return QuestionPlan(
        exam=kwargs.get("exam", "tyt"),
        subject_code=kwargs.get("subject_code", "tyt_matematik"),
        subject_name=kwargs.get("subject_name", "Matematik"),
        topic_code=kwargs.get("topic_code", "tyt_matematik__ucgenler"),
        topic_name=kwargs.get("topic_name", "Üçgenler"),
        skill=kwargs.get("skill", "triangles"),
        difficulty=kwargs.get("difficulty", 38),
        bloom="understand",
        stem_type=kwargs.get("stem_type", "calculation"),
        index=0,
        choice_count=5,
    )


def _item() -> ValidatedQuizItem:
    return ValidatedQuizItem(
        stem="Şekilde ABC üçgeninde açı ortay …",
        choices={"A": "40", "B": "50", "C": "60", "D": "70", "E": "80"},
        correct_key="B",
        explanation="…",
    )


def _corr(verdict: CorrectnessVerdict, *, passed: bool | None = None) -> CorrectnessResult:
    if passed is None:
        passed = verdict != CorrectnessVerdict.FAIL
    return CorrectnessResult(
        verdict=verdict,
        passed=passed,
        error_code=None,
        reason="test",
        checks=[],
        evidence={},
        correctness_version="correctness_v2",
    )


def test_requires_verified_correctness_tyt_ucgen():
    plan = _plan()
    assert requires_verified_correctness(plan=plan) is True


def test_requires_verified_correctness_turkce_false():
    plan = _plan(
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="tyt_turkce__paragraf",
        topic_name="Paragraf",
        skill="main_idea",
        stem_type="main_idea",
    )
    assert requires_verified_correctness(plan=plan) is False


def test_stem_pass_accepted():
    plan = _plan()
    with patch(
        "app.services.qie.orchestrator.evaluate_item_correctness",
        return_value=_corr(CorrectnessVerdict.PASS),
    ):
        assert _correctness_or_reject(_item(), plan) is not None


def test_stem_fail_rejected():
    plan = _plan()
    with patch(
        "app.services.qie.orchestrator.evaluate_item_correctness",
        return_value=_corr(CorrectnessVerdict.FAIL, passed=False),
    ):
        assert _correctness_or_reject(_item(), plan) is None


def test_stem_unsupported_rejected_tyt_ucgen_easy_regression():
    """Live-bug regression: TYT Üçgen easy + unsupported must NOT reach user."""
    plan = _plan(difficulty=34)
    # Gate still sets passed=True for unsupported — policy rejects in orchestrator.
    with patch(
        "app.services.qie.orchestrator.evaluate_item_correctness",
        return_value=_corr(CorrectnessVerdict.UNSUPPORTED, passed=True),
    ):
        assert _correctness_or_reject(_item(), plan) is None


def test_non_stem_unsupported_still_accepted():
    plan = _plan(
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="tyt_turkce__paragraf",
        topic_name="Paragraf",
        skill="main_idea",
        stem_type="main_idea",
    )
    with patch(
        "app.services.qie.orchestrator.evaluate_item_correctness",
        return_value=_corr(CorrectnessVerdict.UNSUPPORTED, passed=True),
    ):
        assert _correctness_or_reject(_item(), plan) is not None


@pytest.mark.asyncio
async def test_pool_serve_skips_stem_unsupported():
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan()
    row = SimpleNamespace(
        id="row1",
        exam="tyt",
        subject_code="tyt_matematik",
        topic_code="tyt_matematik__ucgenler",
        skill="triangles",
        stem="x",
        qie_card={},
    )
    pool = QuestionPoolService(MagicMock())
    pool.mark_quarantined = AsyncMock()
    pool.update_correctness_metadata = AsyncMock()
    pool.to_question_card = MagicMock()
    with (
        patch(
            "app.services.correctness.apply.pool_row_is_quarantined",
            return_value=False,
        ),
        patch(
            "app.services.correctness.apply.pool_row_can_skip_recheck",
            return_value=False,
        ),
        patch(
            "app.services.qie.skill_profiles.pool_row_compatible",
            return_value=True,
        ),
        patch(
            "app.services.correctness.apply.evaluate_pool_row_correctness",
            return_value=_corr(CorrectnessVerdict.UNSUPPORTED, passed=True),
        ),
    ):
        served = await pool.try_serve_row(row, plan)
    assert served is None
    pool.update_correctness_metadata.assert_not_awaited()


@pytest.mark.asyncio
async def test_compact_json_fail_retries_once():
    from app.providers.ai.base import GenerateResult
    from app.services.ai_cost import compact_author as mod
    from app.services.question_author.types import AuthorPlan

    plan = _plan()
    ap = AuthorPlan(
        measured_outcome="triangles",
        reasoning_type="calculation",
        distractor_type="near_miss",
        paragraph_length=40,
        option_strategy="tight",
        bloom_level="understand",
        difficulty_target=38,
        reading_duration_sec=45,
        trap_type="yakin",
        exam=plan.exam,
        subject_code=plan.subject_code,
        topic_code=plan.topic_code,
        topic_name=plan.topic_name,
        choice_count=5,
        qie_plan_index=0,
    )
    good = (
        '{"stem":"2+2=?","choices":{"A":"1","B":"2","C":"3","D":"4","E":"5"},'
        '"correct_key":"D","explanation":"2+2=4"}'
    )
    calls = {"n": 0}

    async def fake_gen(*_a, **_k):
        calls["n"] += 1
        if calls["n"] == 1:
            return GenerateResult(text="NOT JSON {{{", provider="gemini", model="x")
        return GenerateResult(text=good, provider="gemini", model="x")

    with (
        patch.object(mod, "build_author_plan", AsyncMock(return_value=ap)),
        patch.object(mod, "generate_with_fallback", side_effect=fake_gen),
    ):
        q = await mod.author_one_compact(plan)
    assert calls["n"] == 2
    assert q.stem.startswith("2+2")
    assert q.correct_key == "D"


@pytest.mark.asyncio
async def test_compact_json_fail_twice_raises():
    from app.providers.ai.base import GenerateResult
    from app.services.ai_cost import compact_author as mod
    from app.services.question_author.types import AuthorPlan

    plan = _plan()
    ap = AuthorPlan(
        measured_outcome="triangles",
        reasoning_type="calculation",
        distractor_type="near_miss",
        paragraph_length=40,
        option_strategy="tight",
        bloom_level="understand",
        difficulty_target=38,
        reading_duration_sec=45,
        trap_type="yakin",
        exam=plan.exam,
        subject_code=plan.subject_code,
        topic_code=plan.topic_code,
        topic_name=plan.topic_name,
        choice_count=5,
        qie_plan_index=0,
    )

    async def always_bad(*_a, **_k):
        return GenerateResult(text="{{{", provider="gemini", model="x")

    with (
        patch.object(mod, "build_author_plan", AsyncMock(return_value=ap)),
        patch.object(mod, "generate_with_fallback", side_effect=always_bad),
    ):
        with pytest.raises(RuntimeError, match="unusable JSON"):
            await mod.author_one_compact(plan)
