"""
StudyOS — AI Insights Şemaları
Sprint-2.0 (Meeting-018) — LLM yok; Insight + Rule Engine yanıtları.
"""

from pydantic import BaseModel, Field


class AiRecommendation(BaseModel):
    code: str
    message: str
    priority: int = Field(ge=1, le=100, description="1=en yüksek öncelik")
    category: str = "general"
    # Sprint-3.1.B — RuleEngine evidence (LLM Explain → 3.1.D)
    reason: str | None = None


class AiInsightMetric(BaseModel):
    key: str
    label: str
    value: str | float | int | None
    unit: str | None = None


class AiOverviewResponse(BaseModel):
    has_enough_data: bool
    streak_days: int = 0
    average_daily_minutes: float = 0.0
    average_daily_questions: float = 0.0
    most_studied_subject: str | None = None
    least_studied_subject: str | None = None
    most_questions_subject: str | None = None
    correct_rate: float = 0.0
    pomodoro_completion_rate: float = 0.0
    most_productive_hour: int | None = None
    least_productive_hour: int | None = None
    idle_days_last_14: int = 0
    top_recommendation: AiRecommendation | None = None
    recommendations_count: int = 0


class AiRecommendationsResponse(BaseModel):
    items: list[AiRecommendation]
    has_enough_data: bool = True


class AiTrendPoint(BaseModel):
    label: str
    study_minutes: int = 0
    question_count: int = 0


class AiTrendsResponse(BaseModel):
    weekly_study_minutes: int = 0
    previous_week_study_minutes: int = 0
    study_minutes_delta_pct: float | None = None
    weekly_questions: int = 0
    previous_week_questions: int = 0
    questions_delta_pct: float | None = None
    monthly_study_minutes: int = 0
    previous_month_study_minutes: int = 0
    daily_series: list[AiTrendPoint] = Field(default_factory=list)


class AiPerformanceResponse(BaseModel):
    correct_rate: float = 0.0
    wrong_rate: float = 0.0
    total_net: float = 0.0
    total_questions: int = 0
    subjects_by_accuracy: list[AiInsightMetric] = Field(default_factory=list)
    subjects_by_questions: list[AiInsightMetric] = Field(default_factory=list)
    pomodoro_completion_rate: float = 0.0
    total_pomodoros: int = 0


class AiProductivityResponse(BaseModel):
    most_productive_hour: int | None = None
    least_productive_hour: int | None = None
    most_productive_weekday_label: str | None = None
    hour_minutes: list[int] = Field(default_factory=lambda: [0] * 24)
    weekday_minutes: list[int] = Field(default_factory=lambda: [0] * 7)
    streak_days: int = 0
    idle_days_last_14: int = 0
    average_daily_minutes: float = 0.0
    average_daily_questions: float = 0.0


# Sprint-12 — AI Explain
class AiExplainRequest(BaseModel):
    context_type: str = Field(
        default="next_action",
        description="'next_action' | 'topic' | 'revision'",
        pattern="^(next_action|topic|revision)$",
    )
    subject_code: str | None = None
    topic_code: str | None = None
    reason: str | None = Field(default=None, max_length=500)


class AiExplainResponse(BaseModel):
    explanation: str
