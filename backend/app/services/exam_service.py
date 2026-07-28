"""
StudyOS — Exam Service
Sprint-2.6 (Meeting-024) — S-13 deneme takibi.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    EXAM_MILESTONE_FIRST,
    EXAM_MILESTONE_TENTH,
)
from app.core.exceptions import NotFoundError, ValidationError
from app.models.activity import ActivityEventType
from app.models.exam import Exam, ExamResult
from app.models.question_record import ExamType
from app.repositories.exam_repository import ExamRepository
from app.schemas.exam import (
    DashboardExamSummary,
    ExamCreate,
    ExamDetailRead,
    ExamListResponse,
    ExamRead,
    ExamResultCreate,
    ExamResultRead,
    ExamResultsReplace,
    ExamStatistics,
    ExamSubjectTrend,
    ExamTrendPoint,
    ExamTrends,
    ExamUpdate,
    ExamWriteResponse,
)
from app.services.activity_service import ActivityService
from app.services.exam_net import compute_exam_net


def _week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


class ExamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamRepository(db)
        self.activity = ActivityService(db)

    def _result_totals(self, results: list[ExamResult]) -> tuple[Decimal, int]:
        total_net = sum((r.net_score for r in results), Decimal("0"))
        total_q = sum(r.question_count for r in results)
        return Decimal(total_net), total_q

    def _to_result_read(self, row: ExamResult) -> ExamResultRead:
        return ExamResultRead.model_validate(row)

    def _to_read(self, exam: Exam) -> ExamRead:
        results = list(exam.results or [])
        total_net, total_q = self._result_totals(results)
        return ExamRead(
            id=exam.id,
            user_id=exam.user_id,
            title=exam.title,
            exam_type=exam.exam_type,
            exam_date=exam.exam_date,
            duration_minutes=exam.duration_minutes,
            notes=exam.notes,
            total_net=total_net.quantize(Decimal("0.01")),
            total_questions=total_q,
            result_count=len(results),
            created_at=exam.created_at,
            updated_at=exam.updated_at,
        )

    def _to_detail(self, exam: Exam) -> ExamDetailRead:
        base = self._to_read(exam)
        return ExamDetailRead(
            **base.model_dump(),
            results=[self._to_result_read(r) for r in (exam.results or [])],
        )

    def _build_result_rows(
        self, exam_id: uuid.UUID, items: list[ExamResultCreate], exam_type: ExamType
    ) -> list[ExamResult]:
        rows: list[ExamResult] = []
        for item in items:
            subject = item.subject.strip()
            if not subject:
                raise ValidationError("Ders adı zorunlu", field="subject")
            rows.append(
                ExamResult(
                    exam_id=exam_id,
                    subject=subject,
                    correct_count=item.correct_count,
                    wrong_count=item.wrong_count,
                    blank_count=item.blank_count,
                    question_count=item.question_count,
                    duration_minutes=item.duration_minutes,
                    net_score=compute_exam_net(
                        item.correct_count, item.wrong_count, exam_type
                    ),
                )
            )
        return rows

    async def _milestones_after_create(
        self, user_id: uuid.UUID, new_exam_id: uuid.UUID, new_net: Decimal
    ) -> list[str]:
        count = await self.repo.count_for_user(user_id)
        milestones: list[str] = []
        if count == EXAM_MILESTONE_FIRST:
            milestones.append("first_exam")
        if count == EXAM_MILESTONE_TENTH:
            milestones.append("tenth_exam")
        all_exams = await self.repo.list_for_user(user_id, limit=500)
        other_nets: list[Decimal] = []
        for ex in all_exams:
            if ex.id == new_exam_id:
                continue
            net, _ = self._result_totals(list(ex.results or []))
            other_nets.append(net)
        if other_nets and new_net > max(other_nets):
            milestones.append("new_record_net")
        return milestones

    async def list_exams(
        self, user_id: uuid.UUID, *, exam_type: ExamType | None = None
    ) -> ExamListResponse:
        items = await self.repo.list_for_user(
            user_id, exam_type=str(exam_type) if exam_type else None
        )
        return ExamListResponse(items=[self._to_read(i) for i in items])

    async def get_exam(self, exam_id: uuid.UUID, user_id: uuid.UUID) -> ExamDetailRead:
        exam = await self.repo.get_for_user(exam_id, user_id)
        if exam is None:
            raise NotFoundError("Deneme", str(exam_id))
        return self._to_detail(exam)

    async def create_exam(self, user_id: uuid.UUID, data: ExamCreate) -> ExamWriteResponse:
        title = data.title.strip()
        if not title:
            raise ValidationError("Başlık zorunlu", field="title")
        exam = Exam(
            user_id=user_id,
            title=title,
            exam_type=data.exam_type,
            exam_date=data.exam_date,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
        )
        exam = await self.repo.add(exam)
        if data.results:
            for row in self._build_result_rows(exam.id, data.results, data.exam_type):
                self.db.add(row)
            await self.db.flush()
        exam = await self.repo.get_for_user(exam.id, user_id)
        assert exam is not None
        total_net, _ = self._result_totals(list(exam.results or []))
        milestones = await self._milestones_after_create(user_id, exam.id, total_net)
        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.EXAM_COMPLETED,
            title=f"Deneme kaydedildi: {exam.title}",
            description=f"Net {total_net}",
            metadata={
                "exam_id": str(exam.id),
                "exam_type": str(exam.exam_type),
                "total_net": float(total_net),
                "exam_date": str(exam.exam_date),
                "milestones": milestones,
            },
        )
        from app.schemas.achievement import AchievementCheckRequest
        from app.services.achievement_service import AchievementService

        await AchievementService(self.db).check(
            user_id,
            AchievementCheckRequest(
                event="exam_completed",
                context={"milestones": milestones, "exam_milestones": milestones},
            ),
        )
        from app.services.goal_progress_service import GoalProgressEvent, GoalProgressService

        subject_nets = {
            r.subject: float(r.net_score) for r in (exam.results or [])
        }
        await GoalProgressService(self.db).apply_event(
            user_id,
            GoalProgressEvent(
                kind="exam_recorded",
                amount=float(total_net),
                exam_type=str(exam.exam_type),
                subject_nets=subject_nets,
                occurred_on=exam.exam_date,
                note=f"Deneme: {exam.title}",
            ),
        )
        return ExamWriteResponse(exam=self._to_detail(exam), milestones=milestones)

    async def update_exam(
        self, exam_id: uuid.UUID, user_id: uuid.UUID, data: ExamUpdate
    ) -> ExamDetailRead:
        exam = await self.repo.get_for_user(exam_id, user_id)
        if exam is None:
            raise NotFoundError("Deneme", str(exam_id))
        payload = data.model_dump(exclude_unset=True)
        if "title" in payload and payload["title"] is not None:
            payload["title"] = payload["title"].strip()
            if not payload["title"]:
                raise ValidationError("Başlık zorunlu", field="title")
        for key, value in payload.items():
            setattr(exam, key, value)
        exam.updated_at = datetime.now(UTC)
        await self.db.flush()
        exam = await self.repo.get_for_user(exam_id, user_id)
        assert exam is not None
        return self._to_detail(exam)

    async def replace_results(
        self, exam_id: uuid.UUID, user_id: uuid.UUID, data: ExamResultsReplace
    ) -> ExamDetailRead:
        exam = await self.repo.get_for_user(exam_id, user_id)
        if exam is None:
            raise NotFoundError("Deneme", str(exam_id))
        exam.results.clear()
        await self.db.flush()
        for row in self._build_result_rows(exam_id, data.results, exam.exam_type):
            exam.results.append(row)
        exam.updated_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(exam, attribute_names=["results"])
        return self._to_detail(exam)

    async def delete_exam(self, exam_id: uuid.UUID, user_id: uuid.UUID) -> None:
        exam = await self.repo.get_for_user(exam_id, user_id, with_results=False)
        if exam is None:
            raise NotFoundError("Deneme", str(exam_id))
        await self.repo.delete(exam)

    async def get_statistics(self, user_id: uuid.UUID) -> ExamStatistics:
        exams = await self.repo.list_for_user(user_id, limit=500)
        if not exams:
            return ExamStatistics()
        nets: list[float] = []
        subject_nets: dict[str, list[float]] = {}
        today = datetime.now(UTC).date()
        week_start = _week_monday(today)
        month_start = today.replace(day=1)
        week_nets: list[float] = []
        month_nets: list[float] = []
        week_count = 0
        month_count = 0

        for ex in exams:
            results = list(ex.results or [])
            net, _ = self._result_totals(results)
            fnet = float(net)
            nets.append(fnet)
            if ex.exam_date >= week_start:
                week_count += 1
                week_nets.append(fnet)
            if ex.exam_date >= month_start:
                month_count += 1
                month_nets.append(fnet)
            for r in results:
                subject_nets.setdefault(r.subject, []).append(float(r.net_score))

        latest = exams[0]
        latest_net, _ = self._result_totals(list(latest.results or []))
        by_subject = {
            s: round(sum(vals) / len(vals), 2) for s, vals in subject_nets.items() if vals
        }
        return ExamStatistics(
            total_exams=len(exams),
            last_exam_title=latest.title,
            last_exam_date=latest.exam_date,
            last_exam_net=round(float(latest_net), 2),
            highest_net=round(max(nets), 2) if nets else 0.0,
            lowest_net=round(min(nets), 2) if nets else 0.0,
            average_net=round(sum(nets) / len(nets), 2) if nets else 0.0,
            week_exams=week_count,
            week_average_net=round(sum(week_nets) / len(week_nets), 2) if week_nets else 0.0,
            month_exams=month_count,
            month_average_net=(
                round(sum(month_nets) / len(month_nets), 2) if month_nets else 0.0
            ),
            by_subject=by_subject,
        )

    async def get_trends(self, user_id: uuid.UUID) -> ExamTrends:
        exams = await self.repo.list_for_user(user_id, limit=100)
        # net_over_time: eski → yeni
        chronological = sorted(exams, key=lambda e: (e.exam_date, e.created_at))
        points: list[ExamTrendPoint] = []
        subject_acc: dict[str, dict] = {}
        cw_b = {"correct": 0, "wrong": 0, "blank": 0}

        for ex in chronological:
            results = list(ex.results or [])
            net, _ = self._result_totals(results)
            points.append(
                ExamTrendPoint(
                    exam_id=ex.id,
                    title=ex.title,
                    exam_date=ex.exam_date,
                    total_net=float(net),
                    exam_type=ex.exam_type,
                )
            )
            for r in results:
                cw_b["correct"] += r.correct_count
                cw_b["wrong"] += r.wrong_count
                cw_b["blank"] += r.blank_count
                acc = subject_acc.setdefault(
                    r.subject,
                    {
                        "nets": [],
                        "q_per_exam": [],
                        "ratios": [],
                        "correct": 0,
                        "wrong": 0,
                        "blank": 0,
                        "count": 0,
                    },
                )
                q = int(r.question_count or 0)
                if q <= 0:
                    q = int(r.correct_count + r.wrong_count + r.blank_count)
                net = float(r.net_score)
                acc["nets"].append(net)
                acc["q_per_exam"].append(q)
                if q > 0:
                    # Per-exam sitting ratio — never avg_net / sum(all questions)
                    acc["ratios"].append(net / q)
                acc["correct"] += r.correct_count
                acc["wrong"] += r.wrong_count
                acc["blank"] += r.blank_count
                acc["count"] += 1

        by_subject = []
        for s, a in sorted(subject_acc.items()):
            exam_count = a["count"] or 1
            avg_net = round(sum(a["nets"]) / len(a["nets"]), 2) if a["nets"] else 0.0
            # Capacity = average questions per exam sitting (e.g. 30), not cumulative
            avg_q = (
                sum(a["q_per_exam"]) / len(a["q_per_exam"])
                if a["q_per_exam"]
                else 0.0
            )
            max_net = float(avg_q)
            if a["ratios"]:
                ratio = round(sum(a["ratios"]) / len(a["ratios"]), 4)
            else:
                ratio = round(avg_net / max_net, 4) if max_net > 0 else 0.0
            by_subject.append(
                ExamSubjectTrend(
                    subject=s,
                    average_net=avg_net,
                    exam_count=exam_count,
                    total_correct=a["correct"],
                    total_wrong=a["wrong"],
                    total_blank=a["blank"],
                    question_count=int(round(avg_q)),
                    max_net=round(max_net, 2),
                    net_ratio=ratio,
                )
            )
        return ExamTrends(
            net_over_time=points,
            by_subject=by_subject,
            correct_wrong_blank=cw_b,
        )

    async def dashboard_summary(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> DashboardExamSummary:
        exams = await self.repo.list_for_user(
            user_id, exam_type=exam_type, limit=5
        )
        if not exams:
            return DashboardExamSummary()
        latest = exams[0]
        latest_net, _ = self._result_totals(list(latest.results or []))
        delta = None
        if len(exams) >= 2:
            prev_net, _ = self._result_totals(list(exams[1].results or []))
            delta = round(float(latest_net) - float(prev_net), 2)
        delta_txt = ""
        if delta is not None:
            sign = "+" if delta >= 0 else ""
            delta_txt = f" ({sign}{delta} net)"
        summary = (
            f"Son deneme: {latest.title} — {float(latest_net):.2f} net{delta_txt}"
        )
        return DashboardExamSummary(
            last_exam_title=latest.title,
            last_exam_net=round(float(latest_net), 2),
            last_exam_delta_net=delta,
            last_exam_date=latest.exam_date,
            today_ai_exam_summary=summary,
        )

    async def context_payload(self, user_id: uuid.UUID) -> dict:
        from app.services.subject_net_targets import (
            below_target_sorted,
            gaps_from_trends,
            on_track_sorted,
            resolve_user_target_net,
        )

        stats = await self.get_statistics(user_id)
        trends = await self.get_trends(user_id)
        user_target = await resolve_user_target_net(self.db, user_id)
        gaps = gaps_from_trends(
            by_subject=trends.by_subject, user_target_net=user_target
        )
        below = below_target_sorted(gaps)[:3]
        on_track = on_track_sorted(gaps)[:3]
        recent = [
            {
                "title": p.title,
                "exam_date": str(p.exam_date),
                "total_net": p.total_net,
                "exam_type": str(p.exam_type),
            }
            for p in trends.net_over_time[-5:]
        ]
        return {
            "summary": {
                "total_exams": stats.total_exams,
                "average_net": stats.average_net,
                "highest_net": stats.highest_net,
                "last_exam_title": stats.last_exam_title,
                "last_exam_net": stats.last_exam_net,
                "target_net": user_target,
            },
            "trends": {
                "week_average_net": stats.week_average_net,
                "month_average_net": stats.month_average_net,
                "recent": recent,
            },
            # Compat key; values are hedefe uzak dersler (not fixed %70 "weak")
            "weak_subjects": [
                {
                    "subject": g.subject,
                    "average_net": g.average_net,
                    "target_net": g.target_net,
                    "gap": g.gap,
                }
                for g in below
            ],
            "strong_subjects": [
                {
                    "subject": g.subject,
                    "average_net": g.average_net,
                    "target_net": g.target_net,
                    "gap": g.gap,
                }
                for g in on_track
            ],
            "below_target_subjects": [
                {
                    "subject": g.subject,
                    "average_net": g.average_net,
                    "target_net": g.target_net,
                    "gap": g.gap,
                }
                for g in below
            ],
            "memory_ready": {
                "source": "exam_tracking",
                "category": "exam",
                "enabled": False,
            },
        }
