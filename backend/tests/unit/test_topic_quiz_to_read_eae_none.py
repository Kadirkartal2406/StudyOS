"""Regression: _to_read / submit must tolerate qie_card.eae_interaction = None."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ValidationError
from app.schemas.topic_quiz import QuizGenerateRequest
from app.services.qie.types import QualityBreakdown, QuestionCard, QuestionPlan
from app.services.topic_quiz_service import (
    TopicQuizService,
    _resolve_item_asset_uri,
    _resolve_item_correct_node,
)


# ── helpers ──────────────────────────────────────────────────


def _item(**overrides) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "ord_index": 0,
        "stem": "Soru?",
        "choices": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        "eae_interaction": None,
        "qie_card": {},
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _gen(items: list) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        subject_code="matematik",
        topic_code="turev",
        subject_name="Matematik",
        topic_name="Türev",
        requested_count=len(items),
        difficulty="medium",
        exam_type="tyt",
        status="ready",
        provider="gemini",
        valid_item_count=len(items),
        correct_count=None,
        wrong_count=None,
        blank_count=None,
        error_message=None,
        created_at=datetime.now(UTC),
        items=items,
    )


# ── _resolve_item_asset_uri ─────────────────────────────────


class TestResolveItemAssetUri:
    def test_eae_key_none_falls_back_to_target_asset_id(self) -> None:
        it = _item(qie_card={"eae_interaction": None, "target_asset_id": "asset://map"})
        assert _resolve_item_asset_uri(it) == "asset://map"

    def test_eae_dict_uses_asset_uri(self) -> None:
        it = _item(
            qie_card={
                "eae_interaction": {"asset_uri": "asset://from-eae"},
                "target_asset_id": "asset://ignored",
            }
        )
        assert _resolve_item_asset_uri(it) == "asset://from-eae"

    def test_both_missing_returns_none(self) -> None:
        it = _item(qie_card={"eae_interaction": None, "target_asset_id": None})
        assert _resolve_item_asset_uri(it) is None

    def test_row_eae_interaction_wins(self) -> None:
        it = _item(
            eae_interaction={"asset_uri": "asset://row"},
            qie_card={
                "eae_interaction": {"asset_uri": "asset://qie"},
                "target_asset_id": "asset://target",
            },
        )
        assert _resolve_item_asset_uri(it) == "asset://row"

    def test_qie_card_none(self) -> None:
        it = _item(qie_card=None)
        assert _resolve_item_asset_uri(it) is None

    def test_empty_qie_card(self) -> None:
        it = _item(qie_card={})
        assert _resolve_item_asset_uri(it) is None

    def test_eae_key_missing_entirely(self) -> None:
        it = _item(qie_card={"target_asset_id": "asset://only-target"})
        assert _resolve_item_asset_uri(it) == "asset://only-target"


# ── _resolve_item_correct_node ───────────────────────────────


class TestResolveItemCorrectNode:
    def test_eae_key_none_falls_back_to_correct_node_id(self) -> None:
        it = _item(qie_card={"eae_interaction": None, "correct_node_id": "n1"})
        assert _resolve_item_correct_node(it) == "n1"

    def test_eae_dict_uses_expected_node_id(self) -> None:
        it = _item(
            qie_card={
                "eae_interaction": {"expected_node_id": "n2"},
                "correct_node_id": "n_ignored",
            }
        )
        assert _resolve_item_correct_node(it) == "n2"

    def test_row_eae_interaction_wins(self) -> None:
        it = _item(
            eae_interaction={"expected_node_id": "n_row"},
            qie_card={"eae_interaction": {"expected_node_id": "n_qie"}},
        )
        assert _resolve_item_correct_node(it) == "n_row"

    def test_qie_card_none(self) -> None:
        it = _item(qie_card=None)
        assert _resolve_item_correct_node(it) is None


# ── _to_read ─────────────────────────────────────────────────


class TestToRead:
    def test_does_not_crash_when_eae_interaction_key_is_none(self) -> None:
        svc = TopicQuizService(db=MagicMock())
        read = svc._to_read(
            _gen([_item(qie_card={"eae_interaction": None, "target_asset_id": None})])
        )
        assert len(read.items) == 1
        assert read.items[0].stem == "Soru?"

    def test_qie_card_none_does_not_crash(self) -> None:
        svc = TopicQuizService(db=MagicMock())
        read = svc._to_read(_gen([_item(qie_card=None)]))
        assert len(read.items) == 1

    def test_multiple_items_mixed(self) -> None:
        svc = TopicQuizService(db=MagicMock())
        items = [
            _item(ord_index=0, qie_card={"eae_interaction": None}),
            _item(
                ord_index=1,
                eae_interaction={"asset_uri": "a://row"},
                qie_card={"eae_interaction": {"asset_uri": "a://qie"}},
            ),
            _item(
                ord_index=2,
                qie_card={"eae_interaction": {"asset_uri": "a://eae"}, "target_asset_id": "a://t"},
            ),
        ]
        read = svc._to_read(_gen(items))
        assert len(read.items) == 3
        assert read.items[0].eae_interaction is None
        assert read.items[1].eae_interaction == {"asset_uri": "a://row"}
        assert read.items[2].eae_interaction is None


# ── generate e2e (mocked QIE) ────────────────────────────────


@pytest.mark.asyncio
async def test_generate_succeeds_with_eae_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production 400 scenario: QIE returns cards whose persist dict has eae_interaction=None."""
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
        eae_interaction=None,
        target_asset_id=None,
    )
    assert card.to_persist_dict()["eae_interaction"] is None

    added: list[object] = []

    class FakeDB:
        def add(self, obj: object) -> None:
            if getattr(obj, "id", None) is None:
                obj.id = uuid.uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = datetime.now(UTC)
            added.append(obj)

        async def flush(self) -> None:
            from app.models.topic_quiz import TopicQuizGeneration, TopicQuizItem

            gens = [o for o in added if isinstance(o, TopicQuizGeneration)]
            items = [o for o in added if isinstance(o, TopicQuizItem)]
            if gens:
                gens[0].items = sorted(items, key=lambda i: i.ord_index)

    db = FakeDB()
    svc = TopicQuizService(db)  # type: ignore[arg-type]
    svc.profile_repo.get_catalog_by_code = AsyncMock(return_value=None)
    svc.profile_repo.get_topic_by_code = AsyncMock(return_value=None)

    monkeypatch.setattr(
        "app.services.notification_settings_service.NotificationSettingsService.get_or_create",
        AsyncMock(
            return_value=SimpleNamespace(
                ai_preferred_provider=None,
                ai_preferred_model=None,
            )
        ),
    )

    class FakeOrch:
        def __init__(self, _db: object) -> None:
            pass

        async def generate_batch(self, _ctx: object) -> tuple:
            return [card], "fp", SimpleNamespace(provider="gemini", model="flash")

    monkeypatch.setattr("app.services.topic_quiz_service.QieOrchestrator", FakeOrch)

    async def _get(_user_id: uuid.UUID, _gid: uuid.UUID):
        from app.models.topic_quiz import TopicQuizGeneration

        gen = next(o for o in added if isinstance(o, TopicQuizGeneration))
        return svc._to_read(gen)

    monkeypatch.setattr(svc, "get", _get)

    read = await svc.generate(
        uuid.uuid4(), "matematik", "turev",
        QuizGenerateRequest(count=1, difficulty="medium", exam_type="tyt"),
    )
    assert read.valid_item_count == 1
    assert len(read.items) == 1
    assert read.items[0].stem == "2+2?"


@pytest.mark.asyncio
async def test_generate_empty_cards_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    added: list[object] = []

    class FakeDB:
        def add(self, obj: object) -> None:
            if getattr(obj, "id", None) is None:
                obj.id = uuid.uuid4()
            added.append(obj)

        async def flush(self) -> None:
            pass

    svc = TopicQuizService(FakeDB())  # type: ignore[arg-type]
    svc.profile_repo.get_catalog_by_code = AsyncMock(return_value=None)
    svc.profile_repo.get_topic_by_code = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.services.notification_settings_service.NotificationSettingsService.get_or_create",
        AsyncMock(
            return_value=SimpleNamespace(ai_preferred_provider=None, ai_preferred_model=None)
        ),
    )

    class FakeOrch:
        def __init__(self, _db: object) -> None:
            pass

        async def generate_batch(self, _ctx: object) -> tuple:
            return [], "fp", SimpleNamespace(provider="gemini", model="x")

    monkeypatch.setattr("app.services.topic_quiz_service.QieOrchestrator", FakeOrch)

    with pytest.raises(ValidationError, match="gerçek soru üretemedi"):
        await svc.generate(
            uuid.uuid4(), "matematik", "turev",
            QuizGenerateRequest(count=1, difficulty="medium", exam_type="tyt"),
        )
