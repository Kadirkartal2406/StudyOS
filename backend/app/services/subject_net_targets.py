"""Subject net vs user target — gap-based priority (not fixed 'weak' labels)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import REVISION_EXAM_MIN_QUESTIONS

# Display-name → official booklet question count
_SUBJECT_CAPACITY: dict[str, dict[str, int]] = {
    "kpss": {
        "türkçe": 30,
        "matematik": 30,
        "tarih": 27,
        "coğrafya": 18,
        "cografya": 18,
        "vatandaşlık": 9,
        "vatandaslik": 9,
        "güncel": 6,
        "guncel": 6,
        "güncel bilgiler": 6,
    },
    "ags": {
        "türkçe": 30,
        "matematik": 30,
        "tarih": 27,
        "coğrafya": 18,
        "cografya": 18,
        "vatandaşlık": 9,
        "güncel": 6,
    },
    "tyt": {
        "türkçe": 40,
        "matematik": 30,
        "geometri": 10,
        "fizik": 7,
        "kimya": 7,
        "biyoloji": 6,
        "tarih": 5,
        "coğrafya": 5,
        "cografya": 5,
        "felsefe": 5,
        "din": 5,
    },
    "lgs": {
        "türkçe": 20,
        "matematik": 20,
        "fen": 20,
        "fen bilimleri": 20,
        "inkılap": 10,
        "inkilap": 10,
        "t.c. inkılap tarihi": 10,
        "din": 10,
        "din kültürü": 10,
        "ingilizce": 10,
    },
    "ales": {"sayısal": 50, "sayisal": 50, "sözel": 50, "sozel": 50},
    "dgs": {"sayısal": 60, "sayisal": 60, "sözel": 60, "sozel": 60},
    "ayt": {
        "matematik": 30,
        "geometri": 10,
        "fizik": 14,
        "kimya": 13,
        "biyoloji": 13,
        "edebiyat": 24,
        "tarih": 21,
        "coğrafya": 17,
        "felsefe": 12,
        "din": 6,
        "ingilizce": 80,
        "yabancı dil": 80,
        "türkçe": 40,
    },
}


def official_subject_question_count(
    *,
    exam_type: str | None,
    subject_name: str,
    fallback: int = 30,
) -> int:
    """Official booklet capacity for a subject display name."""
    exam = (exam_type or "kpss").strip().lower()
    key = (subject_name or "").strip().casefold()
    for prefix in ("tyt ", "ayt "):
        if key.startswith(prefix):
            key = key[len(prefix) :]
    table = _SUBJECT_CAPACITY.get(exam) or _SUBJECT_CAPACITY.get("kpss", {})
    if key in table:
        return int(table[key])
    if exam == "yks":
        for alt in ("tyt", "ayt"):
            t = _SUBJECT_CAPACITY.get(alt, {})
            if key in t:
                return int(t[key])
    return max(1, int(fallback))


# Canonical booklet totals (aliases in _SUBJECT_CAPACITY must not double-count).
_EXAM_TOTAL_QUESTIONS: dict[str, int] = {
    "kpss": 120,
    "ags": 120,
    "tyt": 120,
    "lgs": 90,
    "ales": 100,
    "dgs": 120,
    "ayt": 160,  # rough upper bound across tracks; per-subject caps still apply
}


def exam_total_question_count(exam_type: str | None) -> int:
    exam = (exam_type or "kpss").strip().lower()
    if exam == "yks":
        return exam_total_question_count("tyt") + 80
    if exam in _EXAM_TOTAL_QUESTIONS:
        return _EXAM_TOTAL_QUESTIONS[exam]
    table = _SUBJECT_CAPACITY.get(exam) or _SUBJECT_CAPACITY.get("kpss", {})
    # Collapse ASCII/diacritic aliases: keep max capacity per normalized stem
    by_stem: dict[str, int] = {}
    for name, cap in table.items():
        stem = (
            name.replace("ı", "i")
            .replace("ğ", "g")
            .replace("ü", "u")
            .replace("ş", "s")
            .replace("ö", "o")
            .replace("ç", "c")
            .strip()
        )
        by_stem[stem] = max(by_stem.get(stem, 0), int(cap))
    total = sum(by_stem.values())
    return total if total > 0 else 120


@dataclass(frozen=True)
class SubjectTargetGap:
    subject: str
    average_net: float
    question_count: int
    target_net: float
    gap: float  # target - average (>0 => below target)

    @property
    def below_target(self) -> bool:
        return self.gap > 0.05

    @property
    def on_or_above_target(self) -> bool:
        return self.gap <= 0.05


def compute_subject_target_net(
    *,
    user_target_net: float | None,
    subject_question_count: int,
    total_question_count: int,
) -> float:
    """
    Map overall exam net goal onto one subject's sitting.

    Full-exam goals (e.g. KPSS 85) are distributed by question share.
    Never assign the full exam target as a single subject's hedef.
    """
    q = max(int(subject_question_count), 1)
    if user_target_net is None or user_target_net <= 0:
        return round(q * 0.70, 2)
    t = float(user_target_net)
    total_q = max(int(total_question_count), q)
    # Full-exam style goal: distribute by share of booklet
    if t > q * 1.05 or t > 40:
        return round(min(float(q), t * (q / total_q)), 2)
    # Explicit per-subject style: "bu dersten 20 net"
    return round(min(t, float(q)), 2)


async def resolve_user_target_net(db: AsyncSession, user_id: uuid.UUID) -> float | None:
    """Active exam target_net, else goal with 'net' in title/description."""
    from app.services.goal_service import GoalService
    from app.services.learning_profile_service import LearningProfileService

    profile = LearningProfileService(db)
    student = await profile.ensure_student(user_id)
    targets = await profile.repo.list_exam_targets(user_id)
    active = profile.resolve_active_exam_type(student, targets)
    focus = None
    if active:
        focus = next((t for t in targets if str(t.exam_type) == active), None)
    if focus is None:
        focus = next((t for t in targets if t.is_primary), targets[0] if targets else None)
    if focus and focus.target_net and float(focus.target_net) > 0:
        return float(focus.target_net)

    try:
        goals = await GoalService(db).list_active(user_id)
        for g in goals:
            title = (g.title or "").lower()
            desc = (g.description or "").lower()
            if "net" in title or "net" in desc:
                if g.target_value and float(g.target_value) > 0:
                    return float(g.target_value)
    except Exception:
        pass
    return None


def gaps_from_trends(
    *,
    by_subject: list,
    user_target_net: float | None,
    min_questions: int = REVISION_EXAM_MIN_QUESTIONS,
    exam_type: str | None = None,
) -> list[SubjectTargetGap]:
    """by_subject items need: subject, average_net, question_count."""
    eligible = [r for r in by_subject if getattr(r, "question_count", 0) >= min_questions]
    total_q = exam_total_question_count(exam_type) if exam_type else 0
    if total_q <= 0:
        total_q = sum(int(getattr(r, "question_count", 0) or 0) for r in eligible) or 0
    out: list[SubjectTargetGap] = []
    for r in eligible:
        name = str(getattr(r, "subject", "") or "")
        recorded_q = int(getattr(r, "question_count", 0) or 0)
        q = official_subject_question_count(
            exam_type=exam_type, subject_name=name, fallback=recorded_q or 30
        )
        target = compute_subject_target_net(
            user_target_net=user_target_net,
            subject_question_count=q,
            total_question_count=total_q or q,
        )
        avg = float(r.average_net)
        out.append(
            SubjectTargetGap(
                subject=name,
                average_net=avg,
                question_count=q,
                target_net=target,
                gap=round(target - avg, 2),
            )
        )
    return out


def below_target_sorted(gaps: list[SubjectTargetGap]) -> list[SubjectTargetGap]:
    return sorted(
        [g for g in gaps if g.below_target],
        key=lambda g: g.gap,
        reverse=True,
    )


def on_track_sorted(gaps: list[SubjectTargetGap]) -> list[SubjectTargetGap]:
    return sorted(
        [g for g in gaps if g.on_or_above_target],
        key=lambda g: g.gap,
    )
