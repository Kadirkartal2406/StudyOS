"""Sprint 20 — Coach message builder unit tests (no DB)."""

from app.schemas.dashboard import NextActionProjection
from app.services.ai.coach_message_builder import build_today_message


def test_build_today_from_next_action() -> None:
    action = NextActionProjection(
        title="Fonksiyonlar çalış",
        reason="Confidence MEDIUM; son quiz zayıf",
        action_type="focus",
        deep_link_hint="/subjects/mat/topics/fonksiyonlar",
        subject_code="mat",
        topic_code="fonksiyonlar",
        tool_hint="pomodoro",
    )
    msg = build_today_message(
        next_action=action,
        insight_message=None,
        insight_reason=None,
        confidence_level="medium",
        assessment_note="Kalibrasyon %40",
        habit_hint="20:00 civarı daha başarılısın",
        knowledge=None,
        win=None,
        revision_due=True,
    )
    assert "Fonksiyonlar" in msg.headline or "fonksiyonlar" in (msg.focus_topic or "")
    assert msg.suggested_minutes == 25
    assert any(r.code == "confidence" for r in msg.reasons)
    assert msg.habit_hint
    assert msg.follow_ups


def test_build_observing_when_empty() -> None:
    msg = build_today_message(
        next_action=None,
        insight_message=None,
        insight_reason=None,
        confidence_level=None,
        assessment_note=None,
        habit_hint=None,
        knowledge=None,
        win=None,
        revision_due=False,
    )
    assert "dinliyorum" in msg.headline.lower() or "sinyal" in msg.body.lower()
