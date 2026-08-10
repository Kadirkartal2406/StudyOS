"""
Official exam booklet blueprints — subject order + question counts.

Section sizes come from exam_catalog.distributions.SUBJECT_QUOTAS (SSOT).
Topics are allocated by callers using EI topic metadata weights.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.exam_identity import canonicalize_exam_type
from app.services.ai.subject_catalog_seed import (
    KPSS_SUBJECT_CODES,
    YKS_AYT_BY_BRANCH,
)
from app.services.exam_catalog.distributions import (
    blueprint_sections,
    resolve_quota_key,
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


def _sections_for(key: str) -> tuple[BlueprintSection, ...]:
    rows = blueprint_sections(key)
    if not rows:
        return (BlueprintSection(f"{key}_general", 40),)
    return tuple(BlueprintSection(code, n) for code, n in rows)


def get_exam_blueprint(exam_type: str, branch: str | None = None) -> ExamBlueprint:
    """Return booklet sections for exam_type (+ optional branch)."""
    et_raw = (exam_type or "").strip().lower()
    br_raw = (branch or "").strip().lower() or None
    canonical = canonicalize_exam_type(et_raw, br_raw)
    key = resolve_quota_key(et_raw, br_raw)

    if canonical == "yks":
        if br_raw in {"dil", "en"}:
            return ExamBlueprint("yks", _sections_for("tyt") + _sections_for("ydt_ingilizce"))
        ayt_key = f"ayt_{br_raw}" if br_raw in {"sayisal", "ea", "sozel"} else "ayt_sayisal"
        return ExamBlueprint("yks", _sections_for("tyt") + _sections_for(ayt_key))

    if key in {
        "kpss_lisans",
        "kpss_onlisans",
        "kpss_ortaogretim",
        "tyt",
        "ayt_sayisal",
        "ayt_ea",
        "ayt_sozel",
        "ydt_ingilizce",
        "lgs",
        "lgs_sayisal",
        "lgs_sozel",
        "ags",
        "ales",
        "ales_sayisal",
        "ales_sozel",
        "dgs",
        "dgs_sayisal",
        "dgs_sozel",
        "yds_ingilizce",
        "yokdil_ingilizce",
        "yokdil_fen",
        "yokdil_saglik",
        "yokdil_sosyal",
    }:
        label = canonical if canonical else key
        return ExamBlueprint(label, _sections_for(key))

    # Parent kpss without branch → lisans quotas (same structure)
    if et_raw == "kpss" or canonical.startswith("kpss"):
        return ExamBlueprint(canonical or "kpss", _sections_for("kpss_lisans"))

    return ExamBlueprint(et_raw or "custom", _sections_for(key) if blueprint_sections(key) else (BlueprintSection(f"{et_raw or 'custom'}_general", 40),))


def allocate_topics(topic_codes: list[str], count: int) -> list[tuple[str, int]]:
    if count <= 0:
        return []
    if not topic_codes:
        return []
    topics = list(topic_codes)
    buckets = [0] * len(topics)
    for i in range(count):
        buckets[i % len(topics)] += 1
    return [(topics[i], buckets[i]) for i in range(len(topics)) if buckets[i] > 0]


def filter_blueprint_to_available(
    blueprint: ExamBlueprint,
    available_codes: set[str],
) -> ExamBlueprint:
    sections = tuple(s for s in blueprint.sections if s.subject_code in available_codes)
    if not sections:
        return blueprint
    return ExamBlueprint(blueprint.exam_type, sections)


def kpss_codes() -> tuple[str, ...]:
    return KPSS_SUBJECT_CODES


def ayt_branch_codes(branch: str) -> tuple[str, ...]:
    return YKS_AYT_BY_BRANCH.get(branch, ())
