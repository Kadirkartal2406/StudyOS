"""M29 Question Author unit tests (offline, no LLM)."""

from __future__ import annotations

import asyncio

from app.services.qie.types import GenerateContext, QuestionPlan
from app.services.question_author.author_planner import build_author_plan
from app.services.question_author.calibration_author import enforce_calibration_diversity
from app.services.question_author.diversity_controller import DiversityController
from app.services.question_author.orchestrator import QuestionAuthorEngine
from app.services.question_author.types import CriticScores, MIN_EXAMINER


def _plan(i: int = 0, **kwargs) -> QuestionPlan:
    base = dict(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="kpss_turkce__paragraf",
        topic_name="Paragraf",
        skill="inference",
        difficulty=72,
        bloom="analyze",
        reasoning_type="inference",
        paragraph_length=140,
        reading_time_sec=70,
        stem_type="inference",
        distractor_pattern="meaning_shift",
        choice_count=5,
        index=i,
    )
    base.update(kwargs)
    return QuestionPlan(**base)


def test_author_plan_has_no_stem_fields():
    plan = asyncio.run(build_author_plan(_plan(), use_llm=False))
    d = plan.to_dict()
    assert "stem" not in d
    assert plan.measured_outcome
    assert plan.difficulty_target >= 40
    assert plan.trap_type


def test_critic_rewrite_thresholds():
    low = CriticScores(style=70, difficulty=60, distractors=70)
    assert low.needs_rewrite()
    high = CriticScores(
        style=90,
        difficulty=80,
        option_quality=88,
        distractors=85,
        language=88,
        naturalness=86,
        exam_feeling=87,
        reasoning=84,
    )
    assert not high.needs_rewrite()


def test_diversity_rejects_same_opening():
    ctl = DiversityController(capacity=10)
    assert ctl.accept(
        stem="Ana fikir sorusu için uzun bir giriş metni burada",
        stem_type="a",
        outcome="x",
    )
    assert not ctl.accept(
        stem="Ana fikir sorusu için uzun bir giriş metni burada tekrar",
        stem_type="a",
        outcome="x",
    )


def test_calibration_first_four_diverse():
    plans = [
        _plan(
            i,
            skill="inference",
            stem_type="inference",
            reasoning_type="inference",
            difficulty=70,
            paragraph_length=100,
        )
        for i in range(4)
    ]
    out = enforce_calibration_diversity(plans)
    assert len({p.stem_type for p in out}) >= 3
    assert len({p.reasoning_type for p in out}) >= 3


def test_author_engine_offline_pipeline():
    engine = QuestionAuthorEngine(use_llm=False, separate_distractors=True)
    ctx = GenerateContext(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="kpss_turkce__paragraf",
        topic_name="Paragraf",
        count=2,
        kind="topic_quiz",
    )
    authored = asyncio.run(
        engine.author_batch(
            [_plan(0), _plan(1, skill="main_idea", stem_type="main_idea")],
            ctx=ctx,
        )
    )
    assert len(authored) >= 1
    q = authored[0]
    assert q.stem
    assert len(q.choices) == 5
    assert q.correct_key in q.choices
    assert q.rewrite_count <= 2
    meta = q.internal_metadata()
    assert "author_score" in meta
    assert "critic_score" in meta
    # Offline stubs are allowed only when use_llm=False
    assert not q.rejected
    assert q.examiner.score >= MIN_EXAMINER


def test_stub_guard_detects_template():
    from app.services.question_author.stub_guard import looks_like_author_stub

    stem = (
        "Temel Matematik alanında günlük yaşamdan bir durumu anlatan kısa bir metin "
        "düşününüz. Bloom düzeyi analyze olacak şekilde, yaklaşık 55 kelimelik resmi "
        "bir üslup hedeflenmiştir. Bu metne göre ölçülen kazanım: logic."
    )
    choices = {
        "A": "Doğru yanıt — logic",
        "B": "Çeldirici yakin_anlam",
        "C": "Çeldirici yanlis_cikarim",
    }
    assert looks_like_author_stub(stem, choices)
    assert not looks_like_author_stub(
        "İki sayının toplamı 15, farkı 3 ise büyük sayı kaçtır?",
        {"A": "9", "B": "6", "C": "12", "D": "3"},
    )


def test_writer_no_silent_stub_when_llm_required(monkeypatch):
    import asyncio

    from app.services.question_author import question_writer as qw
    from app.services.question_author.stub_guard import AuthorLLMError
    from app.services.question_author.types import AuthorPlan

    async def boom(*_a, **_k):
        raise RuntimeError("no llm")

    monkeypatch.setattr(qw, "default_llm", boom)
    plan = AuthorPlan(
        measured_outcome="logic",
        reasoning_type="inference",
        distractor_type="yakin_anlam",
        paragraph_length=55,
        option_strategy="tight",
        bloom_level="analyze",
        difficulty_target=70,
        reading_duration_sec=75,
        trap_type="yakin_anlam",
        exam="kpss",
        subject_code="mat",
        topic_code="mat__temel",
        topic_name="Temel Matematik",
        choice_count=4,
    )
    try:
        asyncio.run(qw.write_question(plan, use_llm=True))
        assert False, "expected AuthorLLMError"
    except AuthorLLMError:
        pass
