"""Canonical exam identity — single resolver for catalog, pool, planner, trial.

Canonical ExamType values (user-facing / DB):
  kpss_lisans | kpss_onlisans | kpss_ortaogretim
  tyt | ayt_sayisal | ayt_ea | ayt_sozel | ydt_ingilizce
  lgs | ags | ales | dgs | yds_ingilizce | yokdil_ingilizce
  yks (umbrella: TYT + AYT branch) | custom

EI catalog trees use parent codes (kpss, yks, yds, …) + pack branch_key.
Trial / booklet APIs often pass (parent, branch). This module bridges both.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Values stored on ExamType / user targets / pool keys when fully resolved.
CANONICAL_EXAM_TYPES: frozenset[str] = frozenset(
    {
        "kpss_lisans",
        "kpss_onlisans",
        "kpss_ortaogretim",
        "tyt",
        "ayt_sayisal",
        "ayt_ea",
        "ayt_sozel",
        "ydt_ingilizce",
        "ags",
        "lgs",
        "ales",
        "dgs",
        "yds_ingilizce",
        "yokdil_ingilizce",
        "yks",
        "custom",
    }
)

# Parent exam code → EI catalog root (seed.py top-level exam.code)
_CATALOG_ROOT: dict[str, str] = {
    "kpss_lisans": "kpss",
    "kpss_onlisans": "kpss",
    "kpss_ortaogretim": "kpss",
    "kpss": "kpss",
    "tyt": "yks",
    "ayt": "yks",
    "ayt_sayisal": "yks",
    "ayt_ea": "yks",
    "ayt_sozel": "yks",
    "ydt": "yks",
    "ydt_ingilizce": "yks",
    "yks": "yks",
    "lgs": "lgs",
    "ags": "ags",
    "ales": "ales",
    "dgs": "dgs",
    "yds": "yds",
    "yds_ingilizce": "yds",
    "yokdil": "yokdil",
    "yokdil_ingilizce": "yokdil",
}

_KPSS_BRANCHES = frozenset({"lisans", "onlisans", "ortaogretim"})
_AYT_BRANCHES = frozenset({"sayisal", "ea", "sozel"})
_ALES_DGS_BRANCHES = frozenset({"sayisal", "sozel"})


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def canonicalize_exam_type(
    exam: str | None,
    branch: str | None = None,
) -> str:
    """Map legacy parent (+ optional branch) → canonical ExamType string."""
    e = _norm(exam)
    b = _norm(branch) or None

    if not e:
        return "custom"

    if e in CANONICAL_EXAM_TYPES:
        return e

    if e == "kpss":
        if b in _KPSS_BRANCHES:
            return f"kpss_{b}"
        return "kpss_lisans"

    if e == "ayt":
        if b in _AYT_BRANCHES:
            return f"ayt_{b}"
        if b in {"dil", "en", "ingilizce"}:
            return "ydt_ingilizce"
        return "ayt_sayisal"

    if e in {"ydt", "ydt_en", "yabanci_dil"}:
        return "ydt_ingilizce"

    if e == "yds":
        return "yds_ingilizce"

    if e == "yokdil":
        return "yokdil_ingilizce"

    # Unknown — return cleaned key (do not invent)
    return e


def catalog_exam_and_branch(
    exam: str | None,
    branch: str | None = None,
) -> tuple[str, str | None]:
    """
    Resolve (EI catalog exam code, pack branch_key).

    Examples:
      kpss_lisans → (kpss, lisans)
      ayt_sayisal → (ayt filter via yks tree, sayisal) → catalog root yks
      ydt_ingilizce → (yks, en)
      ("ydt", "en") → (yks, en)
      ("kpss", "lisans") → (kpss, lisans)
    """
    e = _norm(exam)
    b = _norm(branch) or None
    canonical = canonicalize_exam_type(e, b)

    if canonical.startswith("kpss_"):
        return "kpss", canonical.removeprefix("kpss_")

    if canonical.startswith("ayt_"):
        return "yks", canonical.removeprefix("ayt_")

    if canonical == "ydt_ingilizce":
        return "yks", "en"

    if canonical == "tyt":
        # TYT pack lives under yks with branch_key None; filter by pack code in callers
        return "yks", None

    if canonical == "yks":
        # Umbrella: branch selects AYT / YDT track when present
        if b in _AYT_BRANCHES:
            return "yks", b
        if b in {"dil", "en", "ingilizce"}:
            return "yks", "en"
        return "yks", b

    if canonical in {"yds_ingilizce", "yds"}:
        return "yds", b or "en"

    if canonical in {"yokdil_ingilizce", "yokdil"}:
        if b in {"fen", "saglik", "sosyal"}:
            return "yokdil", b
        return "yokdil", b or "fen"

    if canonical in {"ales", "dgs"}:
        if b in _ALES_DGS_BRANCHES:
            return canonical, b
        return canonical, b

    if e in {"ydt"}:
        return "yks", b or "en"

    if e == "ayt":
        return "yks", b if b in _AYT_BRANCHES else (b or "sayisal")

    if e == "kpss":
        return "kpss", b if b in _KPSS_BRANCHES else (b or "lisans")

    root = _CATALOG_ROOT.get(canonical, canonical)
    return root, b


def pool_exam_key(exam: str | None, branch: str | None = None) -> str:
    """
    Fingerprint / pool DB exam bucket.

    Never collapses YDT↔YDS↔YÖKDİL or AYT↔TYT.
    KPSS variants stay separated (kpss_lisans ≠ kpss_onlisans).
    YÖKDİL fields stay separated when branch is fen/saglik/sosyal.
    LGS sayisal/sozel stay separated when branch is set.
    """
    e = _norm(exam)
    b = _norm(branch) or None
    if e in {"yokdil", "yokdil_ingilizce"} and b in {"fen", "saglik", "sosyal"}:
        return f"yokdil_{b}"
    if e == "lgs" and b in {"sayisal", "sozel"}:
        return f"lgs_{b}"
    return canonicalize_exam_type(exam, branch)


def planner_exam_key(exam: str | None, branch: str | None = None) -> str:
    """Key into PLANNER_FALLBACK_BY_EXAM (canonical preferred, parent fallbacks OK)."""
    return canonicalize_exam_type(exam, branch)


def coerce_exam_payload(data: Any) -> Any:
    """Pydantic before-validator helper for dict payloads with exam_type (+ branch)."""
    if not isinstance(data, dict):
        return data
    raw = data.get("exam_type")
    if raw is None:
        return data
    branch = data.get("branch")
    canonical = canonicalize_exam_type(str(raw), branch if isinstance(branch, str) else None)
    out = dict(data)
    out["exam_type"] = canonical
    # Preserve branch when still useful for umbrella / dual-track exams
    if canonical.startswith("kpss_") and not branch:
        out["branch"] = canonical.removeprefix("kpss_")
    elif canonical.startswith("ayt_") and not branch:
        out["branch"] = canonical.removeprefix("ayt_")
    elif canonical == "ydt_ingilizce" and not branch:
        out["branch"] = "en"
    elif canonical in {"yds_ingilizce", "yokdil_ingilizce"} and not branch:
        out["branch"] = "en"
    return out


@dataclass(frozen=True)
class DailyBookletSlot:
    """One shared_daily_booklets row the user should see today.

    ``exam`` / ``branch`` match trial_exam_scheduler keys (e.g. ayt + sayisal),
    not canonical umbrella codes like yks or ayt_sayisal.
    """

    exam: str
    branch: str | None
    label: str


def daily_booklet_slots(
    active_exam: str | None,
    branch: str | None = None,
) -> tuple[DailyBookletSlot, ...]:
    """Map the user's active exam to published daily booklet pack(s).

    YKS (TYT+AYT) gets both a TYT pack and an AYT pack for the chosen field.
    Language-track YKS (dil/en) gets TYT + YDT instead of AYT.
    """
    e = _norm(active_exam)
    b = _norm(branch) or None
    if not e:
        return ()

    if e == "yks":
        if b in {"dil", "en", "ingilizce"}:
            return (
                DailyBookletSlot("tyt", None, "TYT"),
                DailyBookletSlot("ydt", "en", "YDT"),
            )
        ayt_b = b if b in _AYT_BRANCHES else "sayisal"
        return (
            DailyBookletSlot("tyt", None, "TYT"),
            DailyBookletSlot("ayt", ayt_b, "AYT"),
        )

    if e == "tyt":
        return (DailyBookletSlot("tyt", None, "TYT"),)

    if e == "ayt" or e.startswith("ayt_"):
        ayt_b = b if b in _AYT_BRANCHES else (
            e.removeprefix("ayt_") if e.startswith("ayt_") and e.removeprefix("ayt_") in _AYT_BRANCHES else "sayisal"
        )
        return (DailyBookletSlot("ayt", ayt_b, "AYT"),)

    if e in {"ydt", "ydt_ingilizce"}:
        return (DailyBookletSlot("ydt", "en", "YDT"),)

    if e == "kpss" or e.startswith("kpss_"):
        kpss_b = b if b in _KPSS_BRANCHES else (
            e.removeprefix("kpss_") if e.startswith("kpss_") else "lisans"
        )
        if kpss_b not in _KPSS_BRANCHES:
            kpss_b = "lisans"
        return (DailyBookletSlot("kpss", kpss_b, "KPSS"),)

    if e == "lgs":
        lgs_b = b if b in {"sayisal", "sozel"} else None
        return (DailyBookletSlot("lgs", lgs_b, "LGS"),)

    if e == "ales":
        ales_b = b if b in _ALES_DGS_BRANCHES else "sayisal"
        return (DailyBookletSlot("ales", ales_b, "ALES"),)

    if e == "dgs":
        dgs_b = b if b in _ALES_DGS_BRANCHES else "sayisal"
        return (DailyBookletSlot("dgs", dgs_b, "DGS"),)

    if e in {"yds", "yds_ingilizce"}:
        return (DailyBookletSlot("yds", "en", "YDS"),)

    if e.startswith("yokdil"):
        field = b if b in {"fen", "saglik", "sosyal"} else "fen"
        return (DailyBookletSlot("yokdil", field, "YÖKDİL"),)

    if e == "ags":
        return (DailyBookletSlot("ags", None, "AGS"),)

    return (DailyBookletSlot(e, b, e.upper()),)
