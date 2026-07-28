"""
StudyOS — Exam net / score strategies (Sprint 23 M23.8).

Exam Intelligence / style catalog ile uyumlu; magic number yok —
penalty exam_code'a göre seçilir.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExamScoreResult:
    correct: int
    wrong: int
    blank: int
    net: Decimal
    success_pct: float
    penalty_per_wrong: Decimal
    exam_code: str
    formula: str


# Official-ish wrong penalties (ÖSYM common patterns)
_PENALTY: dict[str, Decimal] = {
    "tyt": Decimal("0.25"),
    "ayt": Decimal("0.25"),
    "yks": Decimal("0.25"),
    "kpss": Decimal("0.25"),
    "ales": Decimal("0.25"),
    "dgs": Decimal("0.25"),
    "yds": Decimal("0.25"),
    "yokdil": Decimal("0.25"),
    "lgs": Decimal("0"),  # LGS net = doğru (yanlış düşmez klasik formülde)
    "ags": Decimal("0.25"),
}


def wrong_penalty_for_exam(exam_type: str | None) -> Decimal:
    code = (exam_type or "").strip().lower()
    if code in _PENALTY:
        return _PENALTY[code]
    return Decimal("0.25")


def compute_exam_score(
    *,
    correct: int,
    wrong: int,
    blank: int = 0,
    exam_type: str | None = None,
    total_questions: int | None = None,
) -> ExamScoreResult:
    """Net + başarı yüzdesi — exam_type aware."""
    c = max(0, int(correct))
    w = max(0, int(wrong))
    b = max(0, int(blank))
    code = (exam_type or "").strip().lower() or "generic"
    penalty = wrong_penalty_for_exam(code)
    net = Decimal(c) - (Decimal(w) * penalty)
    if net < 0:
        net = Decimal("0")
    total = total_questions if total_questions and total_questions > 0 else max(c + w + b, 1)
    success = float((Decimal(c) / Decimal(total)) * 100)
    formula = (
        f"net = doğru - yanlış×{penalty}"
        if penalty > 0
        else "net = doğru (yanlış düşmez)"
    )
    return ExamScoreResult(
        correct=c,
        wrong=w,
        blank=b,
        net=net.quantize(Decimal("0.01")),
        success_pct=round(success, 2),
        penalty_per_wrong=penalty,
        exam_code=code,
        formula=formula,
    )


def compute_exam_net(
    correct: int,
    wrong: int,
    exam_type: str | None = None,
) -> Decimal:
    """Geriye uyum — ExamType enum veya str."""
    et = getattr(exam_type, "value", exam_type)
    return compute_exam_score(correct=correct, wrong=wrong, exam_type=str(et) if et else None).net
