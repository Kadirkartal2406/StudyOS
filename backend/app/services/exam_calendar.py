"""Resmi sınav tarihleri — kullanıcıya sormadan geri sayım için.

Tarihler ÖSYM/MEB takvimine göre güncellenir; geçmiş tarihse bir sonraki
yıl aynı güne yuvarlanır (yaklaşık).
"""

from __future__ import annotations

from datetime import date, timedelta

# (ay, gün) — birincil oturum tarihi
_EXAM_MD: dict[str, tuple[int, int]] = {
    "yks": (6, 21),  # TYT haftası civarı
    "tyt": (6, 21),
    "ayt": (6, 22),
    "kpss": (9, 7),  # GY/GK oturumu civarı
    "lgs": (6, 15),
    "ales": (5, 4),
    "yds": (4, 6),
    "yokdil": (3, 16),
    "dgs": (7, 20),
    "ags": (7, 13),
}


def next_exam_date(exam_type: str | None, *, today: date | None = None) -> date:
    """Seçilen sınav için bir sonraki tahmini sınav tarihi."""
    today = today or date.today()
    key = (exam_type or "kpss").strip().lower()
    md = _EXAM_MD.get(key) or _EXAM_MD["kpss"]
    month, day = md
    candidate = date(today.year, month, day)
    if candidate <= today:
        candidate = date(today.year + 1, month, day)
    return candidate


def months_until(exam: date, *, today: date | None = None) -> int:
    today = today or date.today()
    days = max(0, (exam - today).days)
    return max(1, (days + 15) // 30)
