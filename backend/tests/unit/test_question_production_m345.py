"""M34.5 — unit tests for question_production (no DB/LLM)."""

from __future__ import annotations

from app.services.question_production.cost_gate import (
    _batch_size_from_ratio,
    check_can_generate,
)
from app.services.question_production.pending_queue import PendingQueue
from app.services.question_production.progress import ProgressTracker
from app.services.question_production.types import BatchCostReport, PendingQuestion


def test_suggest_batch_size_levels():
    assert _batch_size_from_ratio(1.0) == 50
    assert _batch_size_from_ratio(0.5) == 50
    assert _batch_size_from_ratio(0.49) == 20
    assert _batch_size_from_ratio(0.25) == 20
    assert _batch_size_from_ratio(0.24) == 10
    assert _batch_size_from_ratio(0.10) == 10
    assert _batch_size_from_ratio(0.09) == 5
    assert _batch_size_from_ratio(0.0) == 5


def test_cost_gate_blocks_when_provider_null(monkeypatch):
    from app.core import config as config_mod

    monkeypatch.setattr(config_mod.settings, "AI_PROVIDER", "null")
    result = check_can_generate(planned_count=5)
    assert result.can_generate is False
    assert result.reason == "AI_PROVIDER is null"
    assert "daily_limit" in result.to_dict()
    assert "suggested_batch_size" in result.to_dict()
    assert result.estimated_batch_cost >= 0


def test_progress_stop_flag():
    tracker = ProgressTracker()
    tracker.reset(exam="yks", subject_code="tr", topic_code="t1", planned=10)
    assert tracker.is_stop_requested() is False
    assert tracker.get().status == "running"
    tracker.request_stop()
    assert tracker.is_stop_requested() is True
    assert tracker.get().status == "stopping"
    tracker.update(status="stopped")
    assert tracker.get().status == "stopped"


def test_pending_queue_approve_reject():
    q = PendingQueue()
    item = PendingQuestion(
        id="pq-1",
        stem="Hangisi doğrudur?",
        choices={"A": "a", "B": "b", "C": "c", "D": "d", "E": "e"},
        correct_key="A",
        explanation=None,
        scores={"overall": 90},
        exam="yks",
        subject_code="tr",
        topic_code="t1",
        difficulty_band="medium",
        plan={},
        created_at="2026-01-01T00:00:00+00:00",
    )
    q.add(item)
    assert len(q.list()) == 1
    assert q.get("pq-1") is not None
    approved = q.approve("pq-1")
    assert approved is not None
    assert approved["stem"] == "Hangisi doğrudur?"
    assert q.get("pq-1") is None

    q.add(item)
    assert q.reject("pq-1") is True
    assert q.reject("pq-1") is False
    assert q.list() == []


def test_batch_cost_report_average():
    report = BatchCostReport(
        gemini_calls=2,
        prompt_tokens=1600,
        completion_tokens=800,
        estimated_cost=0.01,
        questions_generated=5,
        questions_accepted=4,
        questions_rejected=1,
        average_cost_per_question=0.01 / 4,
        duration_ms=1200.0,
    )
    d = report.to_dict()
    assert d["questions_accepted"] == 4
    assert abs(d["average_cost_per_question"] - 0.0025) < 1e-9
    assert d["gemini_calls"] == 2
