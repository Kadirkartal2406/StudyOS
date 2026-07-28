"""
StudyOS — Exam Experience Pack (Sprint 11)

Sınav tipine göre konu öncelik önekleri ve etiketler.
Decision Engine / Next Action bu pack'i kullanarak kataloğu sıralar.
"""

from __future__ import annotations

EXAM_PACKS: dict[str, dict] = {
    "kpss": {
        "subject_priority_prefixes": [
            "kpss_genel_yetenek",
            "kpss_turkce",
            "kpss_matematik",
            "kpss_genel_kultur",
            "kpss_",
        ],
        "label": "KPSS",
    },
    "tyt": {
        "subject_priority_prefixes": [
            "tyt_turkce",
            "tyt_matematik",
            "tyt_fen_bilimleri",
            "tyt_sosyal_bilimler",
            "tyt_",
        ],
        "label": "TYT",
    },
    "ayt": {
        "subject_priority_prefixes": [
            "ayt_matematik",
            "ayt_fizik",
            "ayt_kimya",
            "ayt_biyoloji",
            "ayt_",
        ],
        "label": "AYT",
    },
    "yks": {
        "subject_priority_prefixes": [
            "tyt_turkce",
            "tyt_matematik",
            "tyt_fen_bilimleri",
            "tyt_sosyal_bilimler",
            "ayt_matematik",
            "ayt_",
            "tyt_",
        ],
        "label": "YKS",
    },
    "lgs": {
        "subject_priority_prefixes": [
            "lgs_matematik",
            "lgs_turkce",
            "lgs_fen_bilimleri",
            "lgs_sosyal_bilgiler",
            "lgs_",
        ],
        "label": "LGS",
    },
    "ales": {
        "subject_priority_prefixes": ["ales_"],
        "label": "ALES",
    },
    "dgs": {
        "subject_priority_prefixes": ["dgs_"],
        "label": "DGS",
    },
}


def get_pack(exam_type: str) -> dict:
    """Return exam pack for *exam_type* (case-insensitive). Empty dict if unknown."""
    key = (exam_type or "").lower().strip()
    if not key:
        return {}
    # "yks_say" → try full then base prefix
    if key in EXAM_PACKS:
        return EXAM_PACKS[key]
    base = key.split("_")[0]
    return EXAM_PACKS.get(base, {})
