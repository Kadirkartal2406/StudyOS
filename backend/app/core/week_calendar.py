"""Europe/Istanbul ISO-week helpers for weekly deneme + topic-test production."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


def now_istanbul() -> datetime:
    return datetime.now(_TZ)


def week_monday(dt: datetime | date | None = None) -> date:
    """Monday (date) of the ISO week containing *dt* (Istanbul)."""
    if dt is None:
        d = now_istanbul().date()
    elif isinstance(dt, datetime):
        if dt.tzinfo is None:
            d = dt.replace(tzinfo=timezone.utc).astimezone(_TZ).date()
        else:
            d = dt.astimezone(_TZ).date()
    else:
        d = dt
    return d - timedelta(days=d.weekday())


def production_target_monday(dt: datetime | date | None = None) -> date:
    """Monday users will open next — production runs the prior Mon–Sat/Sun.

    Same rules as topic-test production_target_week_id, as a date.
    """
    if dt is None:
        now = now_istanbul()
    elif isinstance(dt, date) and not isinstance(dt, datetime):
        now = datetime(dt.year, dt.month, dt.day, 12, 0, tzinfo=_TZ)
    elif isinstance(dt, datetime):
        if dt.tzinfo is None:
            now = dt.replace(tzinfo=timezone.utc).astimezone(_TZ)
        else:
            now = dt.astimezone(_TZ)
    else:
        now = now_istanbul()

    wd = now.weekday()  # Mon=0 … Sun=6
    if wd == 6:
        target = now + timedelta(days=1)
    elif wd == 0:
        target = now + timedelta(days=7)
    elif wd == 5:
        target = now + timedelta(days=2)
    else:
        target = now + timedelta(days=7 - wd)
    return week_monday(target)


def current_serve_monday(dt: datetime | date | None = None) -> date:
    """Week Monday currently shown to users."""
    return week_monday(dt)
