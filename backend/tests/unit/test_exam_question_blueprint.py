"""Unit tests — Sprint 23 exam booklet blueprint."""

from app.services.ai.exam_question_blueprint import (
    allocate_topics,
    filter_blueprint_to_available,
    get_exam_blueprint,
)


def test_kpss_blueprint_totals_120():
    bp = get_exam_blueprint("kpss")
    assert bp.total_count == 120
    codes = [s.subject_code for s in bp.sections]
    assert codes == [
        "kpss_turkce",
        "kpss_matematik",
        "kpss_tarih",
        "kpss_cografya",
        "kpss_vatandaslik",
        "kpss_guncel",
    ]


def test_tyt_blueprint_totals_120():
    bp = get_exam_blueprint("tyt")
    assert bp.total_count == 120


def test_allocate_topics_covers_all_when_enough():
    topics = [f"t{i}" for i in range(10)]
    alloc = allocate_topics(topics, 30)
    assert sum(n for _, n in alloc) == 30
    assert len(alloc) == 10
    assert all(n >= 1 for _, n in alloc)


def test_allocate_topics_spreads_not_single_pile():
    topics = ["a", "b", "c"]
    alloc = dict(allocate_topics(topics, 8))
    assert alloc["a"] >= 2
    assert alloc["b"] >= 2
    assert alloc["c"] >= 2


def test_filter_blueprint_keeps_available_only():
    bp = get_exam_blueprint("kpss")
    filtered = filter_blueprint_to_available(
        bp, {"kpss_turkce", "kpss_matematik"}
    )
    assert filtered.total_count == 60
    assert len(filtered.sections) == 2
