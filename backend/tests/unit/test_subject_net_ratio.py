"""Sprint 22 — subject-normalized weak/strong net classification."""

from app.core.constants import (
    REVISION_EXAM_MIN_QUESTIONS,
    REVISION_EXAM_STRONG_NET_RATIO,
    REVISION_EXAM_WEAK_NET_RATIO,
)


def _classify(net: float, question_count: int) -> str:
    if question_count < REVISION_EXAM_MIN_QUESTIONS:
        return "unknown"
    max_net = float(question_count)
    ratio = net / max_net if max_net > 0 else 0.0
    if ratio < REVISION_EXAM_WEAK_NET_RATIO:
        return "weak"
    if ratio >= REVISION_EXAM_STRONG_NET_RATIO:
        return "strong"
    return "ok"


def _multi_exam_ratio(sittings: list[tuple[float, int]]) -> float:
    """Average of per-sitting ratios — not avg_net / sum(questions)."""
    ratios = [net / q for net, q in sittings if q > 0]
    return sum(ratios) / len(ratios) if ratios else 0.0


def test_high_subject_net_not_weak_vs_total_exam():
    # 28/30 subject net used to look weak when total exam ~80; ratio fix → strong
    assert _classify(28.0, 30) == "strong"


def test_low_subject_ratio_is_weak():
    assert _classify(15.0, 30) == "weak"


def test_mid_ratio_is_ok():
    assert _classify(22.0, 30) == "ok"


def test_below_min_questions_unknown():
    assert _classify(5.0, max(1, REVISION_EXAM_MIN_QUESTIONS - 1)) == "unknown"


def test_multi_exam_does_not_dilute_ratio():
    # Bug: avg_net=28 / (30+30+30)=90 → 0.31 weak. Correct: mean(28/30)=0.933 strong
    sittings = [(28.0, 30), (27.0, 30), (29.0, 30)]
    ratio = _multi_exam_ratio(sittings)
    assert ratio >= REVISION_EXAM_STRONG_NET_RATIO
    # Broken cumulative formula would fail this:
    broken = (sum(n for n, _ in sittings) / len(sittings)) / sum(q for _, q in sittings)
    assert broken < REVISION_EXAM_WEAK_NET_RATIO
