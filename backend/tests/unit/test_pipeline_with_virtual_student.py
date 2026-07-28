"""M31 pipeline smoke: Author → Review → VSSE (stub must fail; real stem must pass)."""

from __future__ import annotations

import asyncio

from app.services.qie.types import QuestionPlan
from app.services.question_author import QuestionAuthorEngine
from app.services.question_author.types import AuthoredQuestion, AuthorPlan
from app.services.question_review import QuestionReviewEngine
from app.services.question_virtual_student import VirtualStudentEngine


def _plan() -> QuestionPlan:
    return QuestionPlan(
        exam="kpss",
        subject_code="kpss_turkce",
        subject_name="Türkçe",
        topic_code="kpss_turkce__paragraf",
        topic_name="Paragraf",
        skill="inference",
        difficulty=72,
        bloom="analyze",
        reasoning_type="iki_adim",
        paragraph_length=140,
        reading_time_sec=70,
        stem_type="inference",
        distractor_pattern="meaning_shift",
        choice_count=5,
        index=0,
    )


def test_offline_author_stub_fails_review():
    """Production guard: Author offline templates must not pass Review."""
    authored = asyncio.run(QuestionAuthorEngine(use_llm=False).author_one(_plan()))
    assert not authored.rejected  # offline author still emits a template
    review = QuestionReviewEngine().review(authored)
    assert not review.passed


def test_pipeline_with_virtual_student_realistic_stem():
    plan = _plan()
    author_plan = AuthorPlan(
        measured_outcome="ana_fikir",
        reasoning_type="iki_adim",
        distractor_type="meaning_shift",
        paragraph_length=90,
        option_strategy="tight",
        bloom_level="analyze",
        difficulty_target=72,
        reading_duration_sec=70,
        trap_type="yakin_anlam",
        exam=plan.exam,
        subject_code=plan.subject_code,
        topic_code=plan.topic_code,
        topic_name=plan.topic_name,
        choice_count=5,
        qie_plan_index=0,
    )
    authored = AuthoredQuestion(
        stem=(
            "Bir araştırmacı, aynı ürünü farklı mağazalarda incelerken fiyat "
            "etiketlerinin tutarsız olduğunu fark eder. Kimi mağazalar indirimli "
            "görünen fiyatları normal fiyat gibi sunarken, kimileri de küçük "
            "yazılarla ek ücretleri gizlemektedir. Bu gözlemlerden hareketle "
            "aşağıdakilerden hangisi en doğru çıkarımdır?"
        ),
        choices={
            "A": "Tüketicinin bilgilendirilmesi her mağazada aynı standartta yapılır",
            "B": "Fiyat bilgisinin sunuluş biçimi tüketiciyi yanıltabilir",
            "C": "İndirimler her zaman gerçek maliyet düşüşünü yansıtır",
            "D": "Ek ücretler yalnızca büyük mağazalarda uygulanır",
            "E": "Araştırmacı yalnızca bir mağazayı incelemiştir",
        },
        correct_key="B",
        explanation="Paragraf, fiyat sunumundaki tutarsızlığın yanıltıcı olabileceğini gösterir.",
        author_plan=author_plan,
        author_score=88,
        critic_score=88,
        exam_feeling=86,
        style_score=88,
        difficulty_score=75,
        naturalness=86,
        reasoning_score=84,
        distractor_score=85,
        reading_time=70,
        ai_confidence=0.88,
    )
    review = QuestionReviewEngine().review(authored)
    assert review.passed, review.comments
    vsse = VirtualStudentEngine().simulate(authored)
    assert vsse.passed, vsse.reject_reasons
    assert vsse.virtual_student_score >= 70
    assert len(vsse.attempts) == 9
