"""
StudyOS — Dashboard Service
Ana ekran özet verisini üretir.

Sprint-1.6 (Meeting-014): Overview metrikleri StatisticsService üzerinden gelir
(streak, pomodoro, ortalama oturum vb.). Bugünkü plan listesi StudyPlan'dan kalır.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_DAILY_STUDY_GOAL_MINUTES
from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.models.user import User
from app.repositories.study_plan_repository import StudyPlanRepository
from app.schemas.dashboard import DashboardExamTargetSummary, DashboardResponse
from app.schemas.study_plan import StudyPlanRead
from app.services.achievement_service import AchievementService
from app.services.activity_service import ActivityService
from app.services.ai.next_action_engine import (
    CatalogTopic,
    build_journey_line,
    build_next_action,
    build_today_context_lines,
)
from app.services.ai_insights_service import AiInsightsService
from app.services.exam_service import ExamService
from app.services.goal_service import GoalService
from app.services.learning_profile_service import LearningProfileService
from app.services.living_plan_service import maybe_run_living_plan_adapt
from app.services.observation_mode import ObservationMode
from app.services.planner_service import PlannerService
from app.services.policy_decision_engine import Policy, PolicyDecisionEngine
from app.services.question_record_service import QuestionRecordService
from app.services.revision_service import RevisionService
from app.services.statistics_service import StatisticsService
from app.services.study_resource_service import StudyResourceService


def _exam_target_summary(target) -> DashboardExamTargetSummary:
    return DashboardExamTargetSummary(
        exam_type=str(target.exam_type),
        is_primary=bool(target.is_primary),
        target_net=target.target_net,
        target_score=target.target_score,
        target_rank=target.target_rank,
        target_university=target.target_university,
        target_department=target.target_department,
        branch=target.branch,
        exam_date=target.exam_date,
    )


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.study_plan_repo = StudyPlanRepository(db)
        self.statistics_service = StatisticsService(db)
        self.activity_service = ActivityService(db)
        self.question_service = QuestionRecordService(db)
        self.ai_service = AiInsightsService(db)
        self.goal_service = GoalService(db)
        self.resource_service = StudyResourceService(db)
        self.exam_service = ExamService(db)
        self.planner_service = PlannerService(db)
        self.revision_service = RevisionService(db)
        self.achievement_service = AchievementService(db)
        self.learning_profile_service = LearningProfileService(db)

    async def get_dashboard(
        self, user: User, *, exam_type: str | None = None
    ) -> DashboardResponse:
        today = datetime.now(UTC).date()

        # Sprint-3.1.A / M17.1 — resolve Active early so all surfaces share scope
        student = await self.learning_profile_service.ensure_student(user.id)
        targets = await self.learning_profile_service.repo.list_exam_targets(user.id)
        effective = self.learning_profile_service.resolve_active_exam_type(
            student, targets, override=exam_type
        )
        profile = await self.learning_profile_service.get_profile(user.id)
        if effective is None:
            effective = profile.active_exam_type or profile.primary_exam_type

        active_catalog = []
        active_names: set[str] = set()
        active_codes: set[str] = set()
        if effective:
            active_catalog = await self.learning_profile_service.repo.list_catalog(
                exam_type=effective
            )
            active_names = {c.name.lower() for c in active_catalog}
            active_codes = {c.code.lower() for c in active_catalog}

        today_plans = await self.study_plan_repo.list_for_user(user.id, today)
        if active_names:
            scoped_plans = [
                p
                for p in today_plans
                if (p.subject or "").strip().lower() in active_names
            ]
            # Hiç eşleşme yoksa (eski serbest metin) tümünü gösterme — boş tercih
            today_plans = scoped_plans

        overview = await self.statistics_service.get_overview(user.id)
        recent_activities = await self.activity_service.get_recent_for_dashboard(user.id)
        today_questions = await self.question_service.today_question_count(user.id)
        top_rec = await self.ai_service.get_top_recommendation(user.id)
        weekly_goals = await self.goal_service.weekly_summary(
            user.id, exam_type=effective
        )
        resources = await self.resource_service.dashboard_summary(user.id)
        exams = await self.exam_service.dashboard_summary(
            user.id, exam_type=effective
        )
        planner = await self.planner_service.dashboard_summary(user.id)
        revision = await self.revision_service.dashboard_summary(user.id)
        achievement = await self.achievement_service.dashboard_summary(user.id)
        journey = await self.learning_profile_service.journey_progress(user.id)

        subjects = list(profile.subjects)
        if effective:
            names = active_names
            codes = active_codes
            if names or codes:
                filtered = [
                    s
                    for s in subjects
                    if s.subject_name.lower() in names
                    or (s.subject_code and s.subject_code.lower() in codes)
                ]
                if filtered:
                    subjects = filtered

        completed_plan_count = sum(1 for p in today_plans if p.status == StudyPlanStatus.COMPLETED)
        estimated_total = sum(p.estimated_minutes for p in today_plans)
        daily_goal = (
            estimated_total
            if today_plans
            else (profile.daily_study_minutes or DEFAULT_DAILY_STUDY_GOAL_MINUTES)
        )
        progress_percentage = self._calculate_progress(overview.today_study_minutes, daily_goal)

        # Sprint-3.1.B — Primary / Active target summaries for Hero
        primary_row = next((t for t in targets if t.is_primary), None)
        if primary_row is None and targets:
            primary_row = targets[0]
        active_row = None
        if effective:
            active_row = next(
                (t for t in targets if str(t.exam_type) == effective), None
            )
        primary_target = _exam_target_summary(primary_row) if primary_row else None
        active_target = (
            _exam_target_summary(active_row)
            if active_row
            else primary_target
        )

        # Alignment Sprint-1/3 — Today Projection (Decision SSOT → Topic Work Surface)
        topic_rows = await self.learning_profile_service.repo.list_topics(
            active_only=True
        )
        catalog_rows = await self.learning_profile_service.repo.list_catalog()
        name_by_code = {c.code: c.name for c in catalog_rows}
        if active_codes:
            topic_rows = [
                t for t in topic_rows if t.subject_code.lower() in active_codes
            ]
        catalog = [
            CatalogTopic(
                subject_code=t.subject_code,
                topic_code=t.code,
                topic_name=t.name,
                subject_name=name_by_code.get(t.subject_code),
            )
            for t in topic_rows
        ]
        nxt_rev = await self.revision_service.repo.next_due_item(user.id)

        # ── LOS Module 4+5+6: Policy Decision → Today Engine + Living Plan ────
        # insufficient_data: Today Engine'in kendi observation string'ini kullan
        los_ai_reason: str | None = (
            top_rec.reason
            if top_rec and getattr(top_rec, "code", None) != "insufficient_data"
            else None
        )
        try:
            policy_engine = PolicyDecisionEngine(self.db)
            decision = await policy_engine.decide(user.id)
            if decision.policy in (Policy.SUGGEST, Policy.MUTATE_TODAY, Policy.MUTATE_PLAN):
                if decision.topic_code and decision.reason:
                    los_ai_reason = decision.reason
            # Observation state kapılarını kontrol et
            obs = ObservationMode(self.db)
            await obs.advance(user.id)
            # Module 6: Living Plan adapt (fire-and-forget)
            await maybe_run_living_plan_adapt(self.db, user.id)
        except Exception:
            pass  # LOS layer hatası Today Engine'i kesmez

        next_action = build_next_action(
            today_plans=today_plans,
            revision=revision,
            ai_reason=los_ai_reason,
            catalog=catalog,
            revision_subject=nxt_rev.subject if nxt_rev else None,
            revision_topic=nxt_rev.topic if nxt_rev else None,
            exam_type=effective,
        )
        today_context_lines = build_today_context_lines(
            today_plan_count=len(today_plans),
            completed_plan_count=completed_plan_count,
            revision_due_today=revision.due_today if revision else 0,
        )
        today_journey_line = build_journey_line(
            active_exam_type=effective,
            days_remaining=journey.days_remaining if journey else None,
            primary_university=(
                primary_target.target_university if primary_target else None
            ),
            primary_department=(
                primary_target.target_department if primary_target else None
            ),
        )

        obs_state: str | None = None
        try:
            obs_state = student.observation_state
        except Exception:
            pass

        # Sprint 13 — Notification Decision (fire-and-forget; dashboard'u bozma)
        try:
            from app.services.notification_decision_service import (
                NotificationDecisionService,
            )

            decisions = await NotificationDecisionService(self.db).evaluate(user.id)
            if decisions:
                import logging

                logging.getLogger(__name__).debug(
                    "notification decisions user=%s count=%s types=%s",
                    user.id,
                    len(decisions),
                    [d.get("type") for d in decisions],
                )
        except Exception:
            pass

        # Sprint 15 — Home Feed + Insights (read-only)
        # Sprint 18 — Challenge cards prepend (Sense only; Decision yok)
        learning_feed = []
        insight_cards = []
        try:
            from app.schemas.learning_intelligence import FeedCard
            from app.services.assessment_service import AssessmentService
            from app.services.learning_intelligence_service import LearningIntelligenceService

            challenge_cards: list[FeedCard] = []
            try:
                bundle = await AssessmentService(self.db).daily_bundle(user.id)
                if bundle.daily and bundle.daily.status != "completed":
                    challenge_cards.append(
                        FeedCard(
                            id="feed-daily-challenge",
                            title="Günün Denemesi",
                            subtitle="Aktif sınavının tam kitapçığı — çöz veya PDF+optik",
                            kind="quiz",
                            subject_code=None,
                            topic_code=None,
                            deep_link_hint="/assessment/daily",
                            tone="positive",
                        )
                    )
                # Branş kartı Today'de gösterilmez — "Günün Denemesi · Türkçe"
                # sanılıyordu; branş Assessment ekranında kalsın.
                overview_a = await AssessmentService(self.db).overview(user.id)
                if overview_a.progress_pct < 100:
                    challenge_cards.append(
                        FeedCard(
                            id="feed-assessment-progress",
                            title="İlk kalibrasyon",
                            subtitle=overview_a.message,
                            kind="insight",
                            deep_link_hint="/assessment",
                            tone="caution" if overview_a.progress_pct < 50 else "neutral",
                        )
                    )
            except Exception:
                challenge_cards = []

            intel = LearningIntelligenceService(self.db)
            learning_feed = challenge_cards + await intel.home_feed(
                user.id, limit=8, subject_codes=active_codes or None
            )
            learning_feed = learning_feed[:10]
            insight_cards = await intel.home_insights(
                user.id, limit=4, subject_codes=active_codes or None
            )
        except Exception:
            pass

        # Sprint 20 — Coach Today (Experience; Next Action ile tutarlı)
        coach_today = None
        try:
            from app.services.coach_service import CoachService

            coach_today = (await CoachService(self.db).today(user.id)).message
        except Exception:
            pass

        return DashboardResponse(
            first_name=user.first_name,
            daily_study_goal_minutes=daily_goal,
            today_study_minutes=overview.today_study_minutes,
            today_questions_solved=today_questions,
            today_studied_topic=self._current_topic(today_plans) or overview.most_studied_topic,
            daily_progress_percentage=progress_percentage,
            last_login_at=user.last_login_at,
            today_plan_count=len(today_plans),
            completed_plan_count=completed_plan_count,
            today_plans=[StudyPlanRead.model_validate(p) for p in today_plans],
            streak_days=overview.streak_days,
            total_pomodoros=overview.total_pomodoros,
            total_study_minutes=overview.total_study_minutes,
            average_session_minutes=overview.average_session_minutes,
            most_studied_subject=overview.most_studied_subject,
            week_study_minutes=overview.week_study_minutes,
            recent_activities=recent_activities,
            today_ai_recommendation=top_rec.message if top_rec else None,
            today_ai_recommendation_code=top_rec.code if top_rec else None,
            today_ai_recommendation_reason=top_rec.reason if top_rec else None,
            weekly_goals=weekly_goals,
            today_resources_opened=resources.today_opened_count,
            today_resources_completed=resources.today_completed_count,
            recent_resources=resources.recent_items,
            last_exam_title=exams.last_exam_title,
            last_exam_net=exams.last_exam_net,
            last_exam_delta_net=exams.last_exam_delta_net,
            last_exam_date=exams.last_exam_date,
            today_ai_exam_summary=exams.today_ai_exam_summary,
            planner_summary=planner if planner.draft_id else None,
            revision_summary=revision,
            achievement_summary=achievement,
            journey_progress=journey,
            my_subjects=subjects,
            subjects_summary=await self._subjects_summary_vs_target(
                user.id,
                subjects,
                primary_exam_type=profile.primary_exam_type
                or (journey.primary_exam_type if journey else None),
            ),
            active_exam_type=effective,
            primary_exam_type=profile.primary_exam_type,
            primary_target=primary_target,
            active_target=active_target,
            next_action=next_action,
            today_context_lines=today_context_lines,
            today_journey_line=today_journey_line,
            observation_state=obs_state,
            learning_feed=learning_feed,
            insight_cards=insight_cards,
            coach_today=coach_today,
        )

    async def _subjects_summary_vs_target(
        self,
        user_id,
        subjects,
        *,
        primary_exam_type: str | None,
    ):
        """Prefer exam net vs user target; fall back to accuracy summary."""
        summary = self.learning_profile_service.build_subjects_summary(
            subjects,
            primary_exam_type=primary_exam_type,
        )
        try:
            from app.services.subject_net_targets import (
                below_target_sorted,
                gaps_from_trends,
                resolve_user_target_net,
            )

            trends = await ExamService(self.db).get_trends(user_id)
            user_target = await resolve_user_target_net(self.db, user_id)
            gaps = gaps_from_trends(
                by_subject=trends.by_subject, user_target_net=user_target
            )
            below = below_target_sorted(gaps)
            if below:
                summary = summary.model_copy(
                    update={"weakest_subject": below[0].subject}
                )
            else:
                summary = summary.model_copy(update={"weakest_subject": None})
        except Exception:
            pass
        return summary

    @staticmethod
    def _current_topic(plans: list[StudyPlan]) -> str | None:
        in_progress = next((p for p in plans if p.status == StudyPlanStatus.IN_PROGRESS), None)
        if in_progress is not None:
            return in_progress.topic or in_progress.subject
        completed = [p for p in plans if p.status == StudyPlanStatus.COMPLETED]
        if completed:
            latest = max(completed, key=lambda p: p.updated_at)
            return latest.topic or latest.subject
        return None

    @staticmethod
    def _calculate_progress(completed_minutes: int, goal_minutes: int) -> float:
        if goal_minutes <= 0:
            return 0.0
        return min(round((completed_minutes / goal_minutes) * 100, 1), 100.0)
