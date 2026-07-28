"""
StudyOS — Goal Progress Service
Sprint-2.1 (A1): event hook + create recompute; current_value persist.
Sprint-3.0.2: exam_recorded / revision_reviewed + product custom tipleri.
B1: Plan complete Study Time/Pomodoro/Question'a katkı yapmaz.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import GOAL_MILESTONE_PERCENTS
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.question_record import QuestionRecord
from app.models.study_session import StudySession, StudySessionStatus
from app.repositories.goal_repository import GoalRepository
from app.services.goal_product_types import ProductGoalType


@dataclass
class GoalProgressEvent:
    kind: str  # question_recorded | session_completed | plan_completed | exam_recorded | revision_reviewed
    amount: float = 0.0
    subject: str | None = None
    topic: str | None = None
    exam_type: str | None = None
    subject_nets: dict[str, float] | None = None
    occurred_on: date | None = None
    note: str | None = None


def calc_progress(current: float, target: float) -> float:
    """Tek progress dili — Journey / Goal / Dashboard aynı formül."""
    if target <= 0:
        return 0.0
    return min(round((current / target) * 100, 1), 100.0)


# Geriye uyumluluk alias
_calc_progress = calc_progress


def _apply_milestones(goal: Goal) -> list[str]:
    """Yeni geçen milestone'ları döner ve milestones_reached'e ekler."""
    reached = list(goal.milestones_reached or [])
    newly: list[str] = []
    for pct in GOAL_MILESTONE_PERCENTS:
        key = str(pct)
        if goal.progress >= pct and key not in reached:
            reached.append(key)
            newly.append(key)
    goal.milestones_reached = reached
    return newly


def _product(goal: Goal) -> ProductGoalType | None:
    raw = goal.product_goal_type
    if not raw:
        return None
    try:
        return ProductGoalType(str(raw))
    except ValueError:
        return None


def _append_log(
    goal: Goal,
    *,
    source: str,
    note: str | None,
    delta: float | None = None,
    value: float | None = None,
) -> None:
    meta = dict(goal.metadata_ or {})
    log = list(meta.get("progress_log") or [])
    entry: dict[str, Any] = {
        "at": datetime.now(UTC).isoformat(),
        "source": source,
    }
    if note:
        entry["note"] = note
    if delta is not None:
        entry["delta"] = round(delta, 2)
    if value is not None:
        entry["value"] = round(value, 2)
    log.append(entry)
    meta["progress_log"] = log[-20:]
    goal.metadata_ = meta


def _exam_type_matches(goal: Goal, event: GoalProgressEvent) -> bool:
    if not goal.exam_type or not event.exam_type:
        return True
    return str(goal.exam_type).lower() == str(event.exam_type).lower()


class GoalProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GoalRepository(db)

    async def apply_event(
        self, user_id: uuid.UUID, event: GoalProgressEvent
    ) -> list[tuple[Goal, list[str]]]:
        """Aktif hedeflere event uygula. (goal, newly_reached_milestones) listesi."""
        if event.kind == "plan_completed":
            # B1 — standart tipler Plan'dan güncellenmez
            return []

        day = event.occurred_on or datetime.now(UTC).date()
        goals = await self.repo.list_active(user_id)
        updated: list[tuple[Goal, list[str]]] = []

        for goal in goals:
            if day < goal.start_date or day > goal.end_date:
                continue
            if goal.status != GoalStatus.ACTIVE:
                continue

            changed = self._apply_to_goal(goal, event)
            if not changed:
                continue

            self._finalize(goal)
            newly = _apply_milestones(goal)
            updated.append((goal, newly))

        if updated:
            await self.db.flush()
            from app.schemas.achievement import AchievementCheckRequest
            from app.services.achievement_service import AchievementService

            await AchievementService(self.db).check(
                user_id, AchievementCheckRequest(event="goal_progress")
            )
        return updated

    async def recompute_goal(self, goal: Goal) -> list[str]:
        """Dönem içi Session/QR aggregate ile current_value yeniden hesapla."""
        product = _product(goal)
        if goal.goal_type == GoalType.CUSTOM or product in {
            ProductGoalType.NET_TARGET,
            ProductGoalType.SCORE_TARGET,
            ProductGoalType.RANK_TARGET,
            ProductGoalType.BRANCH_NET,
            ProductGoalType.EXAM_COUNT,
            ProductGoalType.REVISION_TARGET,
        }:
            # Product custom: event-driven; mevcut değeri koru
            self._finalize(goal)
            return _apply_milestones(goal)

        value = await self._aggregate_for_goal(goal)
        goal.current_value = float(value)
        self._finalize(goal)
        newly = _apply_milestones(goal)
        await self.db.flush()
        return newly

    def _finalize(self, goal: Goal) -> None:
        goal.progress = calc_progress(float(goal.current_value), float(goal.target_value))
        if goal.current_value >= goal.target_value and goal.status == GoalStatus.ACTIVE:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now(UTC)
            goal.progress = 100.0

    def _apply_to_goal(self, goal: Goal, event: GoalProgressEvent) -> bool:
        """True if current_value changed."""
        product = _product(goal)

        if event.kind == "exam_recorded":
            return self._apply_exam(goal, event, product)
        if event.kind == "revision_reviewed":
            return self._apply_revision(goal, event, product)

        delta = self._delta_for_engine(goal, event)
        if delta <= 0:
            return False
        goal.current_value = float(goal.current_value) + delta
        _append_log(
            goal,
            source=event.kind,
            note=event.note,
            delta=delta,
            value=float(goal.current_value),
        )
        return True

    def _apply_exam(
        self,
        goal: Goal,
        event: GoalProgressEvent,
        product: ProductGoalType | None,
    ) -> bool:
        if not _exam_type_matches(goal, event):
            return False

        if product == ProductGoalType.EXAM_COUNT:
            goal.current_value = float(goal.current_value) + 1.0
            _append_log(
                goal,
                source="exam_recorded",
                note=event.note or "Deneme kaydı",
                delta=1.0,
                value=float(goal.current_value),
            )
            return True

        if product == ProductGoalType.NET_TARGET:
            new_val = max(float(goal.current_value), float(event.amount))
            if new_val <= float(goal.current_value):
                return False
            goal.current_value = new_val
            _append_log(
                goal,
                source="exam_recorded",
                note=event.note or f"Toplam net {event.amount}",
                value=new_val,
            )
            return True

        if product == ProductGoalType.BRANCH_NET:
            if not goal.subject or not event.subject_nets:
                return False
            subject_key = goal.subject.lower()
            matched = None
            for subj, net in event.subject_nets.items():
                if subj.lower() == subject_key:
                    matched = float(net)
                    break
            if matched is None:
                return False
            new_val = max(float(goal.current_value), matched)
            if new_val <= float(goal.current_value):
                return False
            goal.current_value = new_val
            _append_log(
                goal,
                source="exam_recorded",
                note=event.note or f"{goal.subject} net {matched}",
                value=new_val,
            )
            return True

        if product == ProductGoalType.SCORE_TARGET and event.amount > 0:
            # Opsiyonel: amount score olarak verilirse
            meta_note = (event.note or "").lower()
            if "score" not in meta_note and "puan" not in meta_note:
                return False
            new_val = max(float(goal.current_value), float(event.amount))
            if new_val <= float(goal.current_value):
                return False
            goal.current_value = new_val
            _append_log(
                goal, source="exam_recorded", note=event.note, value=new_val
            )
            return True

        return False

    def _apply_revision(
        self,
        goal: Goal,
        event: GoalProgressEvent,
        product: ProductGoalType | None,
    ) -> bool:
        if product != ProductGoalType.REVISION_TARGET:
            return False
        if goal.subject and event.subject:
            if goal.subject.lower() != event.subject.lower():
                return False
        goal.current_value = float(goal.current_value) + max(event.amount, 1.0)
        _append_log(
            goal,
            source="revision_reviewed",
            note=event.note or "Tekrar tamamlandı",
            delta=max(event.amount, 1.0),
            value=float(goal.current_value),
        )
        return True

    def _delta_for_engine(self, goal: Goal, event: GoalProgressEvent) -> float:
        if event.kind == "question_recorded":
            if goal.goal_type == GoalType.QUESTION:
                return event.amount
            if goal.goal_type == GoalType.SUBJECT:
                if goal.subject and event.subject and goal.subject.lower() == event.subject.lower():
                    return event.amount
            if goal.goal_type == GoalType.TOPIC:
                if goal.topic and event.topic and goal.topic.lower() == event.topic.lower():
                    return event.amount
            return 0.0

        if event.kind == "session_completed":
            if goal.goal_type == GoalType.STUDY_TIME:
                return event.amount
            if goal.goal_type == GoalType.POMODORO:
                return 1.0
            return 0.0

        return 0.0

    # Geriye uyumluluk
    def _delta_for_goal(self, goal: Goal, event: GoalProgressEvent) -> float:
        return self._delta_for_engine(goal, event)

    async def _aggregate_for_goal(self, goal: Goal) -> float:
        start = datetime.combine(goal.start_date, datetime.min.time(), tzinfo=UTC)
        end = datetime.combine(
            goal.end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC
        )

        if goal.goal_type == GoalType.STUDY_TIME:
            result = await self.db.execute(
                select(func.coalesce(func.sum(StudySession.actual_duration_minutes), 0)).where(
                    StudySession.user_id == goal.user_id,
                    StudySession.status == StudySessionStatus.COMPLETED,
                    StudySession.started_at >= start,
                    StudySession.started_at < end,
                )
            )
            return float(result.scalar_one())

        if goal.goal_type == GoalType.POMODORO:
            result = await self.db.execute(
                select(func.count()).select_from(StudySession).where(
                    StudySession.user_id == goal.user_id,
                    StudySession.status == StudySessionStatus.COMPLETED,
                    StudySession.started_at >= start,
                    StudySession.started_at < end,
                )
            )
            return float(result.scalar_one())

        filters: list[Any] = [
            QuestionRecord.user_id == goal.user_id,
            QuestionRecord.created_at >= start,
            QuestionRecord.created_at < end,
        ]
        if goal.goal_type == GoalType.SUBJECT and goal.subject:
            filters.append(func.lower(QuestionRecord.subject) == goal.subject.lower())
        elif goal.goal_type == GoalType.TOPIC and goal.topic:
            filters.append(func.lower(QuestionRecord.topic) == goal.topic.lower())
        elif goal.goal_type != GoalType.QUESTION:
            return 0.0

        result = await self.db.execute(
            select(func.coalesce(func.sum(QuestionRecord.question_count), 0)).where(*filters)
        )
        return float(result.scalar_one())
