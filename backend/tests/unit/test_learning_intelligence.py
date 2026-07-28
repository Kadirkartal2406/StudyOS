"""Sprint 15 — Learning Intelligence projection helpers (unit)."""

from app.services.learning_intelligence_service import LearningIntelligenceService


def test_relative_labels():
    from datetime import UTC, datetime, timedelta

    svc = LearningIntelligenceService.__new__(LearningIntelligenceService)
    now = datetime.now(UTC)
    assert svc._relative(now) in ("Az önce",) or "saat" in svc._relative(now) or svc._relative(now) == "Az önce"
    assert svc._relative(now - timedelta(days=1)) == "Dün"
    assert "gün önce" in svc._relative(now - timedelta(days=3))
    assert svc._relative(now - timedelta(days=10)) == "Geçen hafta"


def test_resource_label_not_started_low_confidence():
    svc = LearningIntelligenceService.__new__(LearningIntelligenceService)
    label = svc._resource_label(
        status="not_started",
        confidence_level="low",
        revision_due=False,
    )
    assert "Zayıf alan" in label


def test_resource_label_completed():
    svc = LearningIntelligenceService.__new__(LearningIntelligenceService)
    label = svc._resource_label(
        status="completed",
        confidence_level="high",
        revision_due=False,
    )
    assert label == "Tamamlandı"


def test_resource_label_recently_used():
    from datetime import UTC, datetime, timedelta

    svc = LearningIntelligenceService.__new__(LearningIntelligenceService)
    now = datetime.now(UTC)
    label = svc._resource_label(
        status="in_progress",
        confidence_level="medium",
        revision_due=False,
        last_opened_at=now - timedelta(days=1),
        now=now,
    )
    assert label == "Son kullanılan"
