"""Topic quiz generate — pool commit integrity and dedup."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ValidationError
from app.schemas.topic_quiz import QuizGenerateRequest
from app.services.deduplication_service import compute_stem_hash
from app.services.qie.types import GenerateContext, QuestionCard, QuestionPlan, QualityBreakdown
from app.services.topic_quiz_service import TopicQuizService


def _make_plan() -> QuestionPlan:
    return QuestionPlan(
        exam="kpss",
        subject_code="kpss_mat",
        subject_name="Matematik",
        topic_code="kpss_mat__temel",
        topic_name="Temel Kavramlar",
        skill="logic",
    )


def _make_card(stem: str = "3x - 7 = 11 ise x kaçtır?") -> QuestionCard:
    return QuestionCard(
        stem=stem,
        choices={"A": "6", "B": "7", "C": "8", "D": "9", "E": "10"},
        correct_key="A",
        explanation="x = 6",
        plan=_make_plan(),
        difficulty_score=80,
        quality=QualityBreakdown(),
    )


def _mock_db() -> MagicMock:
    db = MagicMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    )
    db.scalar = AsyncMock(return_value=0)
    return db


def _repo_and_ns_patches():
    ns_instance = MagicMock()
    ns_instance.get_or_create = AsyncMock(
        return_value=MagicMock(ai_preferred_provider=None, ai_preferred_model=None)
    )
    return (
        patch(
            "app.services.topic_quiz_service.NotificationSettingsService",
            return_value=ns_instance,
        ),
        patch(
            "app.repositories.learning_profile_repository.LearningProfileRepository.get_catalog_by_code",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "app.repositories.learning_profile_repository.LearningProfileRepository.get_topic_by_code",
            new=AsyncMock(return_value=None),
        ),
    )


@pytest.mark.asyncio
async def test_topic_quiz_generate_context_defers_pool_persist():
    """Topic quiz must not write to question_pool during QIE — only after READY."""
    captured_ctx: list[GenerateContext] = []
    user_id = uuid.uuid4()

    async def _capture_generate(_self, ctx: GenerateContext):
        captured_ctx.append(ctx)
        return [], "test-fp", None

    db = _mock_db()
    ns_patch, cat_patch, topic_patch = _repo_and_ns_patches()
    with patch(
        "app.services.topic_quiz_service.QieOrchestrator.generate_batch",
        new=_capture_generate,
    ):
        with ns_patch, cat_patch, topic_patch:
            with pytest.raises(ValidationError):
                await TopicQuizService(db).generate(
                    user_id,
                    "kpss_mat",
                    "kpss_mat__temel",
                    QuizGenerateRequest(count=5, difficulty="medium", exam_type="kpss"),
                )

    assert len(captured_ctx) == 1
    assert captured_ctx[0].persist_pool is False


@pytest.mark.asyncio
async def test_orchestrator_skips_pool_put_when_persist_pool_false():
    """QIE orchestrator respects ctx.persist_pool=False."""
    from app.services.qie.orchestrator import QieOrchestrator
    from app.services.qie.planner import QuestionPlanner

    ctx = GenerateContext(
        exam="kpss",
        subject_code="kpss_mat",
        subject_name="Matematik",
        topic_code="kpss_mat__temel",
        topic_name="Temel",
        count=1,
        difficulty_band="medium",
        persist_pool=False,
    )
    card = _make_card()
    db = _mock_db()

    with patch.object(
        QieOrchestrator,
        "_generate_via_legacy_llm",
        new=AsyncMock(return_value=([card], "fp-test", None)),
    ), patch(
        "app.services.qie.orchestrator.StyleIntelligence",
    ) as style_cls, patch.object(
        QuestionPlanner,
        "plan_batch",
        return_value=[_make_plan()],
    ), patch(
        "app.services.ai_cost.pool.QuestionPoolService.put_card",
        new=AsyncMock(),
    ) as put_mock, patch(
        "app.services.ai_cost.pool.QuestionPoolService.get_by_fingerprint",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.services.ai_cost.pool.QuestionPoolService.get_unused_for_topic",
        new=AsyncMock(return_value=[]),
    ), patch(
        "app.services.ai_cost.flags.compact_author_enabled",
        return_value=False,
    ), patch(
        "app.services.ai_cost.dedup.get_deduplicator",
    ) as dedup_mock:
        style_cls.return_value.dna = AsyncMock(return_value={"choice_count": 5})

        async def _run_dedup(_key, factory):
            return await factory()

        dedup_mock.return_value.do = AsyncMock(side_effect=_run_dedup)
        cards, _, _ = await QieOrchestrator(db, use_question_author=False).generate_batch(ctx)

    assert len(cards) == 1
    put_mock.assert_not_called()


def test_dedup_filter_clears_all_seen_cards():
    """When every QIE card was already seen, filter yields empty (triggers fallback)."""
    cards = [_make_card("Soru 1"), _make_card("Soru 2")]
    seen = {compute_stem_hash("Soru 1"), compute_stem_hash("Soru 2")}
    filtered = [c for c in cards if compute_stem_hash(c.stem) not in seen]
    assert filtered == []


@pytest.mark.asyncio
async def test_generate_validation_error_does_not_call_pool_persist():
    """Failed generation must not persist freshly authored cards to the pool."""
    user_id = uuid.uuid4()
    card = _make_card()
    db = _mock_db()

    async def _fake_batch(_self, ctx: GenerateContext):
        assert ctx.persist_pool is False
        return [card], "fp-test", None

    ns_patch, cat_patch, topic_patch = _repo_and_ns_patches()
    with patch(
        "app.services.topic_quiz_service.QieOrchestrator.generate_batch",
        new=_fake_batch,
    ):
        with patch(
            "app.services.deduplication_service.get_user_seen_stem_hashes",
            new=AsyncMock(return_value={compute_stem_hash(card.stem)}),
        ):
            with patch.object(
                TopicQuizService,
                "_persist_new_cards_to_pool",
                new=AsyncMock(),
            ) as persist_mock:
                with ns_patch, cat_patch, topic_patch:
                    with pytest.raises(ValidationError):
                        await TopicQuizService(db).generate(
                            user_id,
                            "kpss_mat",
                            "kpss_mat__temel",
                            QuizGenerateRequest(
                                count=5, difficulty="medium", exam_type="kpss"
                            ),
                        )

    persist_mock.assert_not_called()


@pytest.mark.asyncio
async def test_generate_success_persists_pool_cards():
    """Successful quiz generation writes freshly authored cards to the pool."""
    user_id = uuid.uuid4()
    card = _make_card("Yeni benzersiz soru metni?")
    db = _mock_db()

    async def _fake_batch(_self, ctx: GenerateContext):
        return [card], "fp-test", None

    gen = MagicMock()
    gen.id = uuid.uuid4()
    gen.items = []
    gen.subject_code = "kpss_mat"
    gen.topic_code = "kpss_mat__temel"
    gen.subject_name = "Matematik"
    gen.topic_name = "Temel"
    gen.requested_count = 1
    gen.difficulty = "medium"
    gen.exam_type = "kpss"
    gen.status = "ready"
    gen.provider = None
    gen.valid_item_count = 1
    gen.correct_count = None
    gen.wrong_count = None
    gen.blank_count = None
    gen.error_message = None
    gen.created_at = MagicMock()

    ns_patch, cat_patch, topic_patch = _repo_and_ns_patches()
    with patch(
        "app.services.topic_quiz_service.QieOrchestrator.generate_batch",
        new=_fake_batch,
    ):
        with patch(
            "app.services.deduplication_service.get_user_seen_stem_hashes",
            new=AsyncMock(return_value=set()),
        ):
            with patch.object(
                TopicQuizService,
                "_persist_new_cards_to_pool",
                new=AsyncMock(),
            ) as persist_mock:
                with patch.object(
                    TopicQuizService,
                    "get",
                    new=AsyncMock(
                        return_value=MagicMock(status="ready", valid_item_count=1)
                    ),
                ):
                    with ns_patch, cat_patch, topic_patch:
                        result = await TopicQuizService(db).generate(
                            user_id,
                            "kpss_mat",
                            "kpss_mat__temel",
                            QuizGenerateRequest(
                                count=1, difficulty="medium", exam_type="kpss"
                            ),
                        )

    persist_mock.assert_called_once()
    assert result.status == "ready"
    assert result.valid_item_count == 1
