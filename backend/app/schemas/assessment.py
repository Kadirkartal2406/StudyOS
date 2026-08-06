"""Sprint 18 — Assessment schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class AssessmentStartRequest(BaseModel):
    kind: str = Field(
        description="initial_calibration | daily_challenge | branch_question"
    )
    subject_code: str | None = None
    topic_code: str | None = None
    count: int | None = Field(default=None, ge=1, le=200)
    difficulty: str = "medium"
    # Sprint 23 — force synthetic questions (tests / offline); ignored in prod unless settings allow
    synthetic: bool = False


class AssessmentAnswerItem(BaseModel):
    question_id: uuid.UUID
    selected_key: str | None = None


class AssessmentSubmitRequest(BaseModel):
    answers: list[AssessmentAnswerItem] = Field(default_factory=list)


class AssessmentQuestionPublic(BaseModel):
    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]
    subject_code: str | None = None
    topic_code: str | None = None
    subject_name: str | None = None
    eae_interaction: dict | None = None


class AssessmentQuestionReview(BaseModel):
    id: uuid.UUID
    ord_index: int
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None = None
    selected_key: str | None = None
    is_correct: bool | None = None
    eae_interaction: dict | None = None


class AssessmentSessionRead(BaseModel):
    id: uuid.UUID
    exam_type: str
    kind: str
    subject_code: str | None = None
    topic_code: str | None = None
    subject_name: str | None = None
    topic_name: str | None = None
    status: str
    difficulty: str
    requested_count: int
    challenge_date: date | None = None
    quiz_generation_id: uuid.UUID | None = None
    correct_count: int | None = None
    wrong_count: int | None = None
    blank_count: int | None = None
    accuracy: float | None = None
    commentary: str | None = None
    is_booklet: bool = False
    section_plan: dict = Field(default_factory=dict)
    generation_progress: int = 0
    questions: list[AssessmentQuestionPublic] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentSubjectBreakdown(BaseModel):
    subject_code: str
    subject_name: str
    correct: int = 0
    wrong: int = 0
    blank: int = 0
    net: float = 0.0
    total: int = 0


class AssessmentTopicBreakdown(BaseModel):
    topic_code: str
    topic_name: str
    subject_code: str | None = None
    correct: int = 0
    wrong: int = 0
    blank: int = 0
    total: int = 0


class AssessmentSubmitResult(BaseModel):
    session: AssessmentSessionRead
    review_items: list[AssessmentQuestionReview] = Field(default_factory=list)
    commentary: str
    estimated_success_pct: float | None = None
    # Sprint 23 M23.6 / M23.8
    net: float | None = None
    score_formula: str | None = None
    by_subject: list[AssessmentSubjectBreakdown] = Field(default_factory=list)
    by_topic: list[AssessmentTopicBreakdown] = Field(default_factory=list)


class AssessmentWrongExplainRequest(BaseModel):
    selected_key: str | None = None


class AssessmentWrongExplainResponse(BaseModel):
    question_id: uuid.UUID
    explanation: str
    why_wrong: str | None = None
    why_correct: str | None = None
    cached: bool = False
    provider: str = "ai"


class AssessmentProgressItem(BaseModel):
    subject_code: str
    subject_name: str
    completed: bool
    accuracy: float | None = None
    session_id: uuid.UUID | None = None


class AssessmentOverview(BaseModel):
    exam_type: str
    progress_pct: float
    completed_subjects: int
    total_subjects: int
    message: str
    subjects: list[AssessmentProgressItem] = Field(default_factory=list)
    # Sprint 20 — Assessment Coach (Experience)
    coach_summary: str | None = None
    coach_critical_subject: str | None = None
    coach_next_target: str | None = None
    coach_rank_label: str | None = None


class DailyChallengeRead(BaseModel):
    id: uuid.UUID
    exam_type: str
    challenge_date: date
    status: str
    title: str
    session_id: uuid.UUID | None = None
    subject_code: str | None = None
    topic_code: str | None = None
    deep_link_hint: str | None = None
    requested_count: int | None = None
    generation_progress: int | None = None
    pdf_ready: bool = False
    is_booklet: bool = True


class BookletSectionPlanItem(BaseModel):
    subject_code: str
    subject_name: str
    count: int
    topics: list[dict] = Field(default_factory=list)


class BranchChallengeRead(BaseModel):
    subject_code: str
    subject_name: str
    topic_code: str | None = None
    topic_name: str | None = None
    status: str  # available | completed
    session_id: uuid.UUID | None = None
    deep_link_hint: str | None = None


class DailyChallengeBundle(BaseModel):
    exam_type: str
    challenge_date: date
    daily: DailyChallengeRead | None = None
    branches: list[BranchChallengeRead] = Field(default_factory=list)


class EstimatedScoreRead(BaseModel):
    exam_type: str
    estimated_score: float
    estimated_success_pct: float
    estimated_rank_pct: float
    peer_sample_size: int
    strongest_subject: str | None = None
    weakest_subject: str | None = None
    commentary: str | None = None
    above_average: bool = False


class RankingRead(BaseModel):
    exam_type: str
    estimated_rank_pct: float
    peer_sample_size: int
    label: str
    commentary: str


class DailySubjectOption(BaseModel):
    subject_code: str
    subject_name: str
    status: str  # available | in_progress | completed
    session_id: uuid.UUID | None = None
    deep_link_hint: str | None = None


class DailySubjectsBundle(BaseModel):
    exam_type: str
    challenge_date: date
    subjects: list[DailySubjectOption] = Field(default_factory=list)
    completed_count: int = 0
    total_count: int = 0
    overall_ready: bool = False


class LeaderboardEntry(BaseModel):
    rank: int
    nickname: str
    user_id: uuid.UUID | None = None
    score: float
    accuracy: float
    is_me: bool = False


class LeaderboardRead(BaseModel):
    exam_type: str
    challenge_date: date
    subject_code: str | None = None
    scope: str  # subject | overall
    entries: list[LeaderboardEntry] = Field(default_factory=list)
    my_rank: int | None = None
    my_score: float | None = None
    total_participants: int = 0
