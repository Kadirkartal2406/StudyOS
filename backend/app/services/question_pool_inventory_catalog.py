"""Catalog-driven inventory slots for Question Pool admin.

Uses exam catalog seed + trial scheduler canonical identities as SSOT.
Stock target JSON supplies min/target overrides only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from app.core.exam_identity import pool_exam_key
from app.services.ai.subject_catalog_seed import YKS_AYT_BY_BRANCH, codes_for_exam
from app.services.exam_catalog.seed import build_exam_intelligence_seed
from app.services.trial_exam_scheduler import _ALL_EXAMS

DEFAULT_MINIMUM = 100
DEFAULT_TARGET = 200
DEFAULT_BAND = "medium"


@dataclass(frozen=True)
class InventoryCatalogSlot:
    exam: str  # canonical pool / inventory exam key
    exam_label: str
    subject_code: str
    subject_name: str
    topic_code: str
    topic_name: str
    difficulty_band: str = DEFAULT_BAND
    display_order: int = 0


def inventory_exam_label(pool_key: str, pack_name: str | None = None) -> str:
    """Human-readable exam row label for admin inventory."""
    labels = {
        "tyt": "TYT",
        "ayt_sayisal": "AYT Sayısal",
        "ayt_ea": "AYT EA",
        "ayt_sozel": "AYT Sözel",
        "ydt_ingilizce": "YDT",
        "kpss_lisans": "KPSS Lisans",
        "kpss_onlisans": "KPSS Ön Lisans",
        "kpss_ortaogretim": "KPSS Ortaöğretim",
        "lgs_sayisal": "LGS Sayısal",
        "lgs_sozel": "LGS Sözel",
        "ags": "AGS",
        "ales": "ALES",
        "dgs": "DGS",
        "yds_ingilizce": "YDS",
        "yokdil_fen": "YÖKDİL Fen",
        "yokdil_saglik": "YÖKDİL Sağlık",
        "yokdil_sosyal": "YÖKDİL Sosyal",
    }
    if pool_key in labels:
        return labels[pool_key]
    if pack_name:
        return pack_name
    return pool_key.replace("_", " ").upper()


def _flatten_packs(packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pack in packs or []:
        out.append(pack)
        for child in pack.get("children") or []:
            out.extend(_flatten_packs([child]))
    return out


def _catalog_root_for_parent(parent_exam: str) -> str:
    mapping = {
        "tyt": "yks",
        "ayt": "yks",
        "ydt": "yks",
        "kpss": "kpss",
        "lgs": "lgs",
        "ags": "ags",
        "ales": "ales",
        "dgs": "dgs",
        "yds": "yds",
        "yokdil": "yokdil",
    }
    return mapping.get(parent_exam, parent_exam)


def _find_pack(
    seed: list[dict[str, Any]],
    *,
    parent_exam: str,
    branch: str | None,
    pool_key: str,
) -> dict[str, Any] | None:
    root = _catalog_root_for_parent(parent_exam)
    exam_node = next((e for e in seed if e.get("code") == root), None)
    if exam_node is None:
        return None

    packs = _flatten_packs(exam_node.get("packs") or [])

    # Direct pack code match (ayt_sayisal, kpss_lisans, lgs_sayisal, yokdil_fen, …)
    for pack in packs:
        if pack.get("code") == pool_key:
            return pack

    # TYT
    if pool_key == "tyt":
        return next((p for p in packs if p.get("code") == "tyt"), None)

    # YDT
    if pool_key == "ydt_ingilizce":
        for pack in packs:
            if pack.get("code") == "ydt_ingilizce":
                return pack
            for child in pack.get("children") or []:
                if child.get("code") == "ydt_ingilizce":
                    return child

    # AGS
    if pool_key == "ags":
        return next((p for p in packs if p.get("code") in {"ags", "ags_genel"}), None)

    # ALES / DGS — pool key collapses branches; match by branch_key on pack
    if parent_exam in {"ales", "dgs"} and branch:
        want = f"{parent_exam}_{branch}"
        return next((p for p in packs if p.get("code") == want), None)

    # Fallback: branch_key
    if branch:
        return next((p for p in packs if p.get("branch_key") == branch), None)

    return None


def _infer_ayt_pool_key(subject_code: str) -> str | None:
    sc = subject_code.lower()
    matches: list[str] = []
    for branch, codes in YKS_AYT_BY_BRANCH.items():
        if branch in {"dil", "en"}:
            continue
        if sc in codes:
            matches.append(f"ayt_{branch}")
    if len(matches) == 1:
        return matches[0]
    if "ayt_sayisal" in matches:
        return "ayt_sayisal"
    return matches[0] if matches else None


def normalize_stock_exam_key(exam: str, subject_code: str) -> str:
    """Map legacy stock-target exam values to canonical inventory pool keys."""
    e = (exam or "").strip().lower()
    sc = (subject_code or "").strip().lower()

    if e == "yks":
        if sc.startswith("tyt_"):
            return "tyt"
        if sc.startswith("ayt_"):
            return _infer_ayt_pool_key(sc) or "ayt_sayisal"
        if sc == "ydt_ingilizce":
            return "ydt_ingilizce"
        return "yks"

    if e == "ayt":
        return _infer_ayt_pool_key(sc) or "ayt_sayisal"

    if e == "kpss":
        return "kpss_lisans"

    if e == "yds":
        return "yds_ingilizce"

    return pool_exam_key(e, None) if e in {"lgs", "yokdil"} else e


def pool_count_exam_keys(pool_exam: str, subject_code: str) -> list[str]:
    """Exam keys to aggregate when counting legacy pool rows (read-only)."""
    keys: list[str] = [pool_exam]
    sc = subject_code.lower()

    if pool_exam == "tyt" and sc.startswith("tyt_"):
        keys.append("yks")
    elif pool_exam.startswith("ayt_") and sc.startswith("ayt_"):
        keys.extend(["yks", "ayt"])
    elif pool_exam.startswith("kpss_"):
        keys.append("kpss")
    elif pool_exam == "yds_ingilizce":
        keys.append("yds")

    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def iter_catalog_inventory_slots() -> Iterator[InventoryCatalogSlot]:
    """Yield every canonical exam → subject → topic slot from catalog SSOT."""
    seed = build_exam_intelligence_seed()
    order = 0

    for parent_exam, branch in _ALL_EXAMS:
        pool_key = pool_exam_key(parent_exam, branch)
        pack = _find_pack(seed, parent_exam=parent_exam, branch=branch, pool_key=pool_key)
        if pack is None:
            continue

        allowed = codes_for_exam(pool_key, branch)
        pack_label = inventory_exam_label(pool_key, pack.get("name"))

        for subject in pack.get("subjects") or []:
            sc = subject.get("code") or ""
            if allowed is not None and sc not in allowed:
                continue
            sn = subject.get("name") or sc
            for topic in subject.get("topics") or []:
                order += 1
                yield InventoryCatalogSlot(
                    exam=pool_key,
                    exam_label=pack_label,
                    subject_code=sc,
                    subject_name=sn,
                    topic_code=topic.get("code") or "",
                    topic_name=topic.get("name") or topic.get("code") or "",
                    difficulty_band=DEFAULT_BAND,
                    display_order=order,
                )
