"""
Official-ish exam booklet blueprints — subject order + question counts.
Topics are distributed round-robin / proportionally by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ai.subject_catalog_seed import (
    KPSS_SUBJECT_CODES,
    YKS_AYT_BY_BRANCH,
)


BOOKLET_SUBJECT_CODE = "booklet"


@dataclass(frozen=True)
class BlueprintSection:
    subject_code: str
    count: int


@dataclass(frozen=True)
class ExamBlueprint:
    exam_type: str
    sections: tuple[BlueprintSection, ...]

    @property
    def total_count(self) -> int:
        return sum(s.count for s in self.sections)


# KPSS Genel Yetenek + Genel Kültür (lisans formu — ürün ders kodları)
_KPSS: tuple[BlueprintSection, ...] = (
    BlueprintSection("kpss_turkce", 30),
    BlueprintSection("kpss_matematik", 30),
    BlueprintSection("kpss_tarih", 27),
    BlueprintSection("kpss_cografya", 18),
    BlueprintSection("kpss_vatandaslik", 9),
    BlueprintSection("kpss_guncel", 6),
)

# TYT 120 — fine-grained StudyOS subjects (Matematik bloğu Mat+Geo)
_TYT: tuple[BlueprintSection, ...] = (
    BlueprintSection("tyt_turkce", 40),
    BlueprintSection("tyt_matematik", 30),
    BlueprintSection("tyt_geometri", 10),
    BlueprintSection("tyt_tarih", 5),
    BlueprintSection("tyt_cografya", 5),
    BlueprintSection("tyt_felsefe", 5),
    BlueprintSection("tyt_din", 5),
    BlueprintSection("tyt_fizik", 7),
    BlueprintSection("tyt_kimya", 7),
    BlueprintSection("tyt_biyoloji", 6),
)

# LGS ~90
_LGS: tuple[BlueprintSection, ...] = (
    BlueprintSection("lgs_turkce", 20),
    BlueprintSection("lgs_matematik", 20),
    BlueprintSection("lgs_fen", 20),
    BlueprintSection("lgs_inkilap", 10),
    BlueprintSection("lgs_din", 10),
    BlueprintSection("lgs_ingilizce", 10),
)

# AYT by branch (typical booklet sizes)
_AYT_BY_BRANCH: dict[str, tuple[BlueprintSection, ...]] = {
    "sayisal": (
        BlueprintSection("ayt_matematik", 30),
        BlueprintSection("ayt_geometri", 10),
        BlueprintSection("ayt_fizik", 14),
        BlueprintSection("ayt_kimya", 13),
        BlueprintSection("ayt_biyoloji", 13),
    ),
    "ea": (
        BlueprintSection("ayt_matematik", 30),
        BlueprintSection("ayt_geometri", 10),
        BlueprintSection("ayt_edebiyat", 24),
        BlueprintSection("ayt_tarih_1", 10),
        BlueprintSection("ayt_cografya_1", 6),
    ),
    "sozel": (
        BlueprintSection("ayt_edebiyat", 24),
        BlueprintSection("ayt_tarih_1", 10),
        BlueprintSection("ayt_cografya_1", 6),
        BlueprintSection("ayt_tarih_2", 11),
        BlueprintSection("ayt_cografya_2", 11),
        BlueprintSection("ayt_felsefe", 12),
        BlueprintSection("ayt_din", 6),
    ),
    "dil": (BlueprintSection("ayt_yabanci_dil", 80),),
}

_ALES: tuple[BlueprintSection, ...] = (
    BlueprintSection("ales_sayisal", 50),
    BlueprintSection("ales_sozel", 50),
)

_DGS: tuple[BlueprintSection, ...] = (
    BlueprintSection("dgs_sayisal", 60),
    BlueprintSection("dgs_sozel", 60),
)


def get_exam_blueprint(exam_type: str, branch: str | None = None) -> ExamBlueprint:
    """Return booklet sections for exam_type (+ optional YKS/AYT branch)."""
    et = (exam_type or "").strip().lower()
    br = (branch or "").strip().lower() or None

    if et == "kpss":
        return ExamBlueprint("kpss", _KPSS)

    if et == "tyt":
        return ExamBlueprint("tyt", _TYT)

    if et == "lgs":
        return ExamBlueprint("lgs", _LGS)

    if et == "ales":
        return ExamBlueprint("ales", _ALES)

    if et == "dgs":
        return ExamBlueprint("dgs", _DGS)

    if et == "ayt":
        sections = _AYT_BY_BRANCH.get(br or "sayisal") or _AYT_BY_BRANCH["sayisal"]
        return ExamBlueprint("ayt", sections)

    if et == "yks":
        # Full day: TYT + AYT branch
        ayt = _AYT_BY_BRANCH.get(br or "sayisal") or _AYT_BY_BRANCH["sayisal"]
        return ExamBlueprint("yks", _TYT + ayt)

    # Fallback: equal split across known KPSS codes if somehow unknown
    if et.startswith("kpss"):
        return ExamBlueprint(et, _KPSS)

    # Generic: one section placeholder — caller should expand via catalog
    return ExamBlueprint(et, (BlueprintSection(f"{et}_general", 40),))


def allocate_topics(topic_codes: list[str], count: int) -> list[tuple[str, int]]:
    """
    Spread `count` questions across topics (round-robin buckets).
    Returns [(topic_code, n), ...] with positive n only, covering as many
    distinct topics as possible.
    """
    if count <= 0:
        return []
    if not topic_codes:
        return []

    topics = list(topic_codes)
    # Prefer using all topics when count >= len(topics)
    buckets = [0] * len(topics)
    for i in range(count):
        buckets[i % len(topics)] += 1
    return [(topics[i], buckets[i]) for i in range(len(topics)) if buckets[i] > 0]


def filter_blueprint_to_available(
    blueprint: ExamBlueprint,
    available_codes: set[str],
) -> ExamBlueprint:
    """Drop sections whose subject is not in the user's catalog."""
    sections = tuple(s for s in blueprint.sections if s.subject_code in available_codes)
    if not sections:
        # Keep original if filter emptied (caller may still fail later)
        return blueprint
    return ExamBlueprint(blueprint.exam_type, sections)


def kpss_codes() -> tuple[str, ...]:
    return KPSS_SUBJECT_CODES


def ayt_branch_codes(branch: str) -> tuple[str, ...]:
    return YKS_AYT_BY_BRANCH.get(branch, ())
