"""
StudyOS — Subject catalog seed (Sprint-3.1.C.x)

Long-term domain model for Topic System, Flashcards, Resources,
Question Bank, AI Coach, and Adaptive Planner.

Identity = subject_code (canonical). subject_name = short display only.
LLM does not pick subjects; onboarding exam_type + branch → seed.
"""

from __future__ import annotations

from typing import Any

# ── TYT (common for all YKS branches) ─────────────────────────
TYT_SUBJECT_CODES: tuple[str, ...] = (
    "tyt_turkce",
    "tyt_matematik",
    "tyt_geometri",
    "tyt_tarih",
    "tyt_cografya",
    "tyt_felsefe",
    "tyt_din",
    "tyt_fizik",
    "tyt_kimya",
    "tyt_biyoloji",
)

# ── AYT by YKS branch ─────────────────────────────────────────
YKS_AYT_BY_BRANCH: dict[str, tuple[str, ...]] = {
    "sayisal": (
        "ayt_matematik",
        "ayt_geometri",
        "ayt_fizik",
        "ayt_kimya",
        "ayt_biyoloji",
    ),
    "ea": (
        "ayt_matematik",
        "ayt_geometri",
        "ayt_edebiyat",
        "ayt_tarih_1",
        "ayt_cografya_1",
    ),
    "sozel": (
        "ayt_edebiyat",
        "ayt_tarih_1",
        "ayt_cografya_1",
        "ayt_tarih_2",
        "ayt_cografya_2",
        "ayt_felsefe",
        "ayt_din",
    ),
    "dil": ("ydt_ingilizce",),
    "en": ("ydt_ingilizce",),
}

YKS_BRANCHES = frozenset(YKS_AYT_BY_BRANCH.keys())
KPSS_BRANCHES = frozenset({"lisans", "onlisans", "ortaogretim"})

KPSS_SUBJECT_CODES: tuple[str, ...] = (
    "kpss_turkce",
    "kpss_matematik",
    "kpss_tarih",
    "kpss_cografya",
    "kpss_vatandaslik",
    "kpss_guncel",
)

AGS_SUBJECT_CODES: tuple[str, ...] = (
    "ags_turkce",
    "ags_matematik",
)

# Codes that must be soft-deactivated (no longer product subjects)
INACTIVE_SUBJECT_CODES: tuple[str, ...] = (
    "tyt_sosyal",
    "tyt_fen",
    "ayt_tarih",
    "ayt_cografya",
    "ayt_yabanci_dil",  # superseded by ydt_ingilizce
    "kpss_gy",
    "kpss_gk",
    "kpss_eb",
    "yks_turkce",
    "yks_matematik",
    "yks_fizik",
    "yks_kimya",
    "yks_biyoloji",
    "yks_tarih",
    "yks_cografya",
    "yks_edebiyat",
    "yks_felsefe",
    "yks_din",
    "yds_kelime",
    "yds_okuma",
    "ags_egitim_bilimleri",
    "ags_genel_kultur",
)


def codes_for_exam(exam_type: str, branch: str | None) -> set[str] | None:
    """
    Return allowed subject_codes for seeding/listing.
    None = use full active catalog filtered by exam_type (LGS/ALES/DGS/…).
    """
    from app.core.exam_identity import canonicalize_exam_type
    from app.services.exam_catalog.distributions import SUBJECT_QUOTAS, resolve_quota_key

    et = (exam_type or "").strip().lower()
    br = (branch or "").strip().lower() or None
    canonical = canonicalize_exam_type(et, br)

    if canonical.startswith("kpss_") or et == "kpss":
        return set(KPSS_SUBJECT_CODES)

    if canonical == "tyt" or et == "tyt":
        return set(TYT_SUBJECT_CODES)

    if canonical.startswith("ayt_") or et == "ayt":
        key = br or (
            canonical.removeprefix("ayt_") if canonical.startswith("ayt_") else None
        )
        if key and key in YKS_AYT_BY_BRANCH:
            return set(YKS_AYT_BY_BRANCH[key])
        return set()

    if canonical == "ydt_ingilizce" or et in {"ydt", "ydt_ingilizce"}:
        return {"ydt_ingilizce"}

    if canonical == "yds_ingilizce" or et in {"yds", "yds_ingilizce"}:
        return {"yds_ingilizce"}

    if canonical.startswith("yokdil") or et in {"yokdil", "yokdil_ingilizce"}:
        return {"yokdil_ingilizce"}

    if canonical == "ags" or et == "ags":
        return set(AGS_SUBJECT_CODES)

    if canonical == "lgs" or et == "lgs":
        key = resolve_quota_key("lgs", br)
        quotas = SUBJECT_QUOTAS.get(key) or SUBJECT_QUOTAS["lgs"]
        return set(quotas.keys())

    if canonical in {"ales", "dgs"} or et in {"ales", "dgs"}:
        key = resolve_quota_key(et or canonical, br)
        quotas = SUBJECT_QUOTAS.get(key) or {}
        return set(quotas.keys()) if quotas else None

    if canonical == "yks" or et == "yks":
        codes = set(TYT_SUBJECT_CODES)
        if br and br in YKS_AYT_BY_BRANCH:
            codes.update(YKS_AYT_BY_BRANCH[br])
        return codes

    return None
# exam_types: ExamType string list; section: tyt/ayt (optional)
SUBJECT_CATALOG_SEED: list[dict[str, Any]] = [
    # YKS — TYT (individual dersler)
    {"code": "tyt_turkce", "name": "Türkçe", "exam_types": ["yks", "tyt"], "sort_order": 10, "section": "tyt", "is_active": True},
    {"code": "tyt_matematik", "name": "Matematik", "exam_types": ["yks", "tyt"], "sort_order": 20, "section": "tyt", "is_active": True},
    {"code": "tyt_geometri", "name": "Geometri", "exam_types": ["yks", "tyt"], "sort_order": 30, "section": "tyt", "is_active": True},
    {"code": "tyt_tarih", "name": "Tarih", "exam_types": ["yks", "tyt"], "sort_order": 40, "section": "tyt", "is_active": True},
    {"code": "tyt_cografya", "name": "Coğrafya", "exam_types": ["yks", "tyt"], "sort_order": 50, "section": "tyt", "is_active": True},
    {"code": "tyt_felsefe", "name": "Felsefe", "exam_types": ["yks", "tyt"], "sort_order": 60, "section": "tyt", "is_active": True},
    {"code": "tyt_din", "name": "Din Kültürü", "exam_types": ["yks", "tyt"], "sort_order": 70, "section": "tyt", "is_active": True},
    {"code": "tyt_fizik", "name": "Fizik", "exam_types": ["yks", "tyt"], "sort_order": 80, "section": "tyt", "is_active": True},
    {"code": "tyt_kimya", "name": "Kimya", "exam_types": ["yks", "tyt"], "sort_order": 90, "section": "tyt", "is_active": True},
    {"code": "tyt_biyoloji", "name": "Biyoloji", "exam_types": ["yks", "tyt"], "sort_order": 100, "section": "tyt", "is_active": True},
    # Legacy TYT packages — inactive
    {"code": "tyt_sosyal", "name": "Sosyal Bilimler", "exam_types": ["yks", "tyt"], "sort_order": 999, "section": "tyt", "is_active": False},
    {"code": "tyt_fen", "name": "Fen Bilimleri", "exam_types": ["yks", "tyt"], "sort_order": 999, "section": "tyt", "is_active": False},
    # YKS — AYT
    {"code": "ayt_matematik", "name": "Matematik", "exam_types": ["yks", "ayt"], "sort_order": 110, "section": "ayt", "is_active": True},
    {"code": "ayt_geometri", "name": "Geometri", "exam_types": ["yks", "ayt"], "sort_order": 120, "section": "ayt", "is_active": True},
    {"code": "ayt_fizik", "name": "Fizik", "exam_types": ["yks", "ayt"], "sort_order": 130, "section": "ayt", "is_active": True},
    {"code": "ayt_kimya", "name": "Kimya", "exam_types": ["yks", "ayt"], "sort_order": 140, "section": "ayt", "is_active": True},
    {"code": "ayt_biyoloji", "name": "Biyoloji", "exam_types": ["yks", "ayt"], "sort_order": 150, "section": "ayt", "is_active": True},
    {"code": "ayt_edebiyat", "name": "Edebiyat", "exam_types": ["yks", "ayt"], "sort_order": 160, "section": "ayt", "is_active": True},
    {"code": "ayt_tarih_1", "name": "Tarih-1", "exam_types": ["yks", "ayt"], "sort_order": 170, "section": "ayt", "is_active": True},
    {"code": "ayt_cografya_1", "name": "Coğrafya-1", "exam_types": ["yks", "ayt"], "sort_order": 180, "section": "ayt", "is_active": True},
    {"code": "ayt_tarih_2", "name": "Tarih-2", "exam_types": ["yks", "ayt"], "sort_order": 190, "section": "ayt", "is_active": True},
    {"code": "ayt_cografya_2", "name": "Coğrafya-2", "exam_types": ["yks", "ayt"], "sort_order": 200, "section": "ayt", "is_active": True},
    {"code": "ayt_felsefe", "name": "Felsefe", "exam_types": ["yks", "ayt"], "sort_order": 210, "section": "ayt", "is_active": True},
    {"code": "ayt_din", "name": "Din Kültürü", "exam_types": ["yks", "ayt"], "sort_order": 220, "section": "ayt", "is_active": True},
    {"code": "ayt_yabanci_dil", "name": "Yabancı Dil", "exam_types": ["yks", "ayt"], "sort_order": 999, "section": "ayt", "is_active": False},
    {"code": "ydt_ingilizce", "name": "YDT İngilizce", "exam_types": ["yks", "ydt", "ydt_ingilizce"], "sort_order": 230, "section": "ydt", "is_active": True},
    # Legacy AYT singles — inactive
    {"code": "ayt_tarih", "name": "Tarih", "exam_types": ["yks", "ayt"], "sort_order": 999, "section": "ayt", "is_active": False},
    {"code": "ayt_cografya", "name": "Coğrafya", "exam_types": ["yks", "ayt"], "sort_order": 999, "section": "ayt", "is_active": False},
    # KPSS — ders odaklı (all variants share subject codes)
    {"code": "kpss_turkce", "name": "Türkçe", "exam_types": ["kpss", "kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"], "sort_order": 10, "section": None, "is_active": True},
    {"code": "kpss_matematik", "name": "Matematik", "exam_types": ["kpss", "kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"], "sort_order": 20, "section": None, "is_active": True},
    {"code": "kpss_tarih", "name": "Tarih", "exam_types": ["kpss", "kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"], "sort_order": 30, "section": None, "is_active": True},
    {"code": "kpss_cografya", "name": "Coğrafya", "exam_types": ["kpss", "kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"], "sort_order": 40, "section": None, "is_active": True},
    {"code": "kpss_vatandaslik", "name": "Vatandaşlık", "exam_types": ["kpss", "kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"], "sort_order": 50, "section": None, "is_active": True},
    {"code": "kpss_guncel", "name": "Güncel Bilgiler", "exam_types": ["kpss", "kpss_lisans", "kpss_onlisans", "kpss_ortaogretim"], "sort_order": 60, "section": None, "is_active": True},
    # Legacy KPSS packages — inactive
    {"code": "kpss_gy", "name": "Genel Yetenek", "exam_types": ["kpss"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "kpss_gk", "name": "Genel Kültür", "exam_types": ["kpss"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "kpss_eb", "name": "Eğitim Bilimleri", "exam_types": ["kpss"], "sort_order": 999, "section": None, "is_active": False},
    # LGS
    {"code": "lgs_turkce", "name": "Türkçe", "exam_types": ["lgs"], "sort_order": 10, "section": None, "is_active": True},
    {"code": "lgs_matematik", "name": "Matematik", "exam_types": ["lgs"], "sort_order": 20, "section": None, "is_active": True},
    {"code": "lgs_fen", "name": "Fen Bilimleri", "exam_types": ["lgs"], "sort_order": 30, "section": None, "is_active": True},
    {"code": "lgs_inkilap", "name": "İnkılap Tarihi", "exam_types": ["lgs"], "sort_order": 40, "section": None, "is_active": True},
    {"code": "lgs_din", "name": "Din Kültürü", "exam_types": ["lgs"], "sort_order": 50, "section": None, "is_active": True},
    {"code": "lgs_ingilizce", "name": "İngilizce", "exam_types": ["lgs"], "sort_order": 60, "section": None, "is_active": True},
    # AGS — resmi: Türkçe + Matematik
    {"code": "ags_turkce", "name": "Türkçe", "exam_types": ["ags"], "sort_order": 10, "section": None, "is_active": True},
    {"code": "ags_matematik", "name": "Matematik", "exam_types": ["ags"], "sort_order": 20, "section": None, "is_active": True},
    {"code": "ags_egitim_bilimleri", "name": "Eğitim Bilimleri", "exam_types": ["ags"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "ags_genel_kultur", "name": "Genel Kültür", "exam_types": ["ags"], "sort_order": 999, "section": None, "is_active": False},
    # YDS / YÖKDİL — single English subject aligned with EI catalog
    {"code": "yds_ingilizce", "name": "İngilizce", "exam_types": ["yds", "yds_ingilizce"], "sort_order": 10, "section": None, "is_active": True},
    {"code": "yokdil_ingilizce", "name": "İngilizce", "exam_types": ["yokdil", "yokdil_ingilizce"], "sort_order": 10, "section": None, "is_active": True},
    # Legacy granular YDS rows — inactive
    {"code": "yds_vocabulary", "name": "Vocabulary", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_grammar", "name": "Grammar", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_reading", "name": "Reading", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_cloze", "name": "Cloze Test", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_sentence_completion", "name": "Sentence Completion", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_translation", "name": "Translation", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_dialogue", "name": "Dialogue", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_paragraph", "name": "Paragraph", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_meaning", "name": "Meaning", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    {"code": "yds_listening", "name": "Listening", "exam_types": ["yds"], "sort_order": 999, "section": None, "is_active": False},
    # ALES / DGS
    {"code": "ales_sayisal", "name": "Sayısal", "exam_types": ["ales"], "sort_order": 10, "section": None, "is_active": True},
    {"code": "ales_sozel", "name": "Sözel", "exam_types": ["ales"], "sort_order": 20, "section": None, "is_active": True},
    {"code": "dgs_sayisal", "name": "Sayısal", "exam_types": ["dgs"], "sort_order": 10, "section": None, "is_active": True},
    {"code": "dgs_sozel", "name": "Sözel", "exam_types": ["dgs"], "sort_order": 20, "section": None, "is_active": True},
]
