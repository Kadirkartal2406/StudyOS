"""
StudyOS — Adaptive Planner Engine
Sprint-2.7 + Sprint 22: Rule-based haftalık plan; subject-normalized weak nets;
topic-level blocks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    PLANNER_FALLBACK_BY_EXAM,
    PLANNER_FALLBACK_SUBJECTS,
    PLANNER_MAX_RESOURCES_PER_ITEM,
    PLANNER_MIN_MINUTES_PER_BLOCK,
    PLANNER_QUESTIONS_PER_HOUR,
    REVISION_EXAM_MIN_QUESTIONS,
)
from app.models.memory import MemoryCategory
from app.models.study_resource import ResourceType
from app.schemas.planner import PlannerGenerateRequest
from app.services.ai.insight_engine import InsightEngine
from app.services.ai.rule_engine import RuleEngine
from app.services.confidence_engine import ConfidenceEngine
from app.services.exam_service import ExamService
from app.services.goal_service import GoalService
from app.services.memory_service import MemoryService
from app.services.question_record_service import QuestionRecordService
from app.services.study_resource_service import StudyResourceService
from app.services.subject_net_targets import (
    below_target_sorted,
    compute_subject_target_net,
    exam_total_question_count,
    gaps_from_trends,
    official_subject_question_count,
    on_track_sorted,
    resolve_user_target_net,
)


def _week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _fallback_subjects_for_exam(exam: str | None) -> tuple[str, ...]:
    key = (exam or "").strip().lower()
    if hasattr(exam, "value"):
        key = str(getattr(exam, "value", exam)).strip().lower()
    return PLANNER_FALLBACK_BY_EXAM.get(key) or PLANNER_FALLBACK_BY_EXAM.get(
        "kpss", PLANNER_FALLBACK_SUBJECTS
    )


def _parse_subject_nets_from_reason(reason: str | None) -> dict[str, float]:
    """baseline_reason içinden 'Ders netleri: Matematik=40; Türkçe=55' okur."""
    if not reason or "Ders netleri:" not in reason:
        return {}
    chunk = reason.split("Ders netleri:", 1)[1]
    chunk = chunk.split("·")[0].strip()
    out: dict[str, float] = {}
    for part in chunk.replace(",", ";").split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        name, raw = part.split("=", 1)
        try:
            out[name.strip()] = float(raw.strip().replace(",", "."))
        except ValueError:
            continue
    return out


def _parse_labeled_subjects(reason: str | None, label: str) -> list[str]:
    """'Zayıf: Matematik, Tarih' / 'Güçlü: Türkçe' satırlarını ayıkla."""
    if not reason or f"{label}:" not in reason:
        return []
    chunk = reason.split(f"{label}:", 1)[1]
    chunk = chunk.split("·")[0].strip()
    return [p.strip() for p in chunk.replace(";", ",").split(",") if p.strip()]


class AdaptivePlannerEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.insights = InsightEngine(db)
        self.rules = RuleEngine()
        self.exams = ExamService(db)
        self.questions = QuestionRecordService(db)
        self.goals = GoalService(db)
        self.memory = MemoryService(db)
        self.resources = StudyResourceService(db)
        self.confidence = ConfidenceEngine(db)

    async def generate(
        self, user_id: uuid.UUID, req: PlannerGenerateRequest
    ) -> dict[str, Any]:
        if (
            req.target_exam is None
            or req.target_net is None
            or not req.available_days
            or req.available_hours is None
        ):
            raise ValueError("PlannerGenerateRequest unresolved")

        today = datetime.now(UTC).date()
        week_start = _week_monday(today)

        ctx = await self.insights.build_context(user_id)
        recs = self.rules.generate(ctx)
        exam_stats = await self.exams.get_statistics(user_id)
        exam_trends = await self.exams.get_trends(user_id)
        q_subjects = await self.questions.get_subjects_distribution(user_id)

        target_net = float(req.target_net)
        goals = await self.goals.list_active(user_id)
        goal_hint = None
        for g in goals:
            title = g.title.lower()
            desc = (g.description or "").lower()
            if "net" in title or "net" in desc:
                goal_hint = float(g.target_value)
                break

        current_net = exam_stats.last_exam_net or float(ctx.total_net or 0)
        gap = max(0.0, target_net - current_net)

        weak: list[str] = []
        strong: list[str] = []
        exam_strong: set[str] = set()
        exam_below: set[str] = set()
        gap_by_subject: dict[str, float] = {}
        target_by_subject: dict[str, float] = {}

        user_target = await resolve_user_target_net(self.db, user_id)
        if goal_hint and (user_target is None or goal_hint > 0):
            # Prefer explicit goal "net" when present
            user_target = goal_hint
        if req.target_net:
            # Planner request target is authoritative for this generate
            user_target = float(req.target_net)

        gaps = gaps_from_trends(
            by_subject=exam_trends.by_subject,
            user_target_net=user_target,
            exam_type=str(req.target_exam or ""),
        )
        for g in below_target_sorted(gaps):
            exam_below.add(g.subject)
            gap_by_subject[g.subject] = g.gap
            target_by_subject[g.subject] = g.target_net
        for g in on_track_sorted(gaps):
            exam_strong.add(g.subject)
            gap_by_subject[g.subject] = g.gap
            target_by_subject[g.subject] = g.target_net

        for s, _rate in ctx.low_accuracy_subjects:
            if s not in exam_strong and s not in weak:
                weak.append(s)
        for s in ctx.neglected_subjects:
            if s not in exam_strong and s not in weak:
                weak.append(s)

        for s in exam_below:
            if s not in weak:
                weak.append(s)
        for s in exam_strong:
            if s not in strong:
                strong.append(s)
            if s in weak:
                weak = [x for x in weak if x != s]

        for item in q_subjects.items[:8]:
            if item.name in exam_strong:
                if item.name not in strong:
                    strong.append(item.name)
                continue
            # Question accuracy only if no exam signal for this subject
            if item.name in exam_below or item.name in gap_by_subject:
                continue
            if item.correct_rate < 55 and item.name not in weak:
                weak.append(item.name)
            elif item.correct_rate >= 75 and item.name not in strong:
                strong.append(item.name)

        prefs: list[str] = []
        try:
            mem_list = await self.memory.list_memories(user_id, active_only=True)
            prefs = [
                m.content
                for m in mem_list.items
                if m.category == MemoryCategory.PREFERENCE
            ][:8]
        except Exception:
            prefs = []

        used_fallback = False
        if not weak and not strong:
            used_fallback = True
            # Not "weak" — neutral schedule seed when no exam/accuracy signal yet
            weak = []
            strong = []

        # Onboarding ders netleri + zayıf/güçlü beyan → hedeften uzaklık
        try:
            from app.repositories.learning_profile_repository import (
                LearningProfileRepository,
            )

            student = await LearningProfileRepository(self.db).get_student(user_id)
            reason = getattr(student, "baseline_reason", None) if student else None
            for s in _parse_labeled_subjects(reason, "Zayıf"):
                if s not in weak:
                    weak.append(s)
            for s in _parse_labeled_subjects(reason, "Güçlü"):
                if s not in strong and s not in weak:
                    strong.append(s)
            declared = _parse_subject_nets_from_reason(reason)
            if declared and user_target:
                exam_key_local = str(
                    getattr(req.target_exam, "value", None) or req.target_exam or "kpss"
                )
                total_q = exam_total_question_count(exam_key_local)
                for subj, cur in declared.items():
                    q = official_subject_question_count(
                        exam_type=exam_key_local, subject_name=subj
                    )
                    tgt = compute_subject_target_net(
                        user_target_net=float(user_target),
                        subject_question_count=q,
                        total_question_count=total_q,
                    )
                    g = float(tgt) - float(cur)
                    gap_by_subject[subj] = g
                    target_by_subject[subj] = float(tgt)
                    if g > 2 and subj not in weak:
                        weak.append(subj)
                    elif g <= 0 and subj not in strong and subj not in weak:
                        strong.append(subj)
                    if current_net <= 0:
                        current_net = max(current_net, float(cur))
            if declared and current_net <= 0:
                current_net = sum(declared.values()) / max(1, len(declared))
                gap = max(0.0, target_net - current_net)
            if weak or strong:
                used_fallback = False
        except Exception:
            pass

        exam_key = getattr(req.target_exam, "value", None) or str(req.target_exam)
        fallback_subjects = _fallback_subjects_for_exam(exam_key)
        total_q = exam_total_question_count(str(exam_key))

        def _ensure_subject_target(name: str) -> float:
            if name in target_by_subject:
                return float(target_by_subject[name])
            q = official_subject_question_count(
                exam_type=str(exam_key), subject_name=name
            )
            tgt = compute_subject_target_net(
                user_target_net=user_target or target_net,
                subject_question_count=q,
                total_question_count=total_q,
            )
            target_by_subject[name] = tgt
            if name not in gap_by_subject:
                gap_by_subject[name] = round(tgt - 0.0, 2)
            return tgt

        # Topic pool: low-confidence topics preferred; fallback catalog by subject name
        topic_by_subject = await self._resolve_topics_for_subjects(
            user_id, (weak[:6] + strong[:3]) or list(fallback_subjects)
        )

        subject_weights: list[tuple[str, float, str]] = []
        for s in weak[:6]:
            tgt = _ensure_subject_target(s)
            gap_s = float(gap_by_subject.get(s, tgt) or tgt)
            current_s = max(0.0, float(tgt) - gap_s)
            reason = (
                f"{s}: hedef {tgt:.0f} net · durum {current_s:.0f} net "
                f"(genel sınav hedefi {target_net:.0f})."
            )
            subject_weights.append((s, 3.0, reason))
        for s in strong[:3]:
            tgt = _ensure_subject_target(s)
            gap_s = float(gap_by_subject.get(s, 0.0) or 0.0)
            current_s = max(0.0, float(tgt) - gap_s)
            reason = (
                f"{s}: hedef {tgt:.0f} net · durum {current_s:.0f} net — bakım dozu."
            )
            subject_weights.append((s, 1.0, reason))
        if not subject_weights:
            used_fallback = True
            for s in fallback_subjects:
                tgt = _ensure_subject_target(s)
                subject_weights.append(
                    (
                        s,
                        2.0,
                        f"{s}: hedef ~{tgt:.0f} net (genel {target_net:.0f}) — dengeli dağıtım.",
                    ),
                )

        # Sınava ait olmayan dersleri (ör. KPSS’te Fen) ele
        allowed = set(fallback_subjects)
        if allowed:
            filtered = [x for x in subject_weights if x[0] in allowed]
            if filtered:
                subject_weights = filtered
            else:
                used_fallback = True
                subject_weights = [
                    (s, 2.0, f"{exam_key.upper()} şablonu: {s}")
                    for s in fallback_subjects
                ]

        # available_hours = günlük süre
        minutes_per_day = max(
            PLANNER_MIN_MINUTES_PER_BLOCK,
            int(float(req.available_hours) * 60),
        )
        # Önümüzdeki 14 günde uygun hafta günlerinden en fazla 7 çalışma günü
        ordered_dates: list[date] = []
        cursor = today
        while len(ordered_dates) < 7 and (cursor - today).days < 14:
            if cursor.weekday() in req.available_days:
                ordered_dates.append(cursor)
            cursor += timedelta(days=1)
        if not ordered_dates:
            ordered_dates = [today]

        total_hours = (minutes_per_day / 60.0) * len(ordered_dates)
        weight_sum = sum(w for _, w, _ in subject_weights) or 1.0

        all_resources = await self.resources.list_resources(user_id)
        resource_pool = list(all_resources.items)

        items: list[dict[str, Any]] = []
        # Ağırlığa göre sıralı döngü — zayıf dersler önde
        subj_cycle = sorted(subject_weights, key=lambda x: (-x[1], x[0]))
        idx = 0
        rules_applied = [r.code for r in recs[:8]]
        topic_rr: dict[str, int] = {}

        for day_i, day in enumerate(ordered_dates):
            if minutes_per_day >= 180 and len(subj_cycle) >= 3:
                blocks = 3
            elif minutes_per_day >= 90 and len(subj_cycle) > 1:
                blocks = 2
            else:
                blocks = 1
            day_cursor_min = 9 * 60
            block_min = max(
                PLANNER_MIN_MINUTES_PER_BLOCK, minutes_per_day // blocks
            )
            used_today: set[str] = set()
            for _ in range(blocks):
                # Aynı güne aynı dersi tekrarlama (mümkünse)
                pick_i = idx % len(subj_cycle)
                tries = 0
                while (
                    subj_cycle[pick_i][0] in used_today
                    and tries < len(subj_cycle)
                    and len(used_today) < len(subj_cycle)
                ):
                    pick_i = (pick_i + 1) % len(subj_cycle)
                    tries += 1
                subject, weight, base_reason = subj_cycle[pick_i]
                used_today.add(subject)
                idx = pick_i + 1

                gap_s = gap_by_subject.get(subject)
                q_count = max(10, int(block_min / 60 * PLANNER_QUESTIONS_PER_HOUR))
                if (gap_s is not None and gap_s > 8) or gap > 15:
                    q_count = int(q_count * 1.25)
                q_count = min(80, q_count)

                topics = topic_by_subject.get(subject) or []
                topic_name = None
                topic_code = None
                subject_code = None
                if topics:
                    ti = topic_rr.get(subject, 0) % len(topics)
                    topic_rr[subject] = ti + 1
                    pick = topics[ti]
                    topic_name = pick.get("topic_name")
                    topic_code = pick.get("topic_code")
                    subject_code = pick.get("subject_code")

                matched = self._match_resources(subject, resource_pool)
                reason_parts = [base_reason]
                if topic_name:
                    reason_parts.append(f"Odak konu: {topic_name}.")
                if gap_s is not None and gap_s > 0:
                    reason_parts.append(
                        f"Bu derste hedefe {gap_s:.0f} net uzaklık var."
                    )
                elif gap > 0 and day_i == 0:
                    reason_parts.append(
                        f"Genel hedef {target_net:.0f} net; güncel ~{current_net:.0f}."
                    )
                if matched:
                    reason_parts.append(
                        f"İlgili kaynak: {matched[0]['title']}."
                    )

                start_h, start_m = divmod(day_cursor_min, 60)
                end_total = day_cursor_min + block_min
                end_h, end_m = divmod(end_total, 60)
                start_time = f"{start_h:02d}:{start_m:02d}"
                end_time = f"{end_h:02d}:{end_m:02d}"
                day_cursor_min = end_total + 15

                title = (
                    f"{subject} · {topic_name}"
                    if topic_name
                    else f"{subject} çalışması"
                )
                items.append(
                    {
                        "study_date": day.isoformat(),
                        "title": title,
                        "subject": subject,
                        "topic": topic_name,
                        "subject_code": subject_code,
                        "topic_code": topic_code,
                        "target_question_count": q_count,
                        "estimated_minutes": block_min,
                        "start_time": start_time,
                        "end_time": end_time,
                        "resource_ids": [m["id"] for m in matched],
                        "resource_titles": [m["title"] for m in matched],
                        "reason": " ".join(reason_parts),
                    }
                )

        overview = (
            f"{str(exam_key).upper()} · hedef {target_net:.0f} net. "
            f"{len(ordered_dates)} gün · günde ~{minutes_per_day} dk "
            f"(toplam ~{total_hours:.1f} saat). "
            f"Öncelik: {', '.join(weak[:3]) or ', '.join(fallback_subjects[:3])}."
        )
        if used_fallback:
            overview += " İlk plan sınav derslerine göre dengelendi; seviye testi ve denemelerle netleşecek."

        return {
            "week_start": week_start.isoformat(),
            "items": items,
            "summary": {
                "weak_subjects": weak[:6],
                "strong_subjects": strong[:4],
                "target_net": target_net,
                "current_net": current_net,
                "gap": gap,
                "total_hours": total_hours,
                "minutes_per_day": minutes_per_day,
                "used_fallback_template": used_fallback,
                "goal_hint_net": goal_hint,
                "preferences": prefs[:5],
            },
            "rationale": {
                "overview": overview,
                "rules_applied": rules_applied,
                "weight_sum": weight_sum,
            },
        }

    async def _resolve_topics_for_subjects(
        self, user_id: uuid.UUID, subjects: list[str]
    ) -> dict[str, list[dict[str, str]]]:
        """Map subject display name → topic picks (confidence first, then catalog)."""
        from app.repositories.learning_profile_repository import LearningProfileRepository

        repo = LearningProfileRepository(self.db)
        out: dict[str, list[dict[str, str]]] = {s: [] for s in subjects}

        low = await self.confidence.list_low_confidence_topics(user_id, limit=40)
        for conf in low:
            topic = await repo.get_topic_by_code(conf.topic_code)
            catalog_subj = await repo.get_catalog_by_code(conf.subject_code)
            subj_name = catalog_subj.name if catalog_subj else conf.subject_code
            # Match to planner subject labels
            key = None
            for s in subjects:
                if s.casefold() == subj_name.casefold() or s.casefold() in conf.subject_code.casefold():
                    key = s
                    break
            if key is None:
                continue
            out.setdefault(key, []).append(
                {
                    "subject_code": conf.subject_code,
                    "topic_code": conf.topic_code,
                    "topic_name": topic.name if topic else conf.topic_code,
                }
            )

        # Fill missing subjects from catalog first topics
        for s in subjects:
            if out.get(s):
                continue
            # Find subject catalog by name
            catalogs = await repo.list_catalog(active_only=True)
            match = next(
                (c for c in catalogs if c.name.casefold() == s.casefold()),
                None,
            )
            if match is None:
                match = next(
                    (c for c in catalogs if s.casefold() in c.name.casefold()),
                    None,
                )
            if match is None:
                continue
            topics = await repo.list_topics(match.code, active_only=True)
            for t in topics[:3]:
                out.setdefault(s, []).append(
                    {
                        "subject_code": match.code,
                        "topic_code": t.code,
                        "topic_name": t.name,
                    }
                )
        return out

    def _match_resources(
        self, subject: str, pool: list
    ) -> list[dict[str, str]]:
        needle = subject.casefold()
        hits: list[dict[str, str]] = []
        for r in pool:
            title = (r.title or "").casefold()
            desc = (r.description or "").casefold() if getattr(r, "description", None) else ""
            if needle in title or needle in desc:
                if r.resource_type in (
                    ResourceType.YOUTUBE,
                    ResourceType.VIDEO,
                    ResourceType.WEBSITE,
                    ResourceType.PDF,
                ):
                    hits.append({"id": str(r.id), "title": r.title})
            if len(hits) >= PLANNER_MAX_RESOURCES_PER_ITEM:
                break
        return hits
