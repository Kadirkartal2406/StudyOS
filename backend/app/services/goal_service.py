"""
StudyOS — Goal Service
Sprint-2.1 (Meeting-019) — CRUD + progress özetleri.
Sprint-3.0.2 — product types, explain, enriched read.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.goal import Goal, GoalPeriod, GoalStatus
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import (
    GoalCreate,
    GoalExplainResponse,
    GoalListResponse,
    GoalProgressItem,
    GoalProgressLogEntry,
    GoalProgressResponse,
    GoalRead,
    GoalUpdate,
    WeeklyGoalSummaryItem,
)
from app.services.goal_product_types import (
    PRODUCT_GOAL_LABELS_TR,
    ProductGoalType,
    progress_sources_for,
    resolve_product_goal,
    unit_for,
)
from app.services.goal_progress_service import GoalProgressService, calc_progress


def remaining_of(goal: Goal) -> float:
    return max(0.0, float(goal.target_value) - float(goal.current_value))


def eta_days_of(goal: Goal, today: date | None = None) -> float | None:
    """Kalan değere ve dönem günlerine göre kabaca tahmini gün."""
    today = today or datetime.now(UTC).date()
    remaining = remaining_of(goal)
    if remaining <= 0:
        return 0.0
    days_elapsed = max((today - goal.start_date).days + 1, 1)
    rate = float(goal.current_value) / days_elapsed
    if rate <= 0:
        days_left = (goal.end_date - today).days
        return float(max(days_left, 0)) if days_left >= 0 else None
    return round(remaining / rate, 1)


def estimated_completion_of(goal: Goal) -> str | None:
    eta = eta_days_of(goal)
    if eta is None:
        return None
    if eta <= 0:
        return "Tamamlandı"
    today = datetime.now(UTC).date()
    finish = today + timedelta(days=int(round(eta)))
    if finish > goal.end_date:
        return f"~{goal.end_date.isoformat()} (dönem sonu)"
    return f"~{finish.isoformat()}"


def eta_hint_of(goal: Goal) -> str | None:
    eta = eta_days_of(goal)
    if eta is None:
        return None
    if eta <= 0:
        return "Tamamlandı"
    remaining = remaining_of(goal)
    today = datetime.now(UTC).date()
    days_left = max((goal.end_date - today).days, 1)
    per_day = round(remaining / days_left, 1)
    product = None
    if goal.product_goal_type:
        try:
            product = ProductGoalType(str(goal.product_goal_type))
        except ValueError:
            product = None
    unit = unit_for(product, goal.goal_type)
    return f"Günde ~{per_day} {unit}"


def why_created_of(goal: Goal) -> str:
    product = None
    if goal.product_goal_type:
        try:
            product = ProductGoalType(str(goal.product_goal_type))
        except ValueError:
            product = None
    label = (
        PRODUCT_GOAL_LABELS_TR.get(product, str(goal.goal_type))
        if product
        else str(goal.goal_type)
    )
    bits = [f'"{goal.title}" {label} hedefi olarak oluşturuldu.']
    if goal.exam_type:
        bits.append(f"Sınav bağlamı: {str(goal.exam_type).upper()}.")
    if goal.subject:
        bits.append(f"Ders: {goal.subject}.")
    if goal.description:
        bits.append(goal.description)
    return " ".join(bits)


# Aliases used by older imports / weekly
_remaining = remaining_of
_eta_days = eta_days_of
_eta_hint = eta_hint_of
_calc_progress = calc_progress


class GoalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GoalRepository(db)
        self.progress = GoalProgressService(db)

    def to_read(self, goal: Goal) -> GoalRead:
        meta = dict(goal.metadata_ or {})
        product = None
        if goal.product_goal_type:
            try:
                product = ProductGoalType(str(goal.product_goal_type))
            except ValueError:
                product = None
        raw_log = meta.get("progress_log") or []
        progress_log: list[GoalProgressLogEntry] = []
        for entry in raw_log:
            if not isinstance(entry, dict):
                continue
            progress_log.append(
                GoalProgressLogEntry(
                    at=str(entry.get("at", "")),
                    source=str(entry.get("source", "")),
                    note=entry.get("note"),
                    delta=float(entry["delta"]) if entry.get("delta") is not None else None,
                    value=float(entry["value"]) if entry.get("value") is not None else None,
                )
            )
        return GoalRead(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            goal_type=goal.goal_type,
            product_goal_type=product,
            target_value=float(goal.target_value),
            current_value=float(goal.current_value),
            progress=float(goal.progress),
            priority=goal.priority,
            period=goal.period,
            status=goal.status,
            subject=goal.subject,
            topic=goal.topic,
            exam_type=goal.exam_type,
            start_date=goal.start_date,
            end_date=goal.end_date,
            completed_at=goal.completed_at,
            metadata=meta,
            milestones_reached=list(goal.milestones_reached or []),
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            remaining=remaining_of(goal),
            eta_days=eta_days_of(goal),
            estimated_completion=estimated_completion_of(goal),
            progress_sources=progress_sources_for(product, goal.goal_type),
            progress_log=progress_log,
            why_created=why_created_of(goal),
        )

    async def create(self, user_id: uuid.UUID, data: GoalCreate) -> Goal:
        engine_type, period, product = await self._resolve_create_fields(user_id, data)
        exam_type = await self._resolve_exam_type(user_id, data.exam_type)
        if data.subject:
            await self._validate_subject(user_id, data.subject)
        start, end = self._resolve_dates(period, data.start_date, data.end_date)
        meta = dict(data.metadata or {})
        if product is not None:
            meta.setdefault("product_label", PRODUCT_GOAL_LABELS_TR.get(product, product.value))
        goal = Goal(
            user_id=user_id,
            title=data.title,
            description=data.description,
            goal_type=engine_type,
            product_goal_type=product.value if product else None,
            target_value=data.target_value,
            current_value=0.0,
            progress=0.0,
            priority=data.priority,
            period=period,
            status=GoalStatus.ACTIVE,
            subject=data.subject.strip() if data.subject else None,
            topic=data.topic.strip() if data.topic else None,
            exam_type=str(exam_type) if exam_type else None,
            start_date=start,
            end_date=end,
            metadata_=meta,
            milestones_reached=[],
        )
        await self.repo.add(goal)
        await self.progress.recompute_goal(goal)
        return goal

    async def _resolve_create_fields(
        self, _user_id: uuid.UUID, data: GoalCreate
    ) -> tuple:
        if data.product_goal_type is not None:
            engine_type, period, _spec = resolve_product_goal(data.product_goal_type)
            return engine_type, period, data.product_goal_type
        assert data.goal_type is not None and data.period is not None
        return data.goal_type, data.period, None

    async def _resolve_exam_type(self, user_id: uuid.UUID, requested) -> object | None:
        from app.services.learning_profile_service import LearningProfileService

        lp = LearningProfileService(self.db)
        profile = await lp.get_profile(user_id)
        allowed = {str(t.exam_type) for t in profile.exam_targets}
        # M17.3 — default Active Exam (Primary sadece Active yoksa)
        active = profile.active_exam_type
        primary = next((t for t in profile.exam_targets if t.is_primary), None)
        if not primary and profile.exam_targets:
            primary = profile.exam_targets[0]
        fallback = active or (primary.exam_type if primary else None)

        if requested is not None:
            et = str(requested)
            if allowed and et not in allowed:
                raise ValidationError(
                    f"Bu sınav tipi profilinizde yok: {et.upper()}",
                    field="exam_type",
                )
            return requested

        return fallback

    async def _validate_subject(self, user_id: uuid.UUID, subject: str) -> None:
        from app.services.learning_profile_service import LearningProfileService

        profile = await LearningProfileService(self.db).get_profile(user_id)
        names = {s.subject_name.lower() for s in profile.subjects if s.is_active}
        if names and subject.strip().lower() not in names:
            raise ValidationError(
                "Ders, aktif sınav ders listenizde yok",
                field="subject",
            )

    async def _scoped_exam_type(self, user_id: uuid.UUID, exam_type: str | None) -> str | None:
        from app.services.learning_profile_service import LearningProfileService

        if exam_type:
            return exam_type
        effective, _, _ = await LearningProfileService(self.db).resolve_active_scope(
            user_id
        )
        return effective

    async def get(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Goal:
        goal = await self.repo.get_by_id_for_user(goal_id, user_id)
        if goal is None:
            raise NotFoundError("Hedef", str(goal_id))
        return goal

    async def list_all(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        scoped = await self._scoped_exam_type(user_id, exam_type)
        return await self.repo.list_for_user(user_id, exam_type=scoped)

    async def list_active(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        scoped = await self._scoped_exam_type(user_id, exam_type)
        return await self.repo.list_active(user_id, exam_type=scoped)

    async def list_completed(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        scoped = await self._scoped_exam_type(user_id, exam_type)
        return await self.repo.list_completed(user_id, exam_type=scoped)

    async def list_weekly(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        scoped = await self._scoped_exam_type(user_id, exam_type)
        return await self.repo.list_by_period(
            user_id, GoalPeriod.WEEKLY, exam_type=scoped
        )

    async def list_monthly(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[Goal]:
        scoped = await self._scoped_exam_type(user_id, exam_type)
        return await self.repo.list_by_period(
            user_id, GoalPeriod.MONTHLY, exam_type=scoped
        )

    async def update(self, goal_id: uuid.UUID, user_id: uuid.UUID, data: GoalUpdate) -> Goal:
        goal = await self.get(goal_id, user_id)
        payload = data.model_dump(exclude_unset=True)
        if "metadata" in payload:
            goal.metadata_ = payload.pop("metadata") or {}
        if "exam_type" in payload and payload["exam_type"] is not None:
            et = await self._resolve_exam_type(user_id, payload["exam_type"])
            payload["exam_type"] = str(et) if et else None
        if "product_goal_type" in payload and payload["product_goal_type"] is not None:
            payload["product_goal_type"] = str(payload["product_goal_type"])
        if "subject" in payload and payload["subject"]:
            await self._validate_subject(user_id, payload["subject"])
        for key, value in payload.items():
            setattr(goal, key, value)
        if goal.end_date < goal.start_date:
            raise ValidationError("end_date, start_date'den önce olamaz", field="end_date")
        if data.current_value is not None:
            goal.progress = calc_progress(float(goal.current_value), float(goal.target_value))
            if goal.current_value >= goal.target_value and goal.status == GoalStatus.ACTIVE:
                goal.status = GoalStatus.COMPLETED
                goal.completed_at = datetime.now(UTC)
        elif data.start_date is not None or data.end_date is not None or data.target_value is not None:
            await self.progress.recompute_goal(goal)
        await self.db.flush()
        return goal

    async def delete(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> None:
        goal = await self.get(goal_id, user_id)
        await self.repo.delete(goal)

    async def get_progress(self, user_id: uuid.UUID) -> GoalProgressResponse:
        scoped = await self._scoped_exam_type(user_id, None)
        active = await self.list_active(user_id, exam_type=scoped)
        completed_count = await self.repo.count_by_status(
            user_id, GoalStatus.COMPLETED, exam_type=scoped
        )
        items = [
            GoalProgressItem(
                id=g.id,
                title=g.title,
                goal_type=g.goal_type,
                product_goal_type=(
                    ProductGoalType(str(g.product_goal_type))
                    if g.product_goal_type
                    else None
                ),
                period=g.period,
                progress=float(g.progress),
                current_value=float(g.current_value),
                target_value=float(g.target_value),
                remaining=remaining_of(g),
                eta_days=eta_days_of(g),
                estimated_completion=estimated_completion_of(g),
                status=g.status,
                milestones_reached=list(g.milestones_reached or []),
            )
            for g in active
        ]
        avg = (
            round(sum(i.progress for i in items) / len(items), 1) if items else 0.0
        )
        return GoalProgressResponse(
            items=items,
            active_count=len(items),
            completed_count=completed_count,
            average_progress=avg,
        )

    async def weekly_summary(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[WeeklyGoalSummaryItem]:
        today = datetime.now(UTC).date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        scoped = await self._scoped_exam_type(user_id, exam_type)
        goals = await self.repo.list_for_user(user_id, exam_type=scoped)
        items: list[WeeklyGoalSummaryItem] = []
        for g in goals:
            if g.status == GoalStatus.CANCELLED:
                continue
            overlaps = g.start_date <= week_end and g.end_date >= week_start
            if g.period == GoalPeriod.WEEKLY or (g.status == GoalStatus.ACTIVE and overlaps):
                if g.period != GoalPeriod.WEEKLY and g.status != GoalStatus.ACTIVE:
                    continue
                product = None
                if g.product_goal_type:
                    try:
                        product = ProductGoalType(str(g.product_goal_type))
                    except ValueError:
                        product = None
                items.append(
                    WeeklyGoalSummaryItem(
                        id=g.id,
                        title=g.title,
                        progress=float(g.progress),
                        current_value=float(g.current_value),
                        target_value=float(g.target_value),
                        remaining=remaining_of(g),
                        eta_hint=eta_hint_of(g),
                        estimated_completion=estimated_completion_of(g),
                        goal_type=g.goal_type,
                        product_goal_type=product,
                        status=g.status,
                    )
                )
        seen: set[uuid.UUID] = set()
        unique: list[WeeklyGoalSummaryItem] = []
        for item in items:
            if item.id in seen:
                continue
            seen.add(item.id)
            unique.append(item)
        return unique[:10]

    async def explain(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> GoalExplainResponse:
        """LLM yalnızca anlatır — hedef üretmez / progress değiştirmez."""
        from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
        from app.services.notification_settings_service import NotificationSettingsService

        goal = await self.get(goal_id, user_id)
        read = self.to_read(goal)
        sources = ", ".join(read.progress_sources) or "manuel"
        why_progressed = (
            f"İlerleme %{read.progress:.0f}: {read.current_value:.0f}/{read.target_value:.0f}. "
            f"Kaynaklar: {sources}."
        )
        if read.progress_log:
            last = read.progress_log[-1]
            why_progressed += f" Son güncelleme: {last.source}"
            if last.note:
                why_progressed += f" ({last.note})"
            why_progressed += "."

        remaining = read.remaining
        unit = unit_for(read.product_goal_type, goal.goal_type)
        if read.progress >= 100:
            why_stalled = "Hedef tamamlandı; duraklama yok."
            how_to = "Yeni bir hedef ekleyebilir veya mevcut hedefi arşivleyebilirsin."
        elif read.current_value <= 0:
            why_stalled = (
                "Henüz otomatik ilerleme kaydı yok. İlgili aktivite (soru/deneme/"
                "oturum/tekrar) tamamlandığında hedef ilerler."
            )
            how_to = f"Kalan {remaining:.0f} {unit} için ilgili aktiviteyi düzenli tamamla."
        else:
            why_stalled = (
                "İlerleme var; tempo düşükse dönem sonuna kadar yetişmeyebilir. "
                f"Tahmini: {read.estimated_completion or 'belirsiz'}."
            )
            how_to = (
                f"Kalan {remaining:.0f} {unit}. "
                f"{eta_hint_of(goal) or 'Günlük temposunu artır'}."
            )

        system = (
            "Sen StudyOS çalışma koçusun. Hedefleri sen oluşturmazsın; kural motoru "
            "ve kullanıcı oluşturur. Sana verilen why_progressed / why_stalled / "
            "how_to_complete bilgilerini doğal Türkçe ile açıkla. Yeni hedef uydurma, "
            "sayıları değiştirme."
        )
        user_msg = (
            f"Hedef: {goal.title}\n"
            f"Tür: {read.product_goal_type or goal.goal_type}\n"
            f"İlerleme: %{read.progress:.0f} ({read.current_value}/{read.target_value})\n"
            f"Neden ilerledi: {why_progressed}\n"
            f"Neden durdu: {why_stalled}\n"
            f"Nasıl tamamlanır: {how_to}\n"
            "Öğrenciye 2-3 kısa paragrafta açıkla."
        )
        pref = await NotificationSettingsService(self.db).get_or_create(user_id)
        result = await generate_with_fallback(
            GenerateRequest(
                messages=[
                    ChatMessageDTO(role="system", content=system),
                    ChatMessageDTO(role="user", content=user_msg),
                ],
                context={"goal_id": str(goal.id)},
            ),
            preferred=pref.ai_preferred_provider,
            model=pref.ai_preferred_model,
        )
        return GoalExplainResponse(
            goal_id=goal.id,
            explanation=result.text,
            provider=result.provider,
            used_fallback=result.used_fallback,
            why_progressed=why_progressed,
            why_stalled=why_stalled,
            how_to_complete=how_to,
            title=goal.title,
            progress=float(goal.progress),
        )

    def as_list_response(self, goals: list[Goal]) -> GoalListResponse:
        return GoalListResponse(items=[self.to_read(g) for g in goals])

    def _resolve_dates(
        self, period: GoalPeriod, start: date, end: date
    ) -> tuple[date, date]:
        if period == GoalPeriod.DAILY:
            return start, start
        if period == GoalPeriod.WEEKLY:
            monday = start - timedelta(days=start.weekday())
            return monday, monday + timedelta(days=6)
        if period == GoalPeriod.MONTHLY:
            month_start = start.replace(day=1)
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            return month_start, next_month - timedelta(days=1)
        return start, end
