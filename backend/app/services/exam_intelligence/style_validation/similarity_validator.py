"""Expected style-similarity pairs validator."""

from __future__ import annotations

from typing import Any, Callable

# (topic_a, topic_b, expectation, min_score, max_score) — absolute advisory bands
EXPECTED_PAIRS: list[tuple[str, str, str, float, float]] = [
    ("kpss_turkce__paragraf", "yds_ingilizce__reading", "high", 0.55, 1.0),
    ("kpss_turkce__paragraf", "tyt_geometri__ucgenler", "low", 0.0, 0.75),
    ("ales_matematik__problemler", "tyt_matematik__problemler", "high", 0.55, 1.0),
    ("yds_ingilizce__reading", "ayt_fizik__hareket", "very_low", 0.0, 0.72),
    ("kpss_turkce__paragraf", "yokdil_ingilizce__fen", "high", 0.50, 1.0),
    ("tyt_matematik__problemler", "dgs_matematik__problemler", "high", 0.55, 1.0),
]

# Hard gate: similar pair must outrank dissimilar pair by margin
RELATIVE_RULES: list[tuple[tuple[str, str], tuple[str, str], float]] = [
    (
        ("kpss_turkce__paragraf", "yds_ingilizce__reading"),
        ("kpss_turkce__paragraf", "tyt_geometri__ucgenler"),
        0.05,
    ),
    (
        ("ales_matematik__problemler", "tyt_matematik__problemler"),
        ("yds_ingilizce__reading", "ayt_fizik__hareket"),
        0.0,
    ),
    (
        ("tyt_matematik__problemler", "dgs_matematik__problemler"),
        ("kpss_turkce__paragraf", "tyt_geometri__ucgenler"),
        0.05,
    ),
]


def validate_similarity(
    contracts_by_topic: dict[str, dict[str, Any]],
    similarity_fn: Callable[[dict[str, Any], dict[str, Any]], float],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    unexpected: list[dict[str, Any]] = []
    skipped: list[str] = []
    score_cache: dict[tuple[str, str], float] = {}

    def _score(a: str, b: str) -> float | None:
        key = (a, b)
        if key in score_cache:
            return score_cache[key]
        if a not in contracts_by_topic or b not in contracts_by_topic:
            return None
        val = float(similarity_fn(contracts_by_topic[a], contracts_by_topic[b]))
        score_cache[key] = val
        score_cache[(b, a)] = val
        return val

    for a, b, expectation, lo, hi in EXPECTED_PAIRS:
        score = _score(a, b)
        if score is None:
            skipped.append(f"{a}↔{b}")
            continue
        ok = lo <= score <= hi
        row = {
            "a": a,
            "b": b,
            "expectation": expectation,
            "score": score,
            "allowed_range": [lo, hi],
            "passed": ok,
            "gate": "absolute",
        }
        results.append(row)
        if not ok:
            unexpected.append(row)

    relative_results: list[dict[str, Any]] = []
    relative_failures: list[dict[str, Any]] = []
    for high_pair, low_pair, margin in RELATIVE_RULES:
        hs = _score(*high_pair)
        ls = _score(*low_pair)
        if hs is None or ls is None:
            skipped.append(f"relative:{high_pair}vs{low_pair}")
            continue
        ok = hs >= ls + margin
        row = {
            "higher_pair": list(high_pair),
            "lower_pair": list(low_pair),
            "higher_score": hs,
            "lower_score": ls,
            "margin_required": margin,
            "delta": round(hs - ls, 3),
            "passed": ok,
            "gate": "relative",
        }
        relative_results.append(row)
        if not ok:
            relative_failures.append(row)

    tested = len(results)
    passed_abs = sum(1 for r in results if r["passed"])
    # Hard gate = relative ranking (directional correctness of Style DNA)
    passed_all = len(relative_results) > 0 and len(relative_failures) == 0
    return {
        "tested": tested,
        "passed": passed_abs,
        "failed": tested - passed_abs,
        "skipped_missing_topics": skipped,
        "results": results,
        "unexpected": unexpected,
        "relative_results": relative_results,
        "relative_failures": relative_failures,
        "passed_all": passed_all,
        "notes": (
            "Absolute bands are advisory; relative ranking is the M28 hard gate."
        ),
    }
