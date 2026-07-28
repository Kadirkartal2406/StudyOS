"""
StudyOS — Achievement Service
Sprint-2.9 — data-driven check/unlock/explain (U1)
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AI_CONTEXT_ACHIEVEMENTS
from app.core.exceptions import NotFoundError
from app.models.achievement import UserAchievement
from app.models.activity import Activity, ActivityEventType
from app.models.goal import Goal, GoalStatus
from app.models.planner_draft import PlannerDraft, PlannerDraftStatus
from app.models.revision import RevisionItem, RevisionItemStatus, RevisionReview
from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.repositories.achievement_repository import AchievementRepository
from app.schemas.achievement import (
    AchievementCheckRequest,
    AchievementCheckResponse,
    AchievementExplainResponse,
    AchievementProgressRead,
    AchievementRead,
    DashboardAchievementSummary,
    UserAchievementRead,
)
from app.services.activity_service import ActivityService
from app.services.ai.achievement_rule_engine import (
    build_reason,
    evaluate_criteria,
    progress_values,
)
from app.services.exam_service import ExamService
from app.services.notification_settings_service import NotificationSettingsService
from app.services.question_record_service import QuestionRecordService
from app.services.statistics_service import StatisticsService


class AchievementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AchievementRepository(db)
        self.activity = ActivityService(db)
        self.stats = StatisticsService(db)
        self.questions = QuestionRecordService(db)
        self.exams = ExamService(db)
        self.notif = NotificationSettingsService(db)

    def _ach_read(self, a) -> AchievementRead:
        return AchievementRead.model_validate(a)

    def _unlock_read(self, row: UserAchievement) -> UserAchievementRead:
        return UserAchievementRead(
            id=row.id,
            achievement_id=row.achievement_id,
            reason=row.reason,
            source_event=row.source_event,
            unlocked_at=row.unlocked_at,
            achievement=self._ach_read(row.achievement) if row.achievement else None,
        )

    async def _count_activity(self, user_id: uuid.UUID, event_type: str) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Activity)
            .where(Activity.user_id == user_id, Activity.event_type == event_type)
        )
        return int(result.scalar_one())

    async def _build_metrics(
        self, user_id: uuid.UUID, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        ctx = context or {}
        overview = await self.stats.get_overview(user_id)
        streak = await self.stats.get_streak(user_id)
        q = await self.questions.get_statistics_overview(user_id)
        exam_stats = await self.exams.get_statistics(user_id)

        rev_reviews = await self.db.execute(
            select(func.count())
            .select_from(RevisionReview)
            .join(RevisionItem, RevisionItem.id == RevisionReview.revision_item_id)
            .where(RevisionItem.user_id == user_id, RevisionItem.deleted_at.is_(None))
        )
        rev_mastered = await self.db.execute(
            select(func.count())
            .select_from(RevisionItem)
            .where(
                RevisionItem.user_id == user_id,
                RevisionItem.deleted_at.is_(None),
                RevisionItem.status == RevisionItemStatus.MASTERED,
            )
        )
        goals_completed = await self.db.execute(
            select(func.count())
            .select_from(Goal)
            .where(Goal.user_id == user_id, Goal.status == GoalStatus.COMPLETED)
        )
        goals = (
            await self.db.execute(select(Goal).where(Goal.user_id == user_id))
        ).scalars().all()
        milestone_25 = 0
        for g in goals:
            reached = list(g.milestones_reached or [])
            if "25" in reached or 25 in reached:
                milestone_25 += 1

        planner_gen = await self._count_activity(user_id, ActivityEventType.PLANNER_GENERATED)
        planner_acc = await self.db.execute(
            select(func.count())
            .select_from(PlannerDraft)
            .where(
                PlannerDraft.user_id == user_id,
                PlannerDraft.status == PlannerDraftStatus.ACCEPTED,
            )
        )

        milestones = list(ctx.get("exam_milestones") or ctx.get("milestones") or [])
        metrics: dict[str, Any] = {
            "total_pomodoros": float(overview.total_pomodoros),
            "total_study_minutes": float(overview.total_study_minutes),
            "total_questions": float(q.total_questions),
            "correct_rate": float(q.correct_rate),
            "exam_count": float(exam_stats.total_exams),
            "exam_milestone_new_record_net": 1.0 if "new_record_net" in milestones else 0.0,
            "revision_reviews": float(rev_reviews.scalar_one()),
            "revision_mastered": float(rev_mastered.scalar_one()),
            "goals_completed": float(goals_completed.scalar_one()),
            "goal_milestone_25_hits": float(milestone_25),
            "planner_generated_count": float(planner_gen),
            "planner_accepted_count": float(planner_acc.scalar_one()),
            "streak_days": float(streak.current_streak_days),
            "longest_streak": float(streak.longest_streak_days),
        }
        # Context overrides (event-local)
        for key, val in ctx.items():
            if key in ("milestones", "exam_milestones"):
                continue
            if isinstance(val, (int, float)):
                metrics[key] = float(val)
        return metrics

    async def list_catalog(self) -> list[AchievementRead]:
        return [self._ach_read(a) for a in await self.repo.list_active()]

    async def list_unlocked(self, user_id: uuid.UUID) -> list[UserAchievementRead]:
        return [self._unlock_read(r) for r in await self.repo.list_unlocked(user_id)]

    async def list_progress(self, user_id: uuid.UUID) -> list[AchievementProgressRead]:
        catalog = await self.repo.list_active()
        unlocked = await self.repo.unlocked_ids(user_id)
        metrics = await self._build_metrics(user_id)
        progress_rows = {
            p.achievement_id: p for p in await self.repo.list_progress(user_id)
        }
        out: list[AchievementProgressRead] = []
        for a in catalog:
            cur, tgt = progress_values(dict(a.criteria or {}), metrics)
            saved = progress_rows.get(a.id)
            if saved is not None:
                cur, tgt = saved.current_value, saved.target_value
            out.append(
                AchievementProgressRead(
                    achievement_id=a.id,
                    current_value=cur,
                    target_value=tgt,
                    unlocked=a.id in unlocked,
                    achievement=self._ach_read(a),
                )
            )
        return out

    async def get(self, achievement_id: uuid.UUID, user_id: uuid.UUID) -> dict[str, Any]:
        a = await self.repo.get_by_id(achievement_id)
        if a is None or not a.is_active:
            raise NotFoundError("Başarı", str(achievement_id))
        unlock = await self.repo.get_unlock(user_id, achievement_id)
        return {
            "achievement": self._ach_read(a),
            "unlocked": unlock is not None,
            "user_achievement": self._unlock_read(unlock) if unlock else None,
        }

    async def check(
        self, user_id: uuid.UUID, data: AchievementCheckRequest | None = None
    ) -> AchievementCheckResponse:
        data = data or AchievementCheckRequest()
        event = data.event
        metrics = await self._build_metrics(user_id, data.context)
        catalog = await self.repo.list_active()
        unlocked = await self.repo.unlocked_ids(user_id)
        newly: list[UserAchievement] = []
        evaluated = 0

        for a in catalog:
            criteria = dict(a.criteria or {})
            cur, tgt = progress_values(criteria, metrics)
            await self.repo.upsert_progress(user_id, a.id, cur, tgt)
            evaluated += 1
            if a.id in unlocked:
                continue
            if not evaluate_criteria(criteria, metrics, event=event):
                continue
            reason = build_reason(a.title, criteria, metrics)
            row = UserAchievement(
                user_id=user_id,
                achievement_id=a.id,
                reason=reason,
                source_event=event,
                metadata_={
                    "metric": criteria.get("metric"),
                    "value": metrics.get(str(criteria.get("metric"))),
                },
            )
            await self.repo.add_unlock(row)
            row.achievement = a
            newly.append(row)
            unlocked.add(a.id)
            await self.activity.record(
                user_id=user_id,
                event_type=ActivityEventType.ACHIEVEMENT_UNLOCKED,
                title=f"Rozet açıldı: {a.title}",
                description=reason,
                metadata={
                    "achievement_id": str(a.id),
                    "code": a.code,
                    "tier": str(a.tier),
                    "points": a.points,
                },
            )

        return AchievementCheckResponse(
            newly_unlocked=[self._unlock_read(r) for r in newly],
            evaluated=evaluated,
        )

    async def explain(
        self, achievement_id: uuid.UUID, user_id: uuid.UUID
    ) -> AchievementExplainResponse:
        a = await self.repo.get_by_id(achievement_id)
        if a is None:
            raise NotFoundError("Başarı", str(achievement_id))
        unlock = await self.repo.get_unlock(user_id, achievement_id)
        reason = unlock.reason if unlock else (
            f"«{a.title}» henüz açılmadı. Kriter: {a.criteria}"
        )
        system = (
            "Sen StudyOS çalışma koçusun. Rozeti sen açmadın; kural motoru açtı. "
            "Sana verilen reason'ı doğal Türkçe ile açıkla. Yeni rozet uydurma."
        )
        user_msg = (
            f"Rozet: {a.title} ({a.code})\n"
            f"Kategori: {a.category} · Seviye: {a.tier}\n"
            f"Gerekçe: {reason}\n"
            "Öğrenciye 2 kısa paragrafta kutla ve ne anlama geldiğini anlat."
        )
        pref = await self.notif.get_or_create(user_id)
        result = await generate_with_fallback(
            GenerateRequest(
                messages=[
                    ChatMessageDTO(role="system", content=system),
                    ChatMessageDTO(role="user", content=user_msg),
                ],
                context={"achievement_id": str(a.id)},
            ),
            preferred=pref.ai_preferred_provider,
            model=pref.ai_preferred_model,
        )
        return AchievementExplainResponse(
            achievement_id=a.id,
            explanation=result.text,
            provider=result.provider,
            used_fallback=result.used_fallback,
            reason=reason,
            code=a.code,
            title=a.title,
        )

    async def dashboard_summary(self, user_id: uuid.UUID) -> DashboardAchievementSummary:
        rows = await self.repo.list_unlocked(user_id)
        total_points = 0
        for r in rows:
            if r.achievement is not None:
                total_points += int(r.achievement.points)
        recent = rows[0] if rows else None
        return DashboardAchievementSummary(
            total_unlocked=len(rows),
            total_points=total_points,
            recent_title=recent.achievement.title if recent and recent.achievement else None,
            recent_reason=recent.reason if recent else None,
            recent_unlocked_at=recent.unlocked_at if recent else None,
        )

    async def context_payload(self, user_id: uuid.UUID) -> dict[str, Any]:
        rows = await self.repo.list_unlocked(user_id)
        summary = await self.dashboard_summary(user_id)
        return {
            "total_unlocked": summary.total_unlocked,
            "total_points": summary.total_points,
            "recent": [
                {
                    "code": r.achievement.code if r.achievement else None,
                    "title": r.achievement.title if r.achievement else None,
                    "reason": r.reason,
                }
                for r in rows[:AI_CONTEXT_ACHIEVEMENTS]
            ],
        }
