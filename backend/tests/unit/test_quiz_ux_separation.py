"""UX separation: Topic Test Catalog vs AI Soru Üret (topic quiz generate)."""

from __future__ import annotations

from app.core.constants import TOPIC_QUIZ_DEFAULT_COUNT, TOPIC_TEST_QUESTION_COUNT
from app.schemas.topic_quiz import QuizGenerateRequest


def test_generate_request_supports_count_and_difficulty():
    body = QuizGenerateRequest(count=10, difficulty="hard", exam_type="kpss")
    assert body.count == 10
    assert body.difficulty == "hard"
    assert body.exam_type == "kpss"


def test_generate_request_rejects_ultra_hard():
    try:
        QuizGenerateRequest(difficulty="ultra_hard")
        assert False, "expected validation error"
    except Exception:
        pass


def test_generate_count_capped_at_15():
    body = QuizGenerateRequest(count=15)
    assert body.count == 15
    try:
        QuizGenerateRequest(count=20)
        assert False, "expected validation error for count>15"
    except Exception:
        pass


def test_catalog_and_ondemand_counts_are_separate():
    assert TOPIC_TEST_QUESTION_COUNT == 10
    assert TOPIC_QUIZ_DEFAULT_COUNT == 5
    assert TOPIC_TEST_QUESTION_COUNT != TOPIC_QUIZ_DEFAULT_COUNT
