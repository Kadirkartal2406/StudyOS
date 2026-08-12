"""StudyOS booklet PDF theme — print-safe exam booklet styling.

Purple accent for cover/headers; slate text tokens mirror mobile AppColors.
Question pages use ÖSYM-like two-column density settings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BookletPdfTheme:
    # Brand / accent (hex, no '#') — purple cover & headers
    accent: str = "6D28D9"  # violet-700
    accent_soft: str = "DDD6FE"  # violet-200
    accent_muted: str = "C4B5FD"  # violet-300 (geometric decor)
    brand_teal: str = "0F766E"  # AppColors.primary
    text: str = "0F172A"  # slate-900
    text_secondary: str = "64748B"  # slate-500
    rule: str = "E2E8F0"  # slate-200
    rule_strong: str = "CBD5E1"  # slate-300
    chip_bg: str = "F5F3FF"  # violet-50
    warning_border: str = "8B5CF6"  # violet-500
    footer: str = "94A3B8"
    white: str = "FFFFFF"

    # Spacing (mm) — slightly tighter like exam booklets
    margin_x_mm: float = 14.0
    margin_top_mm: float = 14.0
    margin_bottom_mm: float = 14.0
    footer_reserve_mm: float = 12.0
    col_gutter_mm: float = 7.0

    # Typography (pt)
    cover_brand_pt: float = 11.0
    cover_title_pt: float = 28.0
    cover_exam_pt: float = 18.0
    cover_meta_label_pt: float = 8.0
    cover_meta_value_pt: float = 11.0
    section_title_pt: float = 11.0
    section_sub_pt: float = 8.5
    question_pt: float = 9.5
    choice_pt: float = 9.0
    body_pt: float = 10.0
    footer_pt: float = 8.0

    # Vertical rhythm (pt) — ÖSYM denser than brochure layout
    stem_leading: float = 12.0
    choice_leading: float = 11.5
    choice_gap: float = 3.0
    after_question_gap: float = 16.0
    after_section_gap: float = 12.0

    # Approx chars per column line (Arial ~9.5pt)
    col_wrap_stem: int = 46
    col_wrap_choice: int = 42

    brand_name: str = "STUDYOS"
    brand_tagline: str = "Akıllı Çalış. Doğru İlerle."
    brand_url: str = "www.studyos.com"
    booklet_title: str = "GÜNLÜK DENEME"


# Default duration (minutes) when section_plan has no duration metadata.
DEFAULT_EXAM_DURATION_MINUTES: dict[str, int] = {
    "tyt": 135,
    "ayt": 180,
    "lgs": 120,
    "kpss": 130,
    "kpss_lisans": 130,
    "kpss_ön_lisans": 130,
    "kpss_ortaöğretim": 130,
    "dgs": 145,
    "ales": 150,
    "yds": 180,
    "ydt": 120,
    "yökdil": 180,
    "ags": 150,
}


THEME = BookletPdfTheme()
