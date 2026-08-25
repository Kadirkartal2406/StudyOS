"""Staggered topic test production — week targeting and slot math."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.topic_test_catalog_service import iso_week_id, production_target_week_id
from app.services.topic_test_weekly_scheduler import (
    _TESTS_PER_NIGHT,
    catalog_test_slot_count,
    topic_slot_needs_work,
)

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


def _at(wd: int, hour: int = 12) -> datetime:
    # 2026-08-24 is Monday
    base = datetime(2026, 8, 24, hour, 0, 0, tzinfo=_TZ)
    return base + timedelta(days=wd)


def test_catalog_slot_count_matches_984():
    n = catalog_test_slot_count()
    assert n == 984
    assert n == _TESTS_PER_NIGHT * 6


def test_production_target_week_from_prior_monday():
    # Tue W-1 → next Monday is week containing 2026-08-31
    target = production_target_week_id(_at(1))
    assert target == iso_week_id(_at(7))


def test_production_target_week_from_sunday():
    target = production_target_week_id(_at(6))
    assert target == iso_week_id(_at(7))


def test_production_target_week_from_monday_starts_next_cycle():
    target = production_target_week_id(_at(0))
    assert target == iso_week_id(_at(7))


def test_topic_slot_needs_work_when_missing():
    assert topic_slot_needs_work("tyt", "tyt_matematik", "uslu_sayilar", "easy", set()) is True


def test_topic_slot_needs_work_false_when_complete():
    from app.core.constants import normalize_exam_code

    exam_n = normalize_exam_code("tyt")
    complete = {(exam_n, "tyt_matematik", "uslu_sayilar", "easy")}
    assert (
        topic_slot_needs_work("tyt", "tyt_matematik", "uslu_sayilar", "easy", complete)
        is False
    )
