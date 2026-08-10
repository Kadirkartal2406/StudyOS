"""Subject net vs user target — gap-based priority (not fixed 'weak' labels)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import REVISION_EXAM_MIN_QUESTIONS
from app.core.exam_identity import canonicalize_exam_type
from app.services.exam_catalog.distributions import (
    EXAM_TOTALS,
    SUBJECT_QUOTAS,
    resolve_quota_key,
)

# Display-name → official booklet question count (derived from SUBJECT_QUOTAS)
def _display_capacity_table() -> dict[str, dict[str, int]]:
    """Build name-keyed capacity tables from SSOT subject quotas."""
    name_by_code = {
        "kpss_turkce": "türkçe",
        "kpss_matematik": "matematik",
        "kpss_tarih": "tarih",
        "kpss_cografya": "coğrafya",
        "kpss_vatandaslik": "vatandaşlık",
        "kpss_guncel": "güncel",
        "tyt_turkce": "türkçe",
        "tyt_matematik": "matematik",
        "tyt_geometri": "geometri",
        "tyt_fizik": "fizik",
        "tyt_kimya": "kimya",
        "tyt_biyoloji": "biyoloji",
        "tyt_tarih": "tarih",
        "tyt_cografya": "coğrafya",
        "tyt_felsefe": "felsefe",
        "tyt_din": "din",
        "ayt_matematik": "matematik",
        "ayt_geometri": "geometri",
        "ayt_fizik": "fizik",
        "ayt_kimya": "kimya",
        "ayt_biyoloji": "biyoloji",
        "ayt_edebiyat": "edebiyat",
        "ayt_tarih_1": "tarih",
        "ayt_cografya_1": "coğrafya",
        "ayt_tarih_2": "tarih",
        "ayt_cografya_2": "coğrafya",
        "ayt_felsefe": "felsefe",
        "ayt_din": "din",
        "ydt_ingilizce": "ingilizce",
        "lgs_turkce": "türkçe",
        "lgs_matematik": "matematik",
        "lgs_fen": "fen",
        "lgs_inkilap": "inkılap",
        "lgs_din": "din",
        "lgs_ingilizce": "ingilizce",
        "ags_turkce": "türkçe",
        "ags_matematik": "matematik",
        "ales_sayisal": "sayısal",
        "ales_sozel": "sözel",
        "dgs_sayisal": "sayısal",
        "dgs_sozel": "sözel",
        "yds_ingilizce": "ingilizce",
        "yokdil_ingilizce": "ingilizce",
    }
    out: dict[str, dict[str, int]] = {}
    for exam_key, quotas in SUBJECT_QUOTAS.items():
        table: dict[str, int] = {}
        for code, n in quotas.items():
            nm = name_by_code.get(code, code)
            table[nm] = table.get(nm, 0) + int(n)
            # ASCII aliases
            ascii_nm = (
                nm.replace("ı", "i")
                .replace("ğ", "g")
                .replace("ü", "u")
                .replace("ş", "s")
                .replace("ö", "o")
                .replace("ç", "c")
            )
            if ascii_nm != nm:
                table[ascii_nm] = table.get(ascii_nm, 0) + int(n)
        if exam_key.startswith("kpss_"):
            out.setdefault("kpss", {}).update(table)
        out[exam_key] = table
    # Convenience aliases
    if "kpss" in out:
        out["kpss"]["güncel bilgiler"] = out["kpss"].get("güncel", 6)
    if "lgs" in out:
        out["lgs"]["fen bilimleri"] = out["lgs"].get("fen", 20)
        out["lgs"]["din kültürü"] = out["lgs"].get("din", 10)
    return out


_SUBJECT_CAPACITY: dict[str, dict[str, int]] = _display_capacity_table()


def _capacity_exam_key(exam_type: str | None) -> str:
    exam = canonicalize_exam_type(exam_type or "kpss", None)
    return resolve_quota_key(exam, None)


def official_subject_question_count(
    *,
    exam_type: str | None,
    subject_name: str,
    fallback: int = 30,
) -> int:
    """Official booklet capacity for a subject display name."""
    exam = _capacity_exam_key(exam_type)

    if exam in {"yds_ingilizce", "ydt_ingilizce", "yokdil_ingilizce"} or exam.startswith("yokdil_"):
        return 80

    key = (subject_name or "").strip().casefold()
    for prefix in ("tyt ", "ayt ", "ags ", "lgs "):
        if key.startswith(prefix):
            key = key[len(prefix) :]
    table = _SUBJECT_CAPACITY.get(exam) or {}
    if key in table:
        return int(table[key])
    if exam_type and str(exam_type).strip().lower() == "yks":
        for alt in ("tyt", "ayt_sayisal", "ayt"):
            t = _SUBJECT_CAPACITY.get(alt, {})
            if key in t:
                return int(t[key])
    if not table and str(exam).startswith("ayt"):
        table = _SUBJECT_CAPACITY.get("ayt_sayisal", {})
        if key in table:
            return int(table[key])
    if not table:
        table = _SUBJECT_CAPACITY.get("kpss", {})
        if key in table:
            return int(table[key])
    return max(1, int(fallback))


def exam_total_question_count(exam_type: str | None) -> int:
    exam = canonicalize_exam_type(exam_type or "kpss", None)
    key = resolve_quota_key(exam, None)
    if key in EXAM_TOTALS:
        return EXAM_TOTALS[key]
    if exam.startswith("kpss_"):
        return 120
    if exam in {"yds_ingilizce", "ydt_ingilizce"} or exam.startswith("yokdil"):
        return 80
    if exam == "yks":
        return exam_total_question_count("tyt") + 80
    table = _SUBJECT_CAPACITY.get(key) or _SUBJECT_CAPACITY.get("kpss", {})
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
