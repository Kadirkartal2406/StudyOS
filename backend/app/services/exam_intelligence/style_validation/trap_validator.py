"""Trap / distractor profile expectations."""

from __future__ import annotations

from typing import Any

_EXAM_TRAPS: dict[str, set[str]] = {
    "kpss": {"yakin_anlam", "abarti", "eksik_bilgi", "ters_ifade"},
    "yds": {"yakin_anlam", "kelime_tuzagi", "baglam_disi", "ters_ifade"},
    "ydt": {"yakin_anlam", "kelime_tuzagi", "baglam_disi", "ters_ifade"},
    "yokdil": {"yakin_anlam", "alan_kelime_tuzagi", "yanlis_cikarim"},
    "tyt": {"islem_hatasi", "birim_hatasi", "grafik_okuma", "eksik_veri"},
    "ales": {"yanlis_cikarim", "fazla_bilgi", "eksik_oncul", "matematiksel_hata"},
}


def validate_trap(contract: dict[str, Any]) -> dict[str, Any]:
    exam = str(contract.get("exam_code") or "").lower()
    topic = contract.get("topic_code")
    trap = contract.get("trap") or {}
    patterns = set(trap.get("patterns") or []) | set(trap.get("primary") or [])
    issues: list[str] = []
    warnings: list[str] = []

    if not patterns:
        issues.append("trap_patterns_empty")

    expected = _EXAM_TRAPS.get(exam)
    if expected and patterns and patterns.isdisjoint(expected):
        warnings.append(f"exam_trap_mismatch:got={sorted(patterns)[:6]}")

    slug = str(contract.get("topic_slug") or "")
    if slug in ("paragraf", "reading") and not patterns.intersection(
        {"yakin_anlam", "ters_ifade", "kelime_tuzagi", "abarti", "baglam_disi"}
    ):
        warnings.append("reading_trap_profile_weak")
    if slug == "problemler" and "islem_hatasi" not in patterns and exam in (
        "tyt",
        "ayt",
        "dgs",
        "lgs",
    ):
        warnings.append("math_trap_missing_islem_hatasi")

    return {
        "topic_code": topic,
        "exam_code": exam,
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


def validate_trap_batch(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [validate_trap(c) for c in contracts]
    failed = [r for r in rows if not r["passed"]]
    warned = [r for r in rows if r.get("warnings")]
    return {
        "checked": len(rows),
        "failed": len(failed),
        "warned": len(warned),
        "passed": len(failed) == 0,
        "failures": failed[:30],
        "warnings": warned[:40],
    }
