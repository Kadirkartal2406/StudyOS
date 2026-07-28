"""
StudyOS — Dashboard Pydantic Şemaları
Bkz. docs/architecture/api-design.md §2.16

Sprint-1.6: StatisticsService.overview alanları eklendi (streak, pomodoro vb.).
Mevcut alanlar korunur; yeni alanlar geriye uyumlu genişletmedir.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from datetime import date

from app.schemas.achievement import DashboardAchievementSummary
from app.schemas.activity import ActivityRead
from app.schemas.coach import CoachTodayMessage
from app.schemas.goal import WeeklyGoalSummaryItem
from app.schemas.learning_intelligence import FeedCard, InsightCard
from app.schemas.learning_profile import (
    DashboardSubjectsSummary,
    JourneyProgressSummary,
    UserSubjectRead,
)
from app.schemas.planner import DashboardPlannerSummary
from app.schemas.revision import DashboardRevisionSummary
from app.schemas.study_plan import StudyPlanRead
from app.schemas.study_resource import StudyResourceRead


class DashboardExamTargetSummary(BaseModel):
    """Sprint-3.1.B — Hero Primary/Active hedef özeti (additive)."""

    exam_type: str
    is_primary: bool = False
    target_net: float | None = None
    target_score: float | None = None
    target_rank: int | None = None
    target_university: str | None = None
    target_department: str | None = None
    branch: str | None = None
    exam_date: date | None = None


class NextActionProjection(BaseModel):
    """Decision Engine Projection — tek Primary Action (amaç odaklı)."""

    title: str
    subtitle: str | None = None
    reason: str
    action_type: str  # revision | study_plan | focus
    deep_link_hint: str
    cta_label: str = "Başla"
    confidence_tone: str = "high"  # high | low
    # Alignment Sprint-3 — Topic Work Surface yönlendirme
    subject_code: str | None = None
    topic_code: str | None = None
    purpose: str | None = None  # study | review
    tool_hint: str | None = None  # pomodoro | revision — araç Primary değil; aksiyon içinde


class DashboardResponse(BaseModel):
    """Ana ekran (Dashboard) özet verisi."""

    first_name: str
    daily_study_goal_minutes: int
    today_study_minutes: int
    today_questions_solved: int
    today_studied_topic: str | None
    daily_progress_percentage: float
    last_login_at: datetime | None
    today_plan_count: int
    completed_plan_count: int
    today_plans: list[StudyPlanRead]
    # Sprint-1.6 — Statistics overview entegrasyonu
    streak_days: int = 0
    total_pomodoros: int = 0
    total_study_minutes: int = 0
    average_session_minutes: float = 0.0
    most_studied_subject: str | None = None
    week_study_minutes: int = 0
    # Sprint-1.7 — Activity tablosundan gerçek son aktiviteler
    recent_activities: list[ActivityRead] = []
    # Sprint-2.0 — Bugünün AI önerisi (C1 additive)
    today_ai_recommendation: str | None = None
    today_ai_recommendation_code: str | None = None
    # Sprint-3.1.B — RuleEngine reason (LLM Explain değil)
    today_ai_recommendation_reason: str | None = None
    # Sprint-2.1 — Bu haftaki hedefler özeti (C1 additive)
    weekly_goals: list[WeeklyGoalSummaryItem] = []
    # Sprint-2.5 — Kaynak özeti (J1)
    today_resources_opened: int = 0
    today_resources_completed: int = 0
    recent_resources: list[StudyResourceRead] = []
    # Sprint-2.6 — Deneme özeti (L1)
    last_exam_title: str | None = None
    last_exam_net: float | None = None
    last_exam_delta_net: float | None = None
    last_exam_date: date | None = None
    today_ai_exam_summary: str | None = None
    # Sprint-2.7 — Adaptive Planner (O1)
    planner_summary: DashboardPlannerSummary | None = None
    # Sprint-2.8 — Revision (K1)
    revision_summary: DashboardRevisionSummary | None = None
    # Sprint-2.9 — Achievements (K1)
    achievement_summary: DashboardAchievementSummary | None = None
    # Sprint-3.0 — Journey progress (K1) + learning profile summary
    journey_progress: JourneyProgressSummary | None = None
    # Sprint-3.0 post-revision — Derslerim (additive)
    my_subjects: list[UserSubjectRead] = []
    # Sprint-3.0.1 — Derslerim insight özeti
    subjects_summary: DashboardSubjectsSummary | None = None
    # Sprint-3.1.A — Active / Primary echo (additive)
    active_exam_type: str | None = None
    primary_exam_type: str | None = None
    # Sprint-3.1.B — Hero hedef özetleri (tek request)
    primary_target: DashboardExamTargetSummary | None = None
    active_target: DashboardExamTargetSummary | None = None
    # Alignment Sprint-1 — Today Projection (Decision SSOT)
    next_action: NextActionProjection | None = None
    today_context_lines: list[str] = []
    today_journey_line: str | None = None
    # Sprint-8 — Observation mode state ("observing" | "calibrating" | "full")
    observation_state: str = "observing"
    # Sprint 15 — Personalized Home Feed + Insights (Decision değil)
    learning_feed: list[FeedCard] = Field(default_factory=list)
    insight_cards: list[InsightCard] = Field(default_factory=list)
    # Sprint 20 — Adaptive AI Coach (Experience; Decision değil)
    coach_today: CoachTodayMessage | None = None
