"""Unit tests for measurement decision modes (default OFF preserves behavior)."""

from __future__ import annotations

from unittest.mock import patch

from app.services.ai.measurement_decision import decide_measurement_action
from app.services.ai.soft_measurement_scorer import SoftMeasurementScore
from app.services.ai_cost import measurement_flags as mf


def test_off_noop_autopool_unchanged():
    d = decide_measurement_action(
        quality_status="PASS",
        score=SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=1.0),
        mode="off",
    )
    assert d.final_action == "noop"
    assert d.allow_autopool is True
    assert d.should_regen is False


def test_shadow_log_only():
    d = decide_measurement_action(
        quality_status="PASS",
        score=SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=1.0),
        mode="shadow",
    )
    assert d.final_action == "shadow_log"
    assert d.allow_autopool is True
    assert d.should_regen is False


def test_quality_fail_wins():
    d = decide_measurement_action(
        quality_status="FAIL",
        score=SoftMeasurementScore(status="OK"),
        mode="soft_review",
    )
    assert d.final_action == "reject_quality"
    assert d.allow_autopool is False


def test_soft_review_regen_capped():
    score = SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=0.5)
    with patch(
        "app.services.ai.measurement_decision.measurement_max_regen", return_value=1
    ):
        d0 = decide_measurement_action(
            quality_status="PASS", score=score, mode="soft_review", retry_count=0
        )
        assert d0.should_regen is True
        assert d0.final_action == "regen"
        d1 = decide_measurement_action(
            quality_status="PASS", score=score, mode="soft_review", retry_count=1
        )
        assert d1.should_regen is False
        assert d1.final_action == "measurement_review_hold"
        assert d1.allow_autopool is False


def test_soft_review_ok_keep():
    d = decide_measurement_action(
        quality_status="PASS",
        score=SoftMeasurementScore(status="OK", distance=0.0),
        mode="soft_review",
    )
    assert d.final_action == "keep_candidate"
    assert d.allow_autopool is True


def test_unscored_keep_with_uncertainty():
    d = decide_measurement_action(
        quality_status="PASS",
        score=SoftMeasurementScore(status="UNSCORED", uncertainty=True),
        mode="soft_review",
    )
    assert d.final_action == "keep_candidate"
    assert d.provenance.get("measurement_uncertainty") is True


def test_shadow_no_regen_even_when_review():
    score = SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=0.9)
    d = decide_measurement_action(
        quality_status="PASS", score=score, mode="shadow", retry_count=0
    )
    assert d.final_action == "shadow_log"
    assert d.should_regen is False
    assert d.allow_autopool is True


def test_shadow_quality_fail_still_reject():
    d = decide_measurement_action(
        quality_status="FAIL",
        score=SoftMeasurementScore(status="OK"),
        mode="shadow",
    )
    assert d.final_action == "reject_quality"
    assert d.allow_autopool is False


def test_shadow_never_measurement_reject():
    d = decide_measurement_action(
        quality_status="PASS",
        score=SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=2.0),
        mode="shadow",
    )
    assert d.final_action != "reject_quality" or d.quality_status == "FAIL"
    assert "reject" not in (d.measurement_status or "").lower()
    assert d.final_action == "shadow_log"


def test_booklet_tracker_inactive_when_off():
    from app.services.ai.booklet_measurement_tracker import BookletMeasurementTracker

    t = BookletMeasurementTracker(contract=None)
    assert t.active is False
    t.record_item(subject="matematik")
    assert t.snapshot.subject_counts == {}


def test_pool_triage_interface_no_reject_from_measurement_alone_when_quality_pass():
    from app.services.question_pool_triage import SoftMeasurementPoolTriage, TriageAction

    triage = SoftMeasurementPoolTriage()
    long_stem = " ".join(["kelime"] * 40)
    r = triage.triage(
        {
            "quality_status": "PASS",
            "measurement_status": "REVIEW_OR_REGEN",
            "stem": long_stem,
            "exam": "tyt",
            "exam_unit": "yks_tyt",
        }
    )
    assert r.action == TriageAction.REVIEW
    r2 = triage.triage(
        {
            "quality_status": "FAIL",
            "measurement_status": "OK",
            "stem": long_stem,
            "exam": "tyt",
        }
    )
    assert r2.action == TriageAction.REJECT
    r3 = triage.triage({"stem": "kısa", "exam": "tyt"})
    assert r3.action == TriageAction.QUARANTINE


def test_soft_review_hold_no_hard_reject():
    d = decide_measurement_action(
        quality_status="PASS",
        score=SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=1.0),
        mode="soft_review",
        retry_count=1,
    )
    assert d.final_action == "measurement_review_hold"
    assert d.allow_autopool is False
    assert d.should_regen is False


def test_soft_review_no_infinite_regen_loop():
    score = SoftMeasurementScore(status="REVIEW_OR_REGEN", distance=2.0)
    with patch(
        "app.services.ai.measurement_decision.measurement_max_regen", return_value=1
    ):
        actions = []
        for retry in range(0, 5):
            d = decide_measurement_action(
                quality_status="PASS",
                score=score,
                mode="soft_review",
                retry_count=retry,
            )
            actions.append(d.final_action)
            if not d.should_regen:
                break
        assert actions.count("regen") == 1
        assert actions[-1] == "measurement_review_hold"


def test_default_measurement_mode_off():
    assert mf.measurement_mode() == "off"
    assert mf.measurement_enabled() is False
