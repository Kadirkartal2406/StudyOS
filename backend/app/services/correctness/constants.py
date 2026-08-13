"""Correctness gate constants — bump CORRECTNESS_VERSION when gate behavior changes."""

from __future__ import annotations

# Pool metadata / serve-time cache key. Bump when checks or FAIL semantics change.
CORRECTNESS_VERSION = "correctness_v2"

# Ordered check names included in this version. Adding/removing a check requires
# bumping CORRECTNESS_VERSION (enforced by unit tests).
CORRECTNESS_CHECKS: tuple[str, ...] = (
    "option_equivalence",
    "answer_key",
    "explanation_consistency",
)

REL_TOL = 1e-6
ABS_TOL = 1e-4
MAX_EXPR_LEN = 120

NUMERIC_SUBJECT_PREFIXES: tuple[str, ...] = (
    "lgs_matematik",
    "lgs_fen",
    "tyt_matematik",
    "tyt_geometri",
    "tyt_fizik",
    "tyt_kimya",
    "ayt_matematik",
    "ayt_geometri",
    "ayt_fizik",
    "ayt_kimya",
    "ales_sayisal",
    "dgs_sayisal",
    "ags_matematik",
    "kpss_matematik",
)

NUMERIC_EXAM_KEYS: frozenset[str] = frozenset(
    {
        "lgs_sayisal",
        "ales_sayisal",
        "dgs_sayisal",
        "ayt_sayisal",
        "ayt_ea",
    }
)


def is_numeric_subject(subject_code: str | None, exam: str | None = None) -> bool:
    sc = (subject_code or "").strip().lower()
    ex = (exam or "").strip().lower()
    if sc and any(sc == p or sc.startswith(p + "_") or sc.startswith(p) for p in NUMERIC_SUBJECT_PREFIXES):
        return True
    if ex in NUMERIC_EXAM_KEYS:
        return True
    if ex.startswith("lgs") and "sozel" not in ex:
        if not sc or "matematik" in sc or "fen" in sc or "sayisal" in sc:
            return True
    return False


def is_correctness_current(version: str | None) -> bool:
    """Pool hit: only skip re-check when stored version matches this gate."""
    return (version or "").strip() == CORRECTNESS_VERSION


# Domains where UNSUPPORTED must not reach the user (Soru Üret / pool serve).
# Verbal domains keep gate pass-through; do not list them here.
STEM_VERIFIED_DOMAINS: frozenset[str] = frozenset(
    {
        "matematik",
        "geometri",
        "fizik",
        "kimya",
        "biyoloji",
        "fen",
        "quantitative",
    }
)


def requires_verified_correctness(
    *,
    exam: str | None = None,
    subject_code: str | None = None,
    subject_name: str | None = None,
    topic_code: str | None = None,
    topic_name: str | None = None,
    plan: object | None = None,
) -> bool:
    """True when correctness must be PASS (not merely UNSUPPORTED) to accept/serve."""
    from app.services.qie.skill_profiles import resolve_domain

    if plan is not None:
        exam = getattr(plan, "exam", None) or exam
        subject_code = getattr(plan, "subject_code", None) or subject_code
        subject_name = getattr(plan, "subject_name", None) or subject_name
        topic_code = getattr(plan, "topic_code", None) or topic_code
        topic_name = getattr(plan, "topic_name", None) or topic_name
    domain = resolve_domain(
        exam=exam,
        subject_code=subject_code,
        subject_name=subject_name,
        topic_code=topic_code,
        topic_name=topic_name,
    )
    return domain in STEM_VERIFIED_DOMAINS


# Phase 2 integrity — separate from Phase 1 pool-skip version.
INTEGRITY_VERSION = "integrity_v1"
INTEGRITY_CHECKS: tuple[str, ...] = (
    "solution_consistency",
    "solvability",
    "asset",
    "choice_count",
    "ordering",
)
