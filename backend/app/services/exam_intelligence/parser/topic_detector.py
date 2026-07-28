"""Exam catalog–aligned subject/topic blueprints (no AI, no stem text).

Used when PDF text is scanned/empty or keyword confidence is low.
Question numbers map to subject/topic codes only.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlueprintHit:
    subject_code: str
    topic_code: str
    confidence: float
    skill_type: str


def _prefix(exam_code: str) -> str:
    e = (exam_code or "").lower()
    return e or "gen"


def _hit(exam: str, subject: str, topic_slug: str, conf: float, skill: str) -> BlueprintHit:
    p = _prefix(exam)
    sc = f"{p}_{subject}"
    return BlueprintHit(
        subject_code=sc,
        topic_code=f"{sc}__{topic_slug}",
        confidence=conf,
        skill_type=skill,
    )


def expected_question_count(exam_code: str, pack: str | None = None) -> int | None:
    """Canonical booklet sizes when text extraction fails completely."""
    e = (exam_code or "").lower()
    pack = (pack or "").lower()
    if e == "tyt":
        return 120
    if e == "ayt":
        return 40  # booklet varies; keep conservative single-session shell
    if e == "ydt":
        return 80
    if e in ("yds", "yokdil"):
        return 80
    if e == "ales":
        return 50
    if e == "dgs":
        return 60
    if e == "kpss":
        return 120
    if e == "lgs":
        return 20 if pack in ("sayisal", "sozel") else 90
    if e == "ags":
        return 80
    return None


def assign_blueprint(
    exam_code: str,
    number: int,
    *,
    pack: str | None = None,
    question_count: int | None = None,
) -> BlueprintHit | None:
    """Map question number → catalog subject/topic with low–medium confidence."""
    e = (exam_code or "").lower()
    pack = (pack or "").lower()
    n = int(number)
    if n < 1:
        return None

    if e == "tyt":
        # Official TYT blocks (approximate published order)
        if 1 <= n <= 40:
            return _hit(e, "turkce", "paragraf", 0.55, "inference")
        if 41 <= n <= 45:
            return _hit(e, "tarih", "genel", 0.5, "recall")
        if 46 <= n <= 50:
            return _hit(e, "cografya", "genel", 0.5, "recall")
        if 51 <= n <= 55:
            return _hit(e, "felsefe", "genel", 0.5, "inference")
        if 56 <= n <= 60:
            return _hit(e, "din", "genel", 0.5, "recall")
        if 61 <= n <= 100:
            return _hit(e, "matematik", "problemler", 0.55, "problem_solving")
        if 101 <= n <= 107:
            return _hit(e, "fizik", "hareket", 0.5, "problem_solving")
        if 108 <= n <= 114:
            return _hit(e, "kimya", "mol", 0.5, "problem_solving")
        if 115 <= n <= 120:
            return _hit(e, "biyoloji", "hucre", 0.5, "recall")
        return _hit(e, "matematik", "genel", 0.35, "general")

    if e == "ayt":
        # Session PDFs often one field; use pack/heuristic by range within booklet
        if n <= 14:
            return _hit(e, "matematik", "fonksiyonlar", 0.4, "problem_solving")
        if n <= 24:
            return _hit(e, "geometri", "ucgenler", 0.4, "problem_solving")
        if n <= 34:
            return _hit(e, "fizik", "hareket", 0.4, "problem_solving")
        if n <= 41:
            return _hit(e, "kimya", "mol", 0.4, "problem_solving")
        return _hit(e, "biyoloji", "hucre", 0.4, "recall")

    if e == "kpss":
        # Many booklets are 60 (GY or GK). Prefer split by observed count.
        total = question_count or 120
        if total <= 60:
            if n <= 30:
                return _hit(e, "turkce", "paragraf", 0.45, "inference")
            return _hit(e, "matematik", "problemler", 0.45, "problem_solving")
        # Full 120-style GY+GK
        if n <= 27:
            return _hit(e, "turkce", "paragraf", 0.5, "inference")
        if n <= 60:
            return _hit(e, "matematik", "problemler", 0.5, "problem_solving")
        if n <= 87:
            return _hit(e, "tarih", "osmanli", 0.45, "recall")
        if n <= 105:
            return _hit(e, "cografya", "iklim", 0.45, "recall")
        return _hit(e, "vatandaslik", "anayasa", 0.45, "recall")

    if e == "ales":
        # Pack 1/2/3 booklets are typically sayısal or sözel mixed 50
        if n <= 25:
            return _hit(e, "turkce", "paragraf", 0.4, "inference")
        return _hit(e, "matematik", "problemler", 0.4, "problem_solving")

    if e == "dgs":
        if n <= 30:
            return _hit(e, "turkce", "paragraf", 0.4, "inference")
        return _hit(e, "matematik", "problemler", 0.4, "problem_solving")

    if e in ("ydt", "yds"):
        return _hit(e, "ingilizce", "reading", 0.6, "reading_comprehension")

    if e == "yokdil":
        field = pack if pack in ("fen", "saglik", "sosyal") else "general"
        return _hit(e, "ingilizce", field, 0.55, "reading_comprehension")

    if e == "lgs":
        if pack == "sozel":
            return _hit(e, "turkce", "paragraf", 0.5, "inference")
        if pack == "sayisal":
            if n <= 10:
                return _hit(e, "matematik", "problemler", 0.5, "problem_solving")
            return _hit(e, "fen", "genel", 0.45, "problem_solving")
        if n <= 20:
            return _hit(e, "turkce", "paragraf", 0.4, "inference")
        if n <= 40:
            return _hit(e, "matematik", "problemler", 0.4, "problem_solving")
        return _hit(e, "fen", "genel", 0.35, "general")

    if e == "ags":
        if n <= 40:
            return _hit(e, "turkce", "paragraf", 0.4, "inference")
        return _hit(e, "matematik", "problemler", 0.4, "problem_solving")

    return None


def subject_order_for_exam(exam_code: str, pack: str | None = None) -> list[str]:
    e = (exam_code or "").lower()
    p = _prefix(e)
    if e == "tyt":
        return [
            f"{p}_turkce",
            f"{p}_tarih",
            f"{p}_cografya",
            f"{p}_felsefe",
            f"{p}_din",
            f"{p}_matematik",
            f"{p}_fizik",
            f"{p}_kimya",
            f"{p}_biyoloji",
        ]
    if e == "kpss":
        return [
            f"{p}_turkce",
            f"{p}_matematik",
            f"{p}_tarih",
            f"{p}_cografya",
            f"{p}_vatandaslik",
        ]
    if e in ("ydt", "yds", "yokdil"):
        return [f"{p}_ingilizce"]
    if e == "ales":
        return [f"{p}_turkce", f"{p}_matematik"]
    if e == "dgs":
        return [f"{p}_turkce", f"{p}_matematik"]
    if e == "lgs" and pack == "sozel":
        return [f"{p}_turkce"]
    if e == "lgs" and pack == "sayisal":
        return [f"{p}_matematik", f"{p}_fen"]
    if e == "ags":
        return [f"{p}_turkce", f"{p}_matematik"]
    if e == "ayt":
        return [
            f"{p}_matematik",
            f"{p}_geometri",
            f"{p}_fizik",
            f"{p}_kimya",
            f"{p}_biyoloji",
        ]
    return []
