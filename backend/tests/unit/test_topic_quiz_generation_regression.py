"""Topic quiz generation: new vs replay, pool domain, stem exclude."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.constants import TOPIC_QUIZ_DEFAULT_COUNT
from app.core.exceptions import ValidationError
from app.schemas.topic_quiz import QuizGenerateRequest
from app.services.correctness.constants import CORRECTNESS_VERSION
from app.services.qie.planner import QuestionPlanner
from app.services.qie.skill_profiles import (
    LANGUAGE_FORM_SKILLS,
    pool_card_compatible,
    resolve_domain,
)
from app.services.qie.types import (
    GenerateContext,
    QualityBreakdown,
    QuestionCard,
    QuestionPlan,
)
from app.services.topic_quiz_service import TopicQuizService


def _plan(**kwargs) -> QuestionPlan:
    base = dict(
        exam="kpss",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__osmanli",
        topic_name="Osmanlı",
        skill="chronology",
        stem_type="factual_recall",
        index=0,
        choice_count=5,
        difficulty=70,
    )
    base.update(kwargs)
    return QuestionPlan(**base)


def _card(plan: QuestionPlan, stem: str = "Osmanlı'da tımar sistemi nedir?") -> QuestionCard:
    return QuestionCard(
        stem=stem,
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="A",
        explanation="açıklama",
        plan=plan,
        difficulty_score=70,
        quality=QualityBreakdown(),
    )


def _pass_qie(*, skill: str, stem_type: str = "factual_recall") -> dict:
    return {
        "skill": skill,
        "stem_type": stem_type,
        "correctness": {"version": CORRECTNESS_VERSION, "verdict": "pass"},
    }


def _pool_row(*, skill: str, stem: str, stem_type: str = "factual_recall", **kwargs):
    plan = kwargs.pop("plan", None) or _plan(skill=skill, stem_type=stem_type)
    return SimpleNamespace(
        id=uuid.uuid4(),
        stem=stem,
        choices={"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        correct_key="A",
        explanation="x",
        qie_card=_pass_qie(skill=skill, stem_type=stem_type),
        exam=plan.exam,
        subject_code=plan.subject_code,
        topic_code=plan.topic_code,
        difficulty_band="medium",
        skill=skill,
        use_count=0,
        created_at=datetime.now(UTC),
    )


class _TrackingDB:
    def __init__(self, recent_stems: list[str] | None = None) -> None:
        self.added: list[object] = []
        self.recent_stems = list(recent_stems or [])

    def add(self, obj: object) -> None:
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        self.added.append(obj)

    async def flush(self) -> None:
        from app.models.topic_quiz import TopicQuizGeneration, TopicQuizItem

        gens = [o for o in self.added if isinstance(o, TopicQuizGeneration)]
        items = [o for o in self.added if isinstance(o, TopicQuizItem)]
        for g in gens:
            g.items = sorted(
                [i for i in items if i.generation_id == g.id],
                key=lambda i: i.ord_index,
            )

    async def execute(self, _stmt: object) -> object:
        return SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: list(self.recent_stems))
        )


def _patch_generate(monkeypatch: pytest.MonkeyPatch, svc: TopicQuizService, cards_fn):
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
    captured: dict[str, object] = {}

    class FakeOrch:
        def __init__(self, _db: object) -> None:
            pass

        async def generate_batch(self, ctx: object) -> tuple:
            captured["ctx"] = ctx
            cards = cards_fn(ctx)
            return cards, "fp", SimpleNamespace(provider="gemini", model="flash")

    monkeypatch.setattr("app.services.topic_quiz_service.QieOrchestrator", FakeOrch)

    async def _get(user_id: uuid.UUID, gid: uuid.UUID):
        from app.models.topic_quiz import TopicQuizGeneration

        gen = next(
            o
            for o in svc.db.added  # type: ignore[attr-defined]
            if isinstance(o, TopicQuizGeneration) and o.id == gid
        )
        return svc._to_read(gen)

    monkeypatch.setattr(svc, "get", _get)
    return captured


# ── A / B: new quiz vs submitted ────────────────────────────────


@pytest.mark.asyncio
async def test_a_new_quiz_creates_new_generation_despite_submitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = _TrackingDB()
    svc = TopicQuizService(db)  # type: ignore[arg-type]
    n = {"i": 0}

    def cards_fn(_ctx: object) -> list[QuestionCard]:
        n["i"] += 1
        return [_card(_plan(), stem=f"Yeni soru {n['i']}?")]

    _patch_generate(monkeypatch, svc, cards_fn)
    user = uuid.uuid4()
    req = QuizGenerateRequest(count=1, difficulty="medium", exam_type="kpss")
    first = await svc.generate(user, "kpss_tarih", "kpss_tarih__osmanli", req)
    # Pretend first quiz was submitted — generate must still open a new row.
    from app.models.topic_quiz import TopicQuizGeneration, QuizGenerationStatus

    first_gen = next(o for o in db.added if isinstance(o, TopicQuizGeneration) and o.id == first.id)
    first_gen.status = QuizGenerationStatus.SUBMITTED
    second = await svc.generate(user, "kpss_tarih", "kpss_tarih__osmanli", req)
    assert second.id != first.id
    assert second.status == "ready"
    assert first_gen.status == QuizGenerationStatus.SUBMITTED


@pytest.mark.asyncio
async def test_b_new_quiz_does_not_copy_old_topic_quiz_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = _TrackingDB()
    svc = TopicQuizService(db)  # type: ignore[arg-type]
    n = {"i": 0}

    def cards_fn(_ctx: object) -> list[QuestionCard]:
        n["i"] += 1
        return [_card(_plan(), stem=f"Benzersiz stem {n['i']}")]

    _patch_generate(monkeypatch, svc, cards_fn)
    user = uuid.uuid4()
    req = QuizGenerateRequest(count=1, difficulty="medium", exam_type="kpss")
    first = await svc.generate(user, "kpss_tarih", "kpss_tarih__osmanli", req)
    second = await svc.generate(user, "kpss_tarih", "kpss_tarih__osmanli", req)
    first_ids = {it.id for it in first.items}
    second_ids = {it.id for it in second.items}
    assert first_ids.isdisjoint(second_ids)
    assert first.items[0].stem != second.items[0].stem
    from app.models.topic_quiz import TopicQuizItem

    items = [o for o in db.added if isinstance(o, TopicQuizItem)]
    assert len(items) == 2
    assert items[0].generation_id != items[1].generation_id


# ── C / D: pool domain compatibility ────────────────────────────


@pytest.mark.asyncio
async def test_c_legacy_language_skill_not_served_to_non_language() -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan(skill="chronology")
    row = _pool_row(
        skill="spelling",
        stem="Hangisinde yazım yanlışı vardır?",
        stem_type="grammar",
        plan=plan,
    )
    pool = QuestionPoolService(MagicMock())
    served = await pool.try_serve_row(row, plan)
    assert served is None


@pytest.mark.asyncio
async def test_d_domain_compatible_pool_card_can_be_served() -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan(skill="chronology")
    row = _pool_row(
        skill="chronology",
        stem="Osmanlı'da tımar sistemi nedir?",
        stem_type="factual_recall",
        plan=plan,
    )
    pool = QuestionPoolService(MagicMock())
    served = await pool.try_serve_row(row, plan)
    assert served is not None
    assert served.stem == row.stem


@pytest.mark.asyncio
async def test_c_put_card_refuses_legacy_language_on_tarih() -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    pool = QuestionPoolService(MagicMock())
    card = _card(_plan(skill="spelling", stem_type="grammar"), stem="Yazım?")
    with pytest.raises(ValueError, match="domain_incompatible_not_pooled"):
        await pool.put_card(
            fingerprint="x",
            card=card,
            exam="kpss",
            subject_code="kpss_tarih",
            topic_code="kpss_tarih__osmanli",
            difficulty_band="medium",
            skill="spelling",
        )


# ── E: pool miss still generates ────────────────────────────────


@pytest.mark.asyncio
async def test_e_pool_miss_falls_back_to_generation(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.ai_cost import pool as pool_mod
    from app.services.qie.orchestrator import QieOrchestrator

    plan = _plan()
    card = _card(plan)
    ctx = GenerateContext(
        exam="kpss",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="kpss_tarih__osmanli",
        topic_name="Osmanlı",
        count=1,
        difficulty_band="medium",
    )
    pool = SimpleNamespace(
        get_unused_for_topic=AsyncMock(return_value=[]),
        put_card=AsyncMock(),
        mark_used=AsyncMock(),
        try_serve_row=AsyncMock(return_value=None),
    )
    monkeypatch.setattr(pool_mod, "QuestionPoolService", lambda _db: pool)

    async def _dedup_do(_key, fn):
        return await fn()

    monkeypatch.setattr(
        "app.services.ai_cost.dedup.get_deduplicator",
        lambda: SimpleNamespace(do=_dedup_do),
    )
    monkeypatch.setattr("app.services.ai_cost.flags.pool_only_mode", lambda: False)
    monkeypatch.setattr("app.services.ai_cost.flags.compact_author_enabled", lambda: False)
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
    orch._generate_via_legacy_llm = AsyncMock(return_value=([card], "fp-gen", None))

    cards, fp, _ = await orch.generate_batch(ctx)
    assert len(cards) == 1
    assert cards[0].stem == card.stem
    assert fp == "fp-gen"
    pool.get_unused_for_topic.assert_awaited()
    orch._generate_via_legacy_llm.assert_awaited()


# ── F: recent stems excluded; empty pool still generates ────────


@pytest.mark.asyncio
async def test_f_recent_stems_passed_as_exclude_and_empty_pool_generates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recent = "Daha önce gösterilen Osmanlı sorusu?"
    db = _TrackingDB(recent_stems=[recent])
    svc = TopicQuizService(db)  # type: ignore[arg-type]
    captured = _patch_generate(
        monkeypatch,
        svc,
        lambda ctx: [_card(_plan(), stem="Taze üretilmiş soru?")],
    )
    read = await svc.generate(
        uuid.uuid4(),
        "kpss_tarih",
        "kpss_tarih__osmanli",
        QuizGenerateRequest(count=1, difficulty="medium", exam_type="kpss"),
    )
    ctx = captured["ctx"]
    assert recent in ctx.existing_stems
    assert read.items[0].stem == "Taze üretilmiş soru?"
    assert read.items[0].stem != recent


@pytest.mark.asyncio
async def test_f_get_unused_excludes_recent_stems() -> None:
    from app.services.ai_cost.pool import QuestionPoolService
    from app.services.correctness.apply import pool_row_is_quarantined

    used = _pool_row(skill="chronology", stem="Eski stem")
    fresh = _pool_row(skill="chronology", stem="Yeni stem")
    result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [used, fresh]))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))
    pool = QuestionPoolService(db)  # type: ignore[arg-type]
    rows = await pool.get_unused_for_topic(
        exam="kpss",
        subject_code="kpss_tarih",
        topic_code="kpss_tarih__osmanli",
        difficulty_band="medium",
        exclude_stems=["Eski stem"],
        limit=10,
    )
    stems = [r.stem for r in rows]
    assert "Eski stem" not in stems
    assert "Yeni stem" in stems
    assert pool_row_is_quarantined(used) is False


# ── G: language domains keep legitimate skills ──────────────────


@pytest.mark.parametrize(
    ("exam", "subject", "topic", "skill", "ok"),
    [
        ("kpss", "kpss_turkce", "kpss_turkce__paragraf", "spelling", True),
        ("tyt", "tyt_turkce", "tyt_turkce__paragraf", "grammar", True),
        ("yds", "yds_ingilizce", "yds_ingilizce__vocabulary", "vocabulary", True),
        ("ydt", "ydt_ingilizce", "ydt_ingilizce__reading", "grammar", True),
        ("yokdil", "yokdil_fen", "yokdil_fen__reading", "cloze", True),
        ("ales", "ales_sozel", "ales_sozel__anlam", "main_idea", True),
        ("ales", "ales_sozel", "ales_sozel__anlam", "spelling", False),
        ("dgs", "dgs_sozel", "dgs_sozel__anlam", "sentence_meaning", True),
        ("ales", "ales_sayisal", "ales_sayisal__problemler", "vocabulary", False),
        ("dgs", "dgs_sayisal", "dgs_sayisal__problemler", "grammar", False),
        ("kpss", "kpss_tarih", "kpss_tarih__osmanli", "spelling", False),
        ("kpss", "kpss_cografya", "kpss_cografya__nufus", "grammar", False),
        ("kpss", "kpss_matematik", "kpss_matematik__temel", "vocabulary", False),
        ("kpss", "kpss_vatandaslik", "kpss_vatandaslik__anayasa", "paragraph_completion", False),
        ("tyt", "tyt_matematik", "tyt_matematik__temel", "spelling", False),
        ("ayt", "ayt_matematik", "ayt_matematik__fonksiyon", "grammar", False),
        ("ayt", "ayt_fizik", "ayt_fizik__mekanik", "vocabulary", False),
        ("lgs", "lgs_turkce", "lgs_turkce__paragraf", "main_idea", True),
        ("lgs", "lgs_matematik", "lgs_matematik__sayilar", "spelling", False),
        ("kpss", "kpss_guncel", "kpss_guncel__gundem", "grammar", False),
    ],
)
def test_g_pool_domain_matrix(exam: str, subject: str, topic: str, skill: str, ok: bool) -> None:
    assert (
        pool_card_compatible(
            exam=exam,
            subject_code=subject,
            topic_code=topic,
            skill=skill,
        )
        is ok
    )


def test_g_planner_language_domains_untouched() -> None:
    ctx = GenerateContext(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="tyt_turkce__paragraf",
        topic_name="Paragraf",
        count=5,
    )
    plans = QuestionPlanner().plan_batch(ctx, style={"choice_count": 5})
    assert {p.skill for p in plans} & LANGUAGE_FORM_SKILLS
    assert resolve_domain(exam="yds", subject_code="yds_ingilizce") == "english"


# ── H: LGS choice_count ─────────────────────────────────────────


def test_h_lgs_choice_count_remains_4() -> None:
    ctx = GenerateContext(
        exam="lgs",
        subject_code="lgs_matematik",
        subject_name="Matematik",
        topic_code="lgs_matematik__sayilar",
        topic_name="Sayılar",
        count=TOPIC_QUIZ_DEFAULT_COUNT,
    )
    plans = QuestionPlanner().plan_batch(ctx, style={"choice_count": 4})
    assert plans
    assert all(p.choice_count == 4 for p in plans)
    assert not ({p.skill for p in plans} & LANGUAGE_FORM_SKILLS)


@pytest.mark.asyncio
async def test_generate_refills_to_requested_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = _TrackingDB()
    svc = TopicQuizService(db)  # type: ignore[arg-type]
    n = {"i": 0}

    def split_fn(ctx: object) -> list[QuestionCard]:
        n["i"] += 1
        if n["i"] == 1:
            return [_card(_plan(), stem=f"Kısa {i}") for i in range(3)]
        need = int(getattr(ctx, "count", 2) or 2)
        return [_card(_plan(), stem=f"Dolgu {i}") for i in range(need)]

    _patch_generate(monkeypatch, svc, split_fn)
    read = await svc.generate(
        uuid.uuid4(),
        "kpss_tarih",
        "kpss_tarih__osmanli",
        QuizGenerateRequest(count=5, difficulty="medium", exam_type="kpss"),
    )
    assert len(read.items) == 5
    assert read.valid_item_count == 5
    assert n["i"] == 2


def test_quiz_default_count_is_authoritative() -> None:
    assert TOPIC_QUIZ_DEFAULT_COUNT == 5
    assert QuizGenerateRequest().count == TOPIC_QUIZ_DEFAULT_COUNT
    ctx = GenerateContext(
        exam="kpss",
        subject_code="kpss_tarih",
        subject_name="Tarih",
        topic_code="t",
        topic_name="T",
    )
    assert ctx.count == TOPIC_QUIZ_DEFAULT_COUNT


# ── I: correctness_v2 still applied on serve ────────────────────


@pytest.mark.asyncio
async def test_i_incompatible_card_is_not_quarantined() -> None:
    from app.services.ai_cost.pool import QuestionPoolService

    plan = _plan()
    row = _pool_row(
        skill="spelling",
        stem="Yazım?",
        stem_type="grammar",
        plan=plan,
    )
    pool = QuestionPoolService(MagicMock())
    pool.mark_quarantined = AsyncMock()
    served = await pool.try_serve_row(row, plan)
    assert served is None
    pool.mark_quarantined.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_empty_cards_still_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    db = _TrackingDB()
    svc = TopicQuizService(db)  # type: ignore[arg-type]
    _patch_generate(monkeypatch, svc, lambda _ctx: [])
    with pytest.raises(ValidationError, match="gerçek soru üretemedi"):
        await svc.generate(
            uuid.uuid4(),
            "kpss_tarih",
            "kpss_tarih__osmanli",
            QuizGenerateRequest(count=1, difficulty="medium", exam_type="kpss"),
        )
