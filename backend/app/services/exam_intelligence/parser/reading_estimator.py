"""Reading time estimator (seconds) — heuristic wpm."""

from __future__ import annotations

from app.services.exam_intelligence.parser.question_locator import LocatedQuestion

# Turkish formal exam reading ~140–180 wpm; options add overhead
_WPM = 160
_OPTION_SEC = 2.5
_MULTI_STEP_SEC = 8
_VISUAL_SEC = 6


def estimate_reading_time_sec(q: LocatedQuestion) -> int:
    base = (q.word_count / _WPM) * 60
    base += len(q.option_lengths) * _OPTION_SEC
    if q.multi_step:
        base += _MULTI_STEP_SEC
    if q.has_table or q.has_visual_hint:
        base += _VISUAL_SEC
    base += q.equation_count * 4
    return max(5, min(180, int(round(base))))
