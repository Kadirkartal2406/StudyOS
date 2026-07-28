"""
StudyOS — Rule Engine Unit Testleri
"""

from app.services.ai.insight_engine import InsightContext
from app.services.ai.rule_engine import RuleEngine


def test_insufficient_data_recommendation():
    ctx = InsightContext(has_enough_data=False)
    items = RuleEngine().generate(ctx)
    assert items[0].code == "insufficient_data"
    assert items[0].reason


def test_idle_streak_rule():
    ctx = InsightContext(has_enough_data=True, days_since_last_study=3, today_study_minutes=0)
    items = RuleEngine().generate(ctx)
    idle = next(r for r in items if r.code == "idle_streak")
    assert idle.reason
    assert "3" in idle.reason


def test_streak_at_risk():
    ctx = InsightContext(
        has_enough_data=True,
        days_since_last_study=0,
        today_study_minutes=0,
        streak_days=5,
    )
    codes = {r.code for r in RuleEngine().generate(ctx)}
    assert "streak_at_risk" in codes


def test_low_accuracy_rule():
    ctx = InsightContext(
        has_enough_data=True,
        days_since_last_study=0,
        today_study_minutes=30,
        low_accuracy_subjects=[("Matematik", 50.0)],
    )
    items = RuleEngine().generate(ctx)
    assert any(r.code == "low_accuracy" and "Matematik" in r.message for r in items)
    assert any(r.code == "low_accuracy" and r.reason for r in items)


def test_performance_drop_rule():
    ctx = InsightContext(
        has_enough_data=True,
        days_since_last_study=0,
        today_study_minutes=20,
        week_study_minutes=60,
        previous_week_study_minutes=200,
    )
    codes = {r.code for r in RuleEngine().generate(ctx)}
    assert "performance_drop" in codes


def test_keep_going_when_healthy():
    ctx = InsightContext(
        has_enough_data=True,
        days_since_last_study=0,
        today_study_minutes=40,
        streak_days=2,
        week_study_minutes=200,
        previous_week_study_minutes=180,
        pomodoro_completion_rate=80,
    )
    items = RuleEngine().generate(ctx)
    assert items[0].code == "keep_going"
    assert items[0].reason
