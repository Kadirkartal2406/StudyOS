"""
StudyOS — Statistics Pydantic Şemaları
Bkz. docs/architecture/api-design.md §2.9 (Sprint-1.6)
Veri kaynağı: StudySession + StudyPlan aggregate (QuestionStatistics yok).
"""

from datetime import date

from pydantic import BaseModel, Field


class TimeBucket(BaseModel):
    """Zaman serisi noktası (günlük / haftalık / aylık grafik)."""

    label: str
    date_from: date
    date_to: date
    study_minutes: int = 0
    session_count: int = 0
    question_count: int = 0


class DistributionItem(BaseModel):
    """Ders veya konu dağılım satırı."""

    name: str
    study_minutes: int = 0
    session_count: int = 0
    question_count: int = 0
    percentage: float = 0.0


class HeatmapDay(BaseModel):
    """Son N gün aktivite yoğunluğu."""

    date: date
    study_minutes: int = 0
    session_count: int = 0


class ProductivityInsight(BaseModel):
    """En verimli gün / saat bilgisi."""

    most_productive_weekday: int | None = Field(
        default=None,
        description="0=Pazartesi … 6=Pazar (ISO); veri yoksa null",
    )
    most_productive_weekday_label: str | None = None
    most_productive_hour: int | None = Field(
        default=None,
        description="0–23 UTC saat dilimi; veri yoksa null",
    )
    weekday_minutes: list[int] = Field(
        default_factory=lambda: [0] * 7,
        description="7 eleman: Pazartesi→Pazar toplam dakika",
    )
    hour_minutes: list[int] = Field(
        default_factory=lambda: [0] * 24,
        description="24 eleman: saat bazlı toplam dakika",
    )


class StatisticsOverview(BaseModel):
    """Genel istatistik özeti — Dashboard ve Overview sekmesi."""

    total_study_minutes: int = 0
    today_study_minutes: int = 0
    today_questions: int = 0
    week_study_minutes: int = 0
    month_study_minutes: int = 0
    total_sessions: int = 0
    total_pomodoros: int = 0
    completed_plans: int = 0
    total_questions: int = 0
    average_session_minutes: float = 0.0
    longest_session_minutes: int = 0
    most_studied_subject: str | None = None
    most_studied_topic: str | None = None
    streak_days: int = 0
    most_productive_weekday_label: str | None = None
    most_productive_hour: int | None = None


class StatisticsStreak(BaseModel):
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_study_date: date | None = None


class StatisticsDailyResponse(BaseModel):
    date: date
    study_minutes: int = 0
    session_count: int = 0
    question_count: int = 0
    completed_plans: int = 0
    buckets: list[TimeBucket] = Field(
        default_factory=list,
        description="Saatlik kırılım (0–23)",
    )


class StatisticsPeriodResponse(BaseModel):
    """Haftalık / aylık özet + zaman serisi."""

    date_from: date
    date_to: date
    study_minutes: int = 0
    session_count: int = 0
    question_count: int = 0
    completed_plans: int = 0
    buckets: list[TimeBucket] = Field(default_factory=list)


class StatisticsDistributionResponse(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    total_minutes: int = 0
    items: list[DistributionItem] = Field(default_factory=list)


class StatisticsHeatmapResponse(BaseModel):
    date_from: date
    date_to: date
    days: list[HeatmapDay] = Field(default_factory=list)
