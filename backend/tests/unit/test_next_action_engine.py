"""Alignment Sprint-1/3 — Next Action Engine (Decision Projection) unit tests."""

from types import SimpleNamespace
from uuid import uuid4

from app.models.study_plan import StudyPlanStatus
from app.schemas.revision import DashboardRevisionSummary
from app.services.ai.next_action_engine import (
    CatalogTopic,
    build_action_for_topic,
    build_journey_line,
    build_next_action,
    build_today_context_lines,
)


def _plan(**kwargs):
    defaults = {
        "id": uuid4(),
        "title": "Geometri",
        "subject": "TYT Matematik",
        "topic": "Problemler",
        "estimated_minutes": 25,
        "status": StudyPlanStatus.PLANNED,
        "order_index": 0,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


_CATALOG = [
    CatalogTopic(
        subject_code="tyt_matematik",
        topic_code="tyt_mat_problemler",
        topic_name="Problemler",
        subject_name="TYT Matematik",
    ),
    CatalogTopic(
        subject_code="tyt_matematik",
        topic_code="tyt_mat_turev",
        topic_name="Türev",
        subject_name="TYT Matematik",
    ),
]


def test_next_action_prefers_revision_when_due():
    action = build_next_action(
        today_plans=[_plan()],
        revision=DashboardRevisionSummary(due_today=2, next_title="Türev"),
        ai_reason="Trend sinyali.",
        catalog=_CATALOG,
        revision_subject="TYT Matematik",
        revision_topic="Türev",
    )
    assert action.action_type == "revision"
    assert action.title == "Bu konu üzerinde tekrar yap"
    assert action.purpose == "review"
    assert action.tool_hint == "revision"
    assert action.deep_link_hint == "/subjects/tyt_matematik/topics/tyt_mat_turev"
    assert action.confidence_tone == "high"
    assert "2 tekrar" in action.reason or "Trend" in action.reason


def test_next_action_uses_incomplete_plan_when_no_revision():
    action = build_next_action(
        today_plans=[
            _plan(status=StudyPlanStatus.COMPLETED, order_index=0),
            _plan(
                title="Limit",
                subject="TYT Matematik",
                topic="Problemler",
                status=StudyPlanStatus.PLANNED,
                order_index=1,
                estimated_minutes=40,
            ),
        ],
        revision=DashboardRevisionSummary(due_today=0),
        ai_reason=None,
        catalog=_CATALOG,
    )
    assert action.action_type == "study_plan"
    assert action.title == "Bu konu üzerinde çalış"
    assert action.purpose == "study"
    assert action.tool_hint == "pomodoro"
    assert "Problemler" in (action.subtitle or "")
    assert "40 dk" in (action.subtitle or "")
    assert action.deep_link_hint == "/subjects/tyt_matematik/topics/tyt_mat_problemler"
    assert action.confidence_tone == "high"


def test_next_action_safe_default_when_insufficient_evidence():
    action = build_next_action(
        today_plans=[],
        revision=DashboardRevisionSummary(due_today=0),
        ai_reason=None,
        catalog=[],
    )
    assert action.action_type == "focus"
    assert action.confidence_tone == "low"
    assert action.deep_link_hint == "/subjects"
    assert action.purpose == "study"
    assert "tanımaya" in action.reason.lower() or "sinyal" in action.reason.lower()


def test_next_action_observation_uses_first_catalog_topic():
    action = build_next_action(
        today_plans=[],
        revision=DashboardRevisionSummary(due_today=0),
        catalog=_CATALOG,
    )
    assert action.deep_link_hint.startswith("/subjects/")
    assert "/topics/" in action.deep_link_hint
    assert action.tool_hint == "pomodoro"
    assert action.deep_link_hint != "/pomodoro"


def test_build_action_for_topic_review_vs_study():
    review = build_action_for_topic(
        subject_code="tyt_matematik",
        topic_code="tyt_mat_turev",
        topic_name="Türev",
        revision_due_for_topic=True,
    )
    assert review.purpose == "review"
    assert review.tool_hint == "revision"
    assert review.title == "Bu konu üzerinde tekrar yap"

    study = build_action_for_topic(
        subject_code="tyt_matematik",
        topic_code="tyt_mat_problemler",
        topic_name="Problemler",
        revision_due_for_topic=False,
    )
    assert study.purpose == "study"
    assert study.tool_hint == "pomodoro"
    assert study.title == "Bu konu üzerinde çalış"


def test_context_lines_are_informational_not_actions():
    lines = build_today_context_lines(
        today_plan_count=3,
        completed_plan_count=1,
        revision_due_today=1,
    )
    assert any("2 çalışma bloğun kaldı" in line for line in lines)
    assert any("1 tekrar bekliyor" in line for line in lines)
    assert len(lines) <= 3


def test_context_lines_hard_cap_at_three():
    """Sözleşme: Today Context Lines en fazla 3."""
    lines = build_today_context_lines(
        today_plan_count=10,
        completed_plan_count=1,
        revision_due_today=5,
    )
    assert len(lines) <= 3


def test_journey_line_is_compact():
    line = build_journey_line(
        active_exam_type="yks",
        days_remaining=120,
        primary_university="ODTÜ",
        primary_department="Bilgisayar",
    )
    assert line is not None
    assert "YKS" in line
    assert "ODTÜ" in line
    assert "120 gün" in line
