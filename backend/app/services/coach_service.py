"""
Sprint 20 — Adaptive AI Coach Service (LOS §13 Experience).
Decision / Confidence / Planner üretmez; mevcut LOS çıktılarını yorumlar.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.coach import (
    AssessmentCoachSummary,
    CoachFollowUp,
    CoachTimeline,
    CoachTimelineBundle,
    CoachTimelineItem,
    CoachTodayBundle,
    CoachTodayMessage,
    CoachWeeklyBundle,
    KnowledgeCoachHint,
)
from app.schemas.dashboard import NextActionProjection
from app.services.ai.achievement_detector import AchievementDetector
from app.services.ai.coach_message_builder import build_today_message
from app.services.ai_insights_service import AiInsightsService
from app.services.weekly_reflection_service import WeeklyReflectionService


class CoachService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.insights = AiInsightsService(db)
        self.wins = AchievementDetector(db)
        self.weekly = WeeklyReflectionService(db)

    async def today(self, user_id: uuid.UUID) -> CoachTodayBundle:
        # Aynı AsyncSession üzerinde concurrent query güvenli değil — sıralı okuma.
        next_action = await self._next_action(user_id)
        top = await self.insights.get_top_recommendation(user_id)
        wins = await self.wins.detect_wins(user_id)
        win = wins[0] if wins else None
        habit = await self._habit_hint(user_id)
        assessment_note, assessment_summary = await self._assessment_bits(user_id)
        revision_due = await self._revision_due(user_id)
        knowledge = await self._knowledge_hint(user_id, next_action)
        confidence = await self._confidence_for_action(user_id, next_action)

        message = build_today_message(
            next_action=next_action,
            insight_message=top.message if top else None,
            insight_reason=top.reason if top else None,
            confidence_level=confidence,
            assessment_note=assessment_note,
            habit_hint=habit,
            knowledge=knowledge,
            win=win,
            revision_due=revision_due,
        )
        if habit and not message.habit_hint:
            message.habit_hint = habit
        return CoachTodayBundle(message=message, assessment=assessment_summary)

    async def weekly(self, user_id: uuid.UUID) -> CoachWeeklyBundle:
        reflection = await self.weekly.build(user_id)
        return CoachWeeklyBundle(reflection=reflection)

    async def timeline(self, user_id: uuid.UUID) -> CoachTimelineBundle:
        # RC.2 — today() tekrar çağrılmaz (Dashboard zaten coach_today taşır)
        trends = await self.insights.get_trends(user_id)
        overview = await self.insights.get_overview(user_id)
        weekly = await self.weekly.build(user_id)

        today_line = weekly.body
        if overview.top_recommendation:
            today_line = overview.top_recommendation.message

        items = [
            CoachTimelineItem(
                period="last_month",
                title="Geçen ay",
                body=(
                    f"{trends.monthly_study_minutes} dk çalışma. "
                    + (
                        f"Önceki aya göre "
                        f"{'↑' if (trends.monthly_study_minutes or 0) >= (trends.previous_month_study_minutes or 0) else '↓'}."
                        if trends.previous_month_study_minutes
                        else "Temel oluşuyor."
                    )
                ),
                tone="neutral",
            ),
            CoachTimelineItem(
                period="this_week",
                title="Bu hafta",
                body=weekly.body,
                tone="positive" if weekly.questions_solved > 0 else "caution",
            ),
            CoachTimelineItem(
                period="today",
                title="Bugün",
                body=today_line,
                tone="positive",
            ),
            CoachTimelineItem(
                period="next",
                title="Bir sonraki hedef",
                body=weekly.weekly_suggestion,
                tone="neutral",
            ),
        ]
        next_goal = weekly.weekly_suggestion
        if overview.top_recommendation:
            next_goal = overview.top_recommendation.message
        return CoachTimelineBundle(
            timeline=CoachTimeline(items=items, next_goal=next_goal)
        )

    async def assessment_summary(self, user_id: uuid.UUID) -> AssessmentCoachSummary:
        _, summary = await self._assessment_bits(user_id)
        return summary or AssessmentCoachSummary(
            body="Henüz assessment sonucu yok — mini kalibrasyon ile başla."
        )

    async def explain_follow_ups(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        used_knowledge: bool = False,
    ) -> list[CoachFollowUp]:
        """M20.5 + M20.9 — Explain sonrası oku→çöz→tekrar."""
        q = f"subject_code={subject_code}&topic_code={topic_code}"
        steps = [
            CoachFollowUp(
                kind="knowledge" if used_knowledge else "explain",
                title="Önce kaynağı / açıklamayı özümse",
                detail="Ana fikri kendi cümlelerinle tekrar et",
                deep_link_hint=f"/subjects/{subject_code}/topics/{topic_code}",
                cta_label="Work Surface",
            ),
            CoachFollowUp(
                kind="quiz",
                title="Sonra 5 soru çöz",
                detail="Anladığını görmek için kısa quiz",
                deep_link_hint=f"/quiz-session?{q}",
                cta_label="Quiz",
            ),
            CoachFollowUp(
                kind="revision",
                title="Yarın tekrar et",
                detail="Revision kuyruğuna düşecek — Confidence yeniden ölçülür",
                deep_link_hint="/revisions",
                cta_label="Revision",
            ),
        ]
        return steps

    async def quiz_follow_up(
        self,
        *,
        accuracy_pct: float | None,
        subject_code: str | None,
        topic_code: str | None,
    ) -> CoachFollowUp:
        if accuracy_pct is not None and accuracy_pct >= 80:
            return CoachFollowUp(
                kind="rest",
                title="Bu konuda Explain'e şimdilik ihtiyacın kalmadı",
                detail="Confidence yükselişini korumak için kısa revision yeterli",
                deep_link_hint="/revisions",
                cta_label="Revision",
            )
        q = ""
        if subject_code and topic_code:
            q = f"?subject_code={subject_code}&topic_code={topic_code}"
        return CoachFollowUp(
            kind="explain",
            title="Hedefe uzak noktaları Explain ile netleştir",
            detail="Yanlışların üzerinden geç, sonra tekrar quiz",
            deep_link_hint=f"/subjects/{subject_code}/topics/{topic_code}" if subject_code and topic_code else "/subjects",
            cta_label="Açıkla",
        )

    # ── private readers ─────────────────────────────────────────

    async def _next_action(self, user_id: uuid.UUID) -> NextActionProjection | None:
        """Dashboard ile aynı Decision SSOT — yeniden karar üretmez, okur."""
        try:
            from datetime import date

            from app.models.study_plan import StudyPlan, StudyPlanStatus
            from app.services.ai.next_action_engine import CatalogTopic, build_next_action
            from app.services.learning_profile_service import LearningProfileService
            from app.services.revision_service import RevisionService
            from sqlalchemy import select

            lp = LearningProfileService(self.db)
            effective, _, _ = await lp.resolve_active_scope(user_id)
            revision = await RevisionService(self.db).dashboard_summary(user_id)
            top = await self.insights.get_top_recommendation(user_id)
            ai_reason = top.reason if top and top.code != "insufficient_data" else None

            today = date.today()
            plans = list(
                (
                    await self.db.scalars(
                        select(StudyPlan).where(
                            StudyPlan.user_id == user_id,
                            StudyPlan.plan_date == today,
                            StudyPlan.status != StudyPlanStatus.CANCELLED,
                        )
                    )
                ).all()
            )
            topic_rows = await lp.repo.list_topics(active_only=True)
            catalog_rows = await lp.repo.list_catalog()
            name_by_code = {c.code: c.name for c in catalog_rows}
            if effective:
                try:
                    subjects = await lp.list_my_subjects(user_id)
                    codes = {
                        s.subject_code.lower()
                        for s in subjects
                        if s.subject_code
                    }
                    if codes:
                        topic_rows = [
                            t
                            for t in topic_rows
                            if t.subject_code.lower() in codes
                        ]
                except Exception:
                    pass
            catalog = [
                CatalogTopic(
                    subject_code=t.subject_code,
                    topic_code=t.code,
                    topic_name=t.name,
                    subject_name=name_by_code.get(t.subject_code),
                )
                for t in topic_rows
            ]
            nxt_rev = await RevisionService(self.db).repo.next_due_item(user_id)
            return build_next_action(
                today_plans=plans,
                revision=revision,
                ai_reason=ai_reason,
                catalog=catalog,
                revision_subject=getattr(nxt_rev, "subject", None) if nxt_rev else None,
                revision_topic=getattr(nxt_rev, "topic", None) if nxt_rev else None,
                exam_type=effective,
            )
        except Exception:
            return None

    async def _habit_hint(self, user_id: uuid.UUID) -> str | None:
        try:
            from app.services.behavioral_memory_service import BehavioralMemoryService

            ctx = await BehavioralMemoryService(self.db).get_behavioral_context(user_id)
            peaks = ctx.get("peak_hours") or []
            if not peaks:
                prod = await self.insights.get_productivity(user_id)
                if prod.most_productive_hour is not None:
                    peaks = [prod.most_productive_hour]
            if not peaks:
                return None
            hours = ", ".join(f"{int(h):02d}:00" for h in peaks[:2])
            return (
                f"Son haftalarda {hours} civarında daha başarılısın. "
                "Bugünkü çalışmayı bu saatlere koymanı öneriyorum."
            )
        except Exception:
            return None

    async def _knowledge_hint(
        self, user_id: uuid.UUID, next_action: NextActionProjection | None
    ) -> KnowledgeCoachHint | None:
        if not next_action or not next_action.subject_code or not next_action.topic_code:
            return None
        try:
            from app.services.knowledge_service import KnowledgeService

            nb = await KnowledgeService(self.db).get_notebook(
                user_id,
                next_action.subject_code,
                next_action.topic_code,
            )
            if nb.chunk_count <= 0:
                return None
            page = None
            teach = None
            if nb.sources:
                s0 = nb.sources[0]
                teach = (
                    f"Kaynağın «{s0.title}» bu konuda iyi sinyal veriyor. "
                    "Önce kısa bir bölüm oku, sonra quiz."
                )
                page = "Kaynak özeti hazır"
            return KnowledgeCoachHint(
                summary=nb.ai_summary,
                teach_line=teach,
                page_hint=page,
                next_step="Önce kaynak, sonra quiz",
                deep_link_hint=(
                    f"/subjects/{next_action.subject_code}/topics/{next_action.topic_code}"
                ),
            )
        except Exception:
            return None

    async def _assessment_bits(
        self, user_id: uuid.UUID
    ) -> tuple[str | None, AssessmentCoachSummary | None]:
        try:
            from app.services.assessment_service import AssessmentService

            svc = AssessmentService(self.db)
            overview = await svc.overview(user_id)
            ranking = await svc.ranking(user_id)
            est = await svc.estimated_score(user_id)
            note = overview.message
            if overview.progress_pct < 100:
                note = f"Kalibrasyon %{overview.progress_pct:.0f} — {overview.message}"
            critical = est.weakest_subject
            summary = AssessmentCoachSummary(
                estimated_rank_label=ranking.label,
                critical_subject=critical,
                next_target=(
                    f"Hedefe uzak ders: {critical}"
                    if critical
                    else "Branş kalibrasyonunu tamamla"
                ),
                estimated_improvement=(
                    f"Tahmini başarı %{est.estimated_success_pct:.0f}; "
                    f"düzenli günlük deneme ile 1–2 haftada netleşme."
                ),
                body=(
                    f"{ranking.commentary} "
                    + (
                        f"Hedefe en uzak alan: {critical}. "
                        if critical
                        else "Hedefe uzak ders yok veya henüz net değil. "
                    )
                    + "Sonraki hedef: kalibrasyonu ilerletmek."
                ),
            )
            return note, summary
        except Exception:
            return None, None

    async def _revision_due(self, user_id: uuid.UUID) -> bool:
        try:
            from app.services.revision_service import RevisionService

            # dashboard-style summary if available
            due = await RevisionService(self.db).dashboard_summary(user_id)
            return bool(getattr(due, "due_today", 0) or getattr(due, "overdue", 0))
        except Exception:
            return False

    async def _confidence_for_action(
        self, user_id: uuid.UUID, next_action: NextActionProjection | None
    ) -> str | None:
        if not next_action or not next_action.topic_code:
            return None
        try:
            from app.services.confidence_engine import ConfidenceEngine

            conf = await ConfidenceEngine(self.db).get_for_topic(
                user_id, next_action.topic_code
            )
            if conf is None:
                return None
            return str(conf.confidence_level)
        except Exception:
            return None
