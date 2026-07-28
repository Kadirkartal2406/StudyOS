"""Reasoning profile expectations by exam / topic."""

from __future__ import annotations

from typing import Any

# exam → expected dominant families (any match ok)
_EXAM_EXPECTATIONS: dict[str, set[str]] = {
    "kpss": {
        "eleme",
        "karsilastirma",
        "iki_adim",
        "tek_adim",
        "analojik",
        "soyutlama",
        "cok_adim",
        "kosul_zinciri",
        "neden_sonuc",
    },
    "ales": {"cok_adim", "iki_adim", "kosul_zinciri", "karsilastirma", "soyutlama", "neden_sonuc"},
    "tyt": {"iki_adim", "cok_adim", "neden_sonuc", "kosul_zinciri", "tek_adim", "eleme"},
    "yds": {"eleme", "analojik", "karsilastirma", "soyutlama", "tek_adim", "iki_adim"},
    "yokdil": {"eleme", "analojik", "karsilastirma", "iki_adim", "soyutlama"},
    "ydt": {"eleme", "analojik", "karsilastirma", "iki_adim", "soyutlama"},
    "dgs": {"iki_adim", "cok_adim", "neden_sonuc", "karsilastirma", "kosul_zinciri"},
}


def validate_reasoning(contract: dict[str, Any]) -> dict[str, Any]:
    exam = str(contract.get("exam_code") or "").lower()
    topic = contract.get("topic_code")
    reasoning = contract.get("reasoning") or {}
    dominant = reasoning.get("dominant")
    patterns = set(reasoning.get("patterns") or [])
    if dominant:
        patterns.add(str(dominant))

    issues: list[str] = []
    warnings: list[str] = []

    if not dominant and not patterns:
        issues.append("reasoning_empty")

    expected = _EXAM_EXPECTATIONS.get(exam)
    if expected and patterns and patterns.isdisjoint(expected):
        warnings.append(
            f"unexpected_reasoning_family:dominant={dominant};patterns={sorted(patterns)[:5]}"
        )

    # Topic-specific soft checks
    slug = str(contract.get("topic_slug") or "")
    skill = str((contract.get("language_style") or {}).get("skill_type") or "")
    if slug in ("paragraf", "reading") or skill in ("inference", "reading_comprehension"):
        if not patterns.intersection({"eleme", "karsilastirma", "analojik", "soyutlama", "tek_adim", "iki_adim"}):
            warnings.append("reading_topic_missing_comprehension_reasoning")
    if slug == "problemler" or skill == "problem_solving":
        if not patterns.intersection({"neden_sonuc", "kosul_zinciri", "iki_adim", "cok_adim", "hipotez"}):
            warnings.append("problem_topic_missing_multi_step_reasoning")

    return {
        "topic_code": topic,
        "exam_code": exam,
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "dominant": dominant,
    }


def validate_reasoning_batch(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [validate_reasoning(c) for c in contracts]
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
