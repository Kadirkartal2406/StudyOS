"""
StudyOS — Insight Engine
Sprint-2.0: Session/Statistics + QuestionRecord aggregate → InsightContext.
LLM yok; canlı hesap (A1).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.question_record_service import QuestionRecordService
from app.services.statistics_service import StatisticsService, _day_bounds, _week_monday


@dataclass
class InsightContext:
    """RuleEngine ve API yanıtları için ortak bağlam."""

    has_enough_data: bool = False
    streak_days: int = 0
    today_study_minutes: int = 0
    week_study_minutes: int = 0
    previous_week_study_minutes: int = 0
    month_study_minutes: int = 0
    previous_month_study_minutes: int = 0
    total_pomodoros: int = 0
    pomodoro_completion_rate: float = 0.0
    average_daily_minutes: float = 0.0
    average_daily_questions: float = 0.0
    most_studied_subject: str | None = None
    least_studied_subject: str | None = None
    most_questions_subject: str | None = None
    correct_rate: float = 0.0
    wrong_rate: float = 0.0
    total_net: float = 0.0
    total_questions: int = 0
    most_productive_hour: int | None = None
    least_productive_hour: int | None = None
    most_productive_weekday_label: str | None = None
    hour_minutes: list[int] = field(default_factory=lambda: [0] * 24)
    weekday_minutes: list[int] = field(default_factory=lambda: [0] * 7)
    idle_days_last_14: int = 0
    days_since_last_study: int | None = None
    weekly_questions: int = 0
    previous_week_questions: int = 0
    subjects_accuracy: list[tuple[str, float, int]] = field(default_factory=list)
    subjects_questions: list[tuple[str, int]] = field(default_factory=list)
    subjects_minutes: list[tuple[str, int]] = field(default_factory=list)
    daily_series: list[tuple[str, int, int]] = field(default_factory=list)
    low_accuracy_subjects: list[tuple[str, float]] = field(default_factory=list)
    neglected_subjects: list[str] = field(default_factory=list)
    # Sprint-2.1 — Goal Engine özeti (AI oluşturmaz, sadece okur)
    active_goals_count: int = 0
    goals_average_progress: float = 0.0
    top_goal_title: str | None = None
    top_goal_progress: float = 0.0
    top_goal_remaining: float = 0.0
    top_goal_eta_hint: str | None = None
    days_left_in_top_goal: int | None = None


class InsightEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stats = StatisticsService(db)
        self.questions = QuestionRecordService(db)

    async def build_context(self, user_id: uuid.UUID) -> InsightContext:
        today = datetime.now(UTC).date()
        overview = await self.stats.get_overview(user_id)
        productivity = await self.stats.get_productivity(user_id)
        heatmap = await self.stats.get_heatmap(user_id)
        subjects_dist = await self.stats.get_subjects(user_id)
        q_overview = await self.questions.get_statistics_overview(user_id)
        q_subjects = await self.questions.get_subjects_distribution(user_id)

        week_start = _week_monday(today)
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start - timedelta(days=1)
        month_start = today.replace(day=1)
        if month_start.month == 1:
            prev_month_anchor = month_start.replace(year=month_start.year - 1, month=12)
        else:
            prev_month_anchor = month_start.replace(month=month_start.month - 1)

        prev_week = await self.stats.get_weekly(user_id, anchor=prev_week_start)
        prev_month = await self.stats.get_monthly(user_id, anchor=prev_month_anchor)
        weekly = await self.stats.get_weekly(user_id, anchor=today)

        # Önceki hafta / bu hafta soru (QuestionRecord)
        week_from, _ = _day_bounds(week_start)
        _, week_to = _day_bounds(today)
        prev_from, _ = _day_bounds(prev_week_start)
        _, prev_to = _day_bounds(prev_week_end)
        w_q, *_ = await self.questions.repo.aggregate_between(
            user_id, created_from=week_from, created_to=week_to
        )
        pw_q, *_ = await self.questions.repo.aggregate_between(
            user_id, created_from=prev_from, created_to=prev_to
        )

        idle = sum(1 for d in heatmap.days if d.study_minutes == 0)
        active_days = sum(1 for d in heatmap.days if d.study_minutes > 0)
        avg_min = round(overview.total_study_minutes / max(active_days, 1), 1) if active_days else 0.0
        # Son 30 gün soru ortalaması — kayıt günlerine göre kabaca
        avg_q = round(q_overview.total_questions / max(active_days, 1), 1) if active_days else 0.0

        days_since: int | None = None
        for d in reversed(heatmap.days):
            if d.study_minutes > 0:
                days_since = (today - d.date).days
                break
        if days_since is None and heatmap.days:
            days_since = 14

        hour_mins = list(productivity.hour_minutes)
        most_h = productivity.most_productive_hour
        least_h = None
        if any(hour_mins):
            positive = [(i, m) for i, m in enumerate(hour_mins) if m > 0]
            if positive:
                least_h = min(positive, key=lambda x: x[1])[0]

        subjects_minutes = [(i.name, i.study_minutes) for i in subjects_dist.items]
        least_subject = None
        if subjects_minutes:
            least_subject = min(subjects_minutes, key=lambda x: x[1])[0]

        subjects_accuracy: list[tuple[str, float, int]] = []
        subjects_questions: list[tuple[str, int]] = []
        low_acc: list[tuple[str, float]] = []
        for item in q_subjects.items:
            subjects_accuracy.append((item.name, item.correct_rate, item.question_count))
            subjects_questions.append((item.name, item.question_count))
            if item.question_count >= 10 and item.correct_rate < 60:
                low_acc.append((item.name, item.correct_rate))

        most_q_subject = subjects_questions[0][0] if subjects_questions else None

        # İhmal edilen ders: plan/session subject listesinde olup son 10 günde soru yok
        neglected = await self._neglected_subjects(user_id, today)

        # Pomodoro başarı: tamamlanan / (tamamlanan) — basit proxy: completed sessions / total
        # Statistics total_pomodoros = completed sessions; completion rate ≈ 100 if any
        # Daha iyi: planned vs actual — actual_duration >= 0.8 * planned
        pomodoro_rate = await self._pomodoro_completion_rate(user_id)

        # Enrich daily series question counts from QuestionRecord daily buckets
        q_daily = await self.questions.get_daily(user_id, days=14)
        q_by_date = {b.date: b.question_count for b in q_daily.buckets}
        enriched: list[tuple[str, int, int]] = []
        for b in weekly.buckets:
            key = str(b.date_from)
            enriched.append((b.label, b.study_minutes, q_by_date.get(key, 0)))

        has_data = overview.total_sessions > 0 or q_overview.record_count > 0

        # Sprint-2.1 — aktif hedefler
        from app.services.goal_service import GoalService, _eta_hint, _remaining

        goal_service = GoalService(self.db)
        active_goals = await goal_service.list_active(user_id)
        top_goal = None
        if active_goals:
            top_goal = min(active_goals, key=lambda g: (g.progress, g.end_date))
        days_left_top = None
        if top_goal is not None:
            days_left_top = max((top_goal.end_date - today).days, 0)

        return InsightContext(
            has_enough_data=has_data,
            streak_days=overview.streak_days,
            today_study_minutes=overview.today_study_minutes,
            week_study_minutes=overview.week_study_minutes,
            previous_week_study_minutes=prev_week.study_minutes,
            month_study_minutes=overview.month_study_minutes,
            previous_month_study_minutes=prev_month.study_minutes,
            total_pomodoros=overview.total_pomodoros,
            pomodoro_completion_rate=pomodoro_rate,
            average_daily_minutes=avg_min,
            average_daily_questions=avg_q,
            most_studied_subject=overview.most_studied_subject,
            least_studied_subject=least_subject,
            most_questions_subject=most_q_subject,
            correct_rate=q_overview.correct_rate,
            wrong_rate=q_overview.wrong_rate,
            total_net=q_overview.total_net,
            total_questions=q_overview.total_questions,
            most_productive_hour=most_h,
            least_productive_hour=least_h,
            most_productive_weekday_label=productivity.most_productive_weekday_label,
            hour_minutes=hour_mins,
            weekday_minutes=list(productivity.weekday_minutes),
            idle_days_last_14=idle,
            days_since_last_study=days_since,
            weekly_questions=w_q,
            previous_week_questions=pw_q,
            subjects_accuracy=subjects_accuracy,
            subjects_questions=subjects_questions,
            subjects_minutes=subjects_minutes,
            daily_series=enriched,
            low_accuracy_subjects=low_acc,
            neglected_subjects=neglected,
            active_goals_count=len(active_goals),
            goals_average_progress=(
                round(sum(float(g.progress) for g in active_goals) / len(active_goals), 1)
                if active_goals
                else 0.0
            ),
            top_goal_title=top_goal.title if top_goal else None,
            top_goal_progress=float(top_goal.progress) if top_goal else 0.0,
            top_goal_remaining=_remaining(top_goal) if top_goal else 0.0,
            top_goal_eta_hint=_eta_hint(top_goal) if top_goal else None,
            days_left_in_top_goal=days_left_top,
        )

    async def _pomodoro_completion_rate(self, user_id: uuid.UUID) -> float:
        """Tamamlanan oturumlarda actual >= %80 planned → başarılı."""
        from sqlalchemy import select

        from app.models.study_session import StudySession, StudySessionStatus

        result = await self.db.execute(
            select(
                StudySession.planned_duration_minutes,
                StudySession.actual_duration_minutes,
            ).where(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
            )
        )
        rows = list(result.all())
        if not rows:
            return 0.0
        ok = 0
        for planned, actual in rows:
            if planned is None or planned <= 0:
                continue
            if actual is None:
                continue
            if actual >= planned * 0.8:
                ok += 1
        return round((ok / len(rows)) * 100, 1)

    async def _neglected_subjects(self, user_id: uuid.UUID, today: date) -> list[str]:
        """Son 10 günde hiç soru kaydı olmayan, geçmişte çalışılmış dersler."""
        from datetime import timedelta

        cutoff = today - timedelta(days=10)
        subjects_all = await self.stats.get_subjects(user_id)
        if not subjects_all.items:
            return []
        from app.repositories.question_record_repository import QuestionRecordRepository

        repo = QuestionRecordRepository(self.db)
        created_from = datetime.combine(cutoff, datetime.min.time(), tzinfo=UTC)
        recent_rows = await repo.group_by_subject(
            user_id, created_from=created_from, limit=50
        )
        recent_names = {str(r[0]) for r in recent_rows}
        neglected = [
            i.name
            for i in subjects_all.items
            if i.name not in recent_names and i.name != "Serbest"
        ]
        return neglected[:5]
