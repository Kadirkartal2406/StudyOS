"""Weekly deneme calendar + batch sizing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.week_calendar import (
    current_serve_monday,
    production_target_monday,
    week_monday,
)
from app.services.trial_exam_scheduler import (
    _ALL_EXAMS,
    batch_slice_for_weekday,
    packs_per_batch,
)

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


def _at(wd: int, hour: int = 12) -> datetime:
    base = datetime(2026, 8, 24, hour, 0, 0, tzinfo=_TZ)  # Monday
    return base + timedelta(days=wd)


def test_week_monday_of_wednesday():
    assert week_monday(_at(2)) == _at(0).date()


def test_serve_monday_is_current_week():
    assert current_serve_monday(_at(3)) == _at(0).date()


def test_production_target_from_tuesday_is_next_monday():
    assert production_target_monday(_at(1)) == _at(7).date()


def test_nineteen_packs_cover_six_nights():
    assert len(_ALL_EXAMS) == 19
    assert packs_per_batch() == 4
    covered = []
    for wd in range(6):
        covered.extend(batch_slice_for_weekday(wd))
    assert len(covered) == 19
    assert len(set(covered)) == 19
