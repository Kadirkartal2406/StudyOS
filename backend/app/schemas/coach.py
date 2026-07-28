"""Sprint 20 — Adaptive AI Coach projections (LOS §13 Experience).
Karar üretmez; mevcut Decision / Evidence / Confidence okur.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoachReason(BaseModel):
    """Açıklanabilir neden — 'neden bunu öneriyorum?'"""

    code: str
    label: str
    detail: str | None = None


class CoachWin(BaseModel):
    code: str
    title: str
    message: str


class CoachFollowUp(BaseModel):
    """Smart follow-up — Explain/Quiz/Assessment sonrası sonraki adım."""

    kind: str  # quiz | explain | revision | rest | knowledge | assessment
    title: str
    detail: str | None = None
    deep_link_hint: str | None = None
    cta_label: str = "Başla"


class CoachTodayMessage(BaseModel):
    """Today tek Coach mesajı — Decision değil; Next Action yorumu."""

    headline: str
    body: str
    focus_topic: str | None = None
    focus_subject: str | None = None
    suggested_minutes: int | None = None
    reasons: list[CoachReason] = Field(default_factory=list)
    habit_hint: str | None = None
    knowledge_hint: str | None = None
    win: CoachWin | None = None
    follow_ups: list[CoachFollowUp] = Field(default_factory=list)
    deep_link_hint: str | None = None
    cta_label: str = "Başla"
    # Kaynak Decision ile tutarlılık
    next_action_title: str | None = None
    next_action_reason: str | None = None
    voice: str = "coach"  # tutarlı kimlik


class WeeklyReflection(BaseModel):
    questions_solved: int = 0
    study_minutes: int = 0
    confidence_delta_label: str | None = None
    strongest_topic: str | None = None
    weakest_topic: str | None = None
    weekly_suggestion: str
    wins: list[CoachWin] = Field(default_factory=list)
    body: str


class CoachTimelineItem(BaseModel):
    period: str  # last_month | this_week | today | next
    title: str
    body: str
    tone: str = "neutral"  # positive | caution | neutral


class CoachTimeline(BaseModel):
    items: list[CoachTimelineItem] = Field(default_factory=list)
    next_goal: str | None = None


class AssessmentCoachSummary(BaseModel):
    estimated_rank_label: str | None = None
    critical_subject: str | None = None
    next_target: str | None = None
    estimated_improvement: str | None = None
    body: str


class KnowledgeCoachHint(BaseModel):
    summary: str | None = None
    teach_line: str | None = None
    page_hint: str | None = None
    next_step: str | None = None
    deep_link_hint: str | None = None


class CoachTodayBundle(BaseModel):
    message: CoachTodayMessage
    assessment: AssessmentCoachSummary | None = None


class CoachWeeklyBundle(BaseModel):
    reflection: WeeklyReflection


class CoachTimelineBundle(BaseModel):
    timeline: CoachTimeline
