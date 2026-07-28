"""
StudyOS — Statistics Service
StudySession + StudyPlan aggregate istatistikleri.
Sprint-1.6 (Meeting-014): QuestionStatistics tablosu kullanılmaz.
"""

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    STATISTICS_DISTRIBUTION_LIMIT,
    STATISTICS_HEATMAP_DAYS,
)
from app.repositories.statistics_repository import StatisticsRepository
from app.schemas.statistics import (
    DistributionItem,
    HeatmapDay,
    ProductivityInsight,
    StatisticsDailyResponse,
    StatisticsDistributionResponse,
    StatisticsHeatmapResponse,
    StatisticsOverview,
    StatisticsPeriodResponse,
    StatisticsStreak,
    TimeBucket,
)

_WEEKDAY_LABELS_TR = (
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar",
)


def _day_bounds(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, datetime.min.time(), tzinfo=UTC)
    return start, start + timedelta(days=1)


def _week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _pg_dow_to_iso(pg_dow: int) -> int:
    """PostgreSQL DOW 0=Pazar…6=Cumartesi → ISO 0=Pazartesi…6=Pazar."""
    return (pg_dow - 1) % 7


class StatisticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StatisticsRepository(db)

    async def _active_scope(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> tuple[set[str] | None, set[str] | None]:
        """M17.3 — Active Exam subject_codes / names; None = no filter (no exam)."""
        from app.services.learning_profile_service import LearningProfileService

        _, codes, names = await LearningProfileService(self.db).resolve_active_scope(
            user_id, exam_type=exam_type
        )
        return (codes or None), (names or None)

    async def get_overview(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> StatisticsOverview:
        today = datetime.now(UTC).date()
        week_start = _week_monday(today)
        month_start = today.replace(day=1)

        today_from, today_to = _day_bounds(today)
        week_from = datetime.combine(week_start, datetime.min.time(), tzinfo=UTC)
        month_from = datetime.combine(month_start, datetime.min.time(), tzinfo=UTC)
        now_to = datetime.now(UTC) + timedelta(days=1)

        codes, names = await self._active_scope(user_id, exam_type=exam_type)

        total_m, total_s, total_q, _, avg_m, max_m = await self.repo.aggregate_sessions(
            user_id, subject_codes=codes
        )
        today_m, _, today_q, _, _, _ = await self.repo.aggregate_sessions(
            user_id,
            started_from=today_from,
            started_to=today_to,
            subject_codes=codes,
        )
        week_m, _, _, _, _, _ = await self.repo.aggregate_sessions(
            user_id,
            started_from=week_from,
            started_to=now_to,
            subject_codes=codes,
        )
        month_m, _, _, _, _, _ = await self.repo.aggregate_sessions(
            user_id,
            started_from=month_from,
            started_to=now_to,
            subject_codes=codes,
        )

        completed_plans = await self.repo.count_completed_plans(
            user_id, subject_names=names
        )
        subjects = await self.repo.subject_distribution(
            user_id, limit=1, subject_codes=codes
        )
        topics = await self.repo.topic_distribution(
            user_id, limit=1, subject_codes=codes
        )
        streak = await self.get_streak(user_id, exam_type=exam_type)
        productivity = await self.get_productivity(user_id, exam_type=exam_type)

        return StatisticsOverview(
            total_study_minutes=total_m,
            today_study_minutes=today_m,
            today_questions=today_q,
            week_study_minutes=week_m,
            month_study_minutes=month_m,
            total_sessions=total_s,
            total_pomodoros=total_s,
            completed_plans=completed_plans,
            total_questions=total_q,
            average_session_minutes=round(avg_m, 1),
            longest_session_minutes=max_m,
            most_studied_subject=subjects[0][0] if subjects else None,
            most_studied_topic=topics[0][0] if topics else None,
            streak_days=streak.current_streak_days,
            most_productive_weekday_label=productivity.most_productive_weekday_label,
            most_productive_hour=productivity.most_productive_hour,
        )

    async def get_daily(
        self,
        user_id: uuid.UUID,
        target: date | None = None,
        *,
        exam_type: str | None = None,
    ) -> StatisticsDailyResponse:
        day = target or datetime.now(UTC).date()
        started_from, started_to = _day_bounds(day)
        codes, names = await self._active_scope(user_id, exam_type=exam_type)
        minutes, sessions, questions, _, _, _ = await self.repo.aggregate_sessions(
            user_id,
            started_from=started_from,
            started_to=started_to,
            subject_codes=codes,
        )
        completed_plans = await self.repo.count_completed_plans(
            user_id,
            study_date_from=day,
            study_date_to=day,
            subject_names=names,
        )
        hourly = await self.repo.hourly_minutes_series(
            user_id, started_from, started_to, subject_codes=codes
        )
        by_hour = {h: (m, s, q) for h, m, s, q in hourly}
        buckets = [
            TimeBucket(
                label=f"{h:02d}:00",
                date_from=day,
                date_to=day,
                study_minutes=by_hour.get(h, (0, 0, 0))[0],
                session_count=by_hour.get(h, (0, 0, 0))[1],
                question_count=by_hour.get(h, (0, 0, 0))[2],
            )
            for h in range(24)
        ]
        return StatisticsDailyResponse(
            date=day,
            study_minutes=minutes,
            session_count=sessions,
            question_count=questions,
            completed_plans=completed_plans,
            buckets=buckets,
        )

    async def get_weekly(
        self,
        user_id: uuid.UUID,
        anchor: date | None = None,
        *,
        exam_type: str | None = None,
    ) -> StatisticsPeriodResponse:
        ref = anchor or datetime.now(UTC).date()
        start = _week_monday(ref)
        end = start + timedelta(days=6)
        return await self._period_response(
            user_id, start, end, bucket_mode="daily", exam_type=exam_type
        )

    async def get_monthly(
        self,
        user_id: uuid.UUID,
        anchor: date | None = None,
        *,
        exam_type: str | None = None,
    ) -> StatisticsPeriodResponse:
        ref = anchor or datetime.now(UTC).date()
        start = ref.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        end = next_month - timedelta(days=1)
        return await self._period_response(
            user_id, start, end, bucket_mode="daily", exam_type=exam_type
        )

    async def get_subjects(
        self,
        user_id: uuid.UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        exam_type: str | None = None,
    ) -> StatisticsDistributionResponse:
        started_from, started_to = self._optional_bounds(date_from, date_to)
        codes, _ = await self._active_scope(user_id, exam_type=exam_type)
        rows = await self.repo.subject_distribution(
            user_id,
            started_from=started_from,
            started_to=started_to,
            limit=STATISTICS_DISTRIBUTION_LIMIT,
            subject_codes=codes,
        )
        return self._to_distribution(rows, date_from, date_to)

    async def get_topics(
        self,
        user_id: uuid.UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        exam_type: str | None = None,
    ) -> StatisticsDistributionResponse:
        started_from, started_to = self._optional_bounds(date_from, date_to)
        codes, _ = await self._active_scope(user_id, exam_type=exam_type)
        rows = await self.repo.topic_distribution(
            user_id,
            started_from=started_from,
            started_to=started_to,
            limit=STATISTICS_DISTRIBUTION_LIMIT,
            subject_codes=codes,
        )
        return self._to_distribution(rows, date_from, date_to)

    async def get_productivity(
        self,
        user_id: uuid.UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        exam_type: str | None = None,
    ) -> ProductivityInsight:
        started_from, started_to = self._optional_bounds(date_from, date_to)
        codes, _ = await self._active_scope(user_id, exam_type=exam_type)
        weekday_raw = await self.repo.weekday_minutes(
            user_id, started_from, started_to, subject_codes=codes
        )
        iso_minutes = [0] * 7
        for pg_dow, minutes in weekday_raw:
            iso_minutes[_pg_dow_to_iso(pg_dow)] = minutes

        best_wd = None
        best_wd_label = None
        if any(iso_minutes):
            best_wd = max(range(7), key=lambda i: iso_minutes[i])
            if iso_minutes[best_wd] > 0:
                best_wd_label = _WEEKDAY_LABELS_TR[best_wd]
            else:
                best_wd = None

        # Saat dağılımı — tüm aralık
        if started_from is None:
            started_from = datetime(1970, 1, 1, tzinfo=UTC)
        if started_to is None:
            started_to = datetime.now(UTC) + timedelta(days=1)
        hourly = await self.repo.hourly_minutes_series(
            user_id, started_from, started_to, subject_codes=codes
        )
        hour_minutes = [0] * 24
        for h, m, _, _ in hourly:
            if 0 <= h < 24:
                hour_minutes[h] = m
        best_hour = None
        if any(hour_minutes):
            best_hour = max(range(24), key=lambda i: hour_minutes[i])
            if hour_minutes[best_hour] == 0:
                best_hour = None

        return ProductivityInsight(
            most_productive_weekday=best_wd,
            most_productive_weekday_label=best_wd_label,
            most_productive_hour=best_hour,
            weekday_minutes=iso_minutes,
            hour_minutes=hour_minutes,
        )

    async def get_heatmap(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> StatisticsHeatmapResponse:
        today = datetime.now(UTC).date()
        date_from = today - timedelta(days=STATISTICS_HEATMAP_DAYS - 1)
        started_from = datetime.combine(date_from, datetime.min.time(), tzinfo=UTC)
        started_to = datetime.combine(today + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
        codes, _ = await self._active_scope(user_id, exam_type=exam_type)
        series = await self.repo.daily_minutes_series(
            user_id, started_from, started_to, subject_codes=codes
        )
        by_day = {d: (m, s) for d, m, s, _ in series}
        days = [
            HeatmapDay(
                date=date_from + timedelta(days=i),
                study_minutes=by_day.get(date_from + timedelta(days=i), (0, 0))[0],
                session_count=by_day.get(date_from + timedelta(days=i), (0, 0))[1],
            )
            for i in range(STATISTICS_HEATMAP_DAYS)
        ]
        return StatisticsHeatmapResponse(date_from=date_from, date_to=today, days=days)

    async def get_streak(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> StatisticsStreak:
        codes, _ = await self._active_scope(user_id, exam_type=exam_type)
        dates = await self.repo.study_dates_desc(user_id, subject_codes=codes)
        if not dates:
            return StatisticsStreak()

        today = datetime.now(UTC).date()
        date_set = set(dates)
        last = dates[0]

        # Current streak: today or yesterday'den geriye
        if last == today or last == today - timedelta(days=1):
            cursor = last
            current = 0
            while cursor in date_set:
                current += 1
                cursor -= timedelta(days=1)
        else:
            current = 0

        # Longest streak
        longest = 0
        run = 0
        prev: date | None = None
        for d in sorted(date_set):
            if prev is not None and d == prev + timedelta(days=1):
                run += 1
            else:
                run = 1
            longest = max(longest, run)
            prev = d

        return StatisticsStreak(
            current_streak_days=current,
            longest_streak_days=longest,
            last_study_date=last,
        )

    async def _period_response(
        self,
        user_id: uuid.UUID,
        start: date,
        end: date,
        *,
        bucket_mode: str,
        exam_type: str | None = None,
    ) -> StatisticsPeriodResponse:
        started_from = datetime.combine(start, datetime.min.time(), tzinfo=UTC)
        started_to = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
        codes, names = await self._active_scope(user_id, exam_type=exam_type)
        minutes, sessions, questions, _, _, _ = await self.repo.aggregate_sessions(
            user_id,
            started_from=started_from,
            started_to=started_to,
            subject_codes=codes,
        )
        completed_plans = await self.repo.count_completed_plans(
            user_id,
            study_date_from=start,
            study_date_to=end,
            subject_names=names,
        )
        series = await self.repo.daily_minutes_series(
            user_id, started_from, started_to, subject_codes=codes
        )
        by_day = {d: (m, s, q) for d, m, s, q in series}
        buckets: list[TimeBucket] = []
        if bucket_mode == "daily":
            cursor = start
            while cursor <= end:
                m, s, q = by_day.get(cursor, (0, 0, 0))
                buckets.append(
                    TimeBucket(
                        label=cursor.isoformat(),
                        date_from=cursor,
                        date_to=cursor,
                        study_minutes=m,
                        session_count=s,
                        question_count=q,
                    )
                )
                cursor += timedelta(days=1)
        return StatisticsPeriodResponse(
            date_from=start,
            date_to=end,
            study_minutes=minutes,
            session_count=sessions,
            question_count=questions,
            completed_plans=completed_plans,
            buckets=buckets,
        )

    @staticmethod
    def _optional_bounds(
        date_from: date | None, date_to: date | None
    ) -> tuple[datetime | None, datetime | None]:
        started_from = (
            datetime.combine(date_from, datetime.min.time(), tzinfo=UTC) if date_from else None
        )
        started_to = (
            datetime.combine(date_to + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
            if date_to
            else None
        )
        return started_from, started_to

    @staticmethod
    def _to_distribution(
        rows: list[tuple[str, int, int, int]],
        date_from: date | None,
        date_to: date | None,
    ) -> StatisticsDistributionResponse:
        total = sum(r[1] for r in rows)
        items = [
            DistributionItem(
                name=name,
                study_minutes=minutes,
                session_count=sessions,
                question_count=questions,
                percentage=round((minutes / total) * 100, 1) if total > 0 else 0.0,
            )
            for name, minutes, sessions, questions in rows
        ]
        return StatisticsDistributionResponse(
            date_from=date_from,
            date_to=date_to,
            total_minutes=total,
            items=items,
        )
