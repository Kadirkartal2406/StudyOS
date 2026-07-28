"""
Sprint 15 — Learning Intelligence Service.
Mevcut Evidence / Confidence / Activity / Quiz / Policy verisini okur.
Yeni Decision / Confidence / Living Plan algoritması YOK.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.revision import RevisionItem, RevisionItemStatus
from app.models.study_resource import ResourceStatus, StudyResource
from app.models.study_session import StudySession
from app.models.topic_confidence import TopicConfidence
from app.models.topic_quiz import QuizGenerationStatus, TopicQuizGeneration
from app.repositories.learning_profile_repository import LearningProfileRepository
from app.schemas.learning_intelligence import (
    ConfidenceTrendItem,
    FeedCard,
    InsightCard,
    JourneyTrendsProjection,
    QuizHistoryItem,
    ResourceIntelligenceItem,
    TimelineEvent,
    TopicIntelligenceCard,
)


_LEVEL_TR = {
    "unknown": "Bilinmiyor",
    "low": "Düşük",
    "medium": "Orta",
    "high": "Yüksek",
    "conflicted": "Çelişkili",
}

_LEVEL_STARS = {
    "unknown": 1,
    "low": 2,
    "medium": 3,
    "high": 5,
    "conflicted": 2,
}


class LearningIntelligenceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = LearningProfileRepository(db)

    # ── M15.1 ──────────────────────────────────────────────────────────────

    async def topic_intelligence(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        topic_name: str,
        revision_due: bool = False,
        suggestion_fallback: str | None = None,
    ) -> TopicIntelligenceCard:
        conf = await self._get_confidence(user_id, topic_code)
        level = (conf.confidence_level if conf else "unknown") or "unknown"
        last_session = await self.db.scalar(
            select(StudySession)
            .where(
                StudySession.user_id == user_id,
                StudySession.topic_code == topic_code,
                StudySession.status == "finished",
            )
            .order_by(desc(StudySession.ended_at), desc(StudySession.updated_at))
            .limit(1)
        )
        last_quiz = await self.db.scalar(
            select(TopicQuizGeneration)
            .where(
                TopicQuizGeneration.user_id == user_id,
                TopicQuizGeneration.topic_code == topic_code,
                TopicQuizGeneration.status == QuizGenerationStatus.SUBMITTED,
            )
            .order_by(desc(TopicQuizGeneration.submitted_at))
            .limit(1)
        )

        last_studied = None
        if last_session is not None:
            when = last_session.ended_at or last_session.updated_at
            if when is not None:
                last_studied = self._relative(when)

        last_quiz_label = None
        if last_quiz is not None and last_quiz.correct_count is not None:
            total = max(int(last_quiz.valid_item_count or 0), 1)
            last_quiz_label = f"{last_quiz.correct_count} / {total}"

        weak = None
        if conf and conf.weighted_accuracy is not None and conf.weighted_accuracy < 0.55:
            weak = "Doğruluk oranı düşük — temel kavramları gözden geçir"
        elif revision_due:
            weak = "Tekrar zamanı geçmiş alt konular"

        if revision_due:
            headline = "Tekrar zamanı"
            suggestion = "Revision'ı tamamla"
        elif level == "high":
            headline = "İyi gidiyorsun"
            suggestion = suggestion_fallback or "5 soru çöz"
        elif level == "low":
            headline = "Destek gerekiyor"
            suggestion = suggestion_fallback or "Kısa bir quiz ile ölç"
        elif level == "conflicted":
            headline = "Karışık sinyaller"
            suggestion = suggestion_fallback or "Birkaç soru daha çöz"
        else:
            headline = "Öğrenme devam ediyor"
            suggestion = suggestion_fallback or "Bu konuda çalışmaya devam et"

        return TopicIntelligenceCard(
            topic_name=topic_name,
            headline=headline,
            stars=_LEVEL_STARS.get(level, 1),
            last_studied_label=last_studied,
            last_quiz_label=last_quiz_label,
            confidence_label=_LEVEL_TR.get(level, "Bilinmiyor"),
            confidence_level=level,
            weak_spot=weak,
            suggestion=suggestion,
        )

    # ── M15.2 ──────────────────────────────────────────────────────────────

    async def topic_timeline(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        limit: int = 20,
    ) -> list[TimelineEvent]:
        events: list[TimelineEvent] = []

        sessions = (
            await self.db.scalars(
                select(StudySession)
                .where(
                    StudySession.user_id == user_id,
                    StudySession.topic_code == topic_code,
                    StudySession.status == "finished",
                )
                .order_by(desc(StudySession.ended_at))
                .limit(limit)
            )
        ).all()
        for s in sessions:
            when = s.ended_at or s.updated_at or s.created_at
            mins = int(s.actual_duration_minutes or 0)
            events.append(
                TimelineEvent(
                    id=f"session:{s.id}",
                    kind="pomodoro",
                    title="Pomodoro",
                    subtitle=f"{mins} dk" if mins else None,
                    occurred_at=when,
                    relative_label=self._relative(when),
                    deep_link_hint=f"/session-history/{s.id}",
                )
            )

        quizzes = (
            await self.db.scalars(
                select(TopicQuizGeneration)
                .where(
                    TopicQuizGeneration.user_id == user_id,
                    TopicQuizGeneration.topic_code == topic_code,
                    TopicQuizGeneration.status.in_(
                        [QuizGenerationStatus.SUBMITTED, QuizGenerationStatus.READY]
                    ),
                )
                .order_by(desc(TopicQuizGeneration.created_at))
                .limit(limit)
            )
        ).all()
        for q in quizzes:
            when = q.submitted_at or q.created_at
            if q.status == QuizGenerationStatus.SUBMITTED and q.correct_count is not None:
                total = max(int(q.valid_item_count or 0), 1)
                sub = f"{q.correct_count}/{total}"
                title = "Quiz çözdün"
            else:
                sub = f"{q.valid_item_count} soru"
                title = "Quiz üretildi"
            events.append(
                TimelineEvent(
                    id=f"quiz:{q.id}",
                    kind="quiz",
                    title=title,
                    subtitle=sub,
                    occurred_at=when,
                    relative_label=self._relative(when),
                    deep_link_hint=f"/quiz-session?generation_id={q.id}&subject_code={subject_code}&topic_code={topic_code}",
                )
            )

        topic_row = await self.profile_repo.get_topic_by_code(topic_code)
        topic_name_l = (topic_row.name if topic_row else topic_code).strip().lower()

        revisions = (
            await self.db.scalars(
                select(RevisionItem)
                .where(
                    RevisionItem.user_id == user_id,
                    RevisionItem.deleted_at.is_(None),
                    RevisionItem.status == RevisionItemStatus.ACTIVE,
                )
                .order_by(desc(RevisionItem.updated_at))
                .limit(limit * 2)
            )
        ).all()
        for r in revisions:
            r_topic = (r.topic or "").strip().lower()
            if not r_topic:
                continue
            if (
                r_topic != topic_code.lower()
                and r_topic != topic_name_l
                and topic_name_l not in r_topic
                and r_topic not in topic_name_l
            ):
                continue
            when = r.updated_at or r.created_at
            events.append(
                TimelineEvent(
                    id=f"revision:{r.id}",
                    kind="revision",
                    title="Revision",
                    subtitle=r.topic,
                    occurred_at=when,
                    relative_label=self._relative(when),
                    deep_link_hint="/revisions",
                )
            )

        # Activities that mention topic in metadata
        activities = (
            await self.db.scalars(
                select(Activity)
                .where(Activity.user_id == user_id)
                .order_by(desc(Activity.occurred_at))
                .limit(40)
            )
        ).all()
        for a in activities:
            meta = a.metadata_ or {}
            meta_topic = str(meta.get("topic_code") or meta.get("topic") or "").lower()
            if meta_topic and (
                meta_topic == topic_code.lower() or topic_name_l in meta_topic
            ):
                events.append(
                    TimelineEvent(
                        id=f"activity:{a.id}",
                        kind="activity",
                        title=a.title,
                        subtitle=a.description,
                        occurred_at=a.occurred_at,
                        relative_label=self._relative(a.occurred_at),
                        deep_link_hint=None,
                    )
                )

        events.sort(key=lambda e: e.occurred_at, reverse=True)
        return events[:limit]

    # ── M15.3 ──────────────────────────────────────────────────────────────

    async def topic_insights(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        topic_name: str,
        revision_due: bool = False,
    ) -> list[InsightCard]:
        cards: list[InsightCard] = []
        conf = await self._get_confidence(user_id, topic_code)
        q = f"subject_code={subject_code}&topic_code={topic_code}"

        if conf and conf.days_since_last_evidence is not None and conf.days_since_last_evidence >= 5:
            cards.append(
                InsightCard(
                    id=f"idle:{topic_code}",
                    code="topic_idle",
                    message=f"Son çalışmandan beri {conf.days_since_last_evidence} gün geçti.",
                    subject_code=subject_code,
                    topic_code=topic_code,
                    topic_name=topic_name,
                    tone="caution",
                    deep_link_hint=f"/pomodoro?{q}",
                )
            )

        if conf and conf.trend_direction > 0.15:
            cards.append(
                InsightCard(
                    id=f"rising:{topic_code}",
                    code="confidence_rising",
                    message="Confidence yükselmeye başladı.",
                    subject_code=subject_code,
                    topic_code=topic_code,
                    topic_name=topic_name,
                    tone="positive",
                    deep_link_hint=f"/subjects/{subject_code}/topics/{topic_code}",
                )
            )
        elif conf and conf.trend_direction < -0.15:
            cards.append(
                InsightCard(
                    id=f"falling:{topic_code}",
                    code="confidence_falling",
                    message="Confidence son dönemde düşüş gösteriyor.",
                    subject_code=subject_code,
                    topic_code=topic_code,
                    topic_name=topic_name,
                    tone="caution",
                    deep_link_hint=f"/quiz-session?{q}",
                )
            )

        recent_quizzes = (
            await self.db.scalars(
                select(TopicQuizGeneration)
                .where(
                    TopicQuizGeneration.user_id == user_id,
                    TopicQuizGeneration.topic_code == topic_code,
                    TopicQuizGeneration.status == QuizGenerationStatus.SUBMITTED,
                )
                .order_by(desc(TopicQuizGeneration.submitted_at))
                .limit(3)
            )
        ).all()
        if len(recent_quizzes) >= 2:
            accs = []
            for g in recent_quizzes:
                total = max(int(g.valid_item_count or 0), 1)
                accs.append((g.correct_count or 0) / total)
            if all(a < 0.7 for a in accs):
                cards.append(
                    InsightCard(
                        id=f"quiz_weak:{topic_code}",
                        code="quiz_weak_spot",
                        message=f"Bu konuda son {len(accs)} quizde doğruluk düşük kaldı.",
                        subject_code=subject_code,
                        topic_code=topic_code,
                        topic_name=topic_name,
                        tone="caution",
                        deep_link_hint=f"/quiz-session?{q}",
                    )
                )

        if revision_due:
            cards.append(
                InsightCard(
                    id=f"rev:{topic_code}",
                    code="revision_due",
                    message="Bu konu için tekrar zamanı geldi.",
                    subject_code=subject_code,
                    topic_code=topic_code,
                    topic_name=topic_name,
                    tone="caution",
                    deep_link_hint=f"/revisions?{q}",
                )
            )

        return cards[:4]

    # ── M15.5 ──────────────────────────────────────────────────────────────

    async def quiz_history(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        limit: int = 20,
    ) -> list[QuizHistoryItem]:
        rows = (
            await self.db.scalars(
                select(TopicQuizGeneration)
                .where(
                    TopicQuizGeneration.user_id == user_id,
                    TopicQuizGeneration.topic_code == topic_code,
                    TopicQuizGeneration.status.in_(
                        [
                            QuizGenerationStatus.READY,
                            QuizGenerationStatus.SUBMITTED,
                            QuizGenerationStatus.FAILED,
                        ]
                    ),
                )
                .order_by(desc(TopicQuizGeneration.created_at))
                .limit(limit)
            )
        ).all()
        items: list[QuizHistoryItem] = []
        for g in rows:
            total = max(int(g.valid_item_count or g.requested_count or 0), 0)
            accuracy = None
            if g.status == QuizGenerationStatus.SUBMITTED and total > 0:
                accuracy = round(((g.correct_count or 0) / total) * 100, 1)
            when = g.submitted_at or g.created_at
            items.append(
                QuizHistoryItem(
                    id=g.id,
                    question_count=total or g.requested_count,
                    accuracy_pct=accuracy,
                    correct_count=g.correct_count,
                    wrong_count=g.wrong_count,
                    blank_count=g.blank_count,
                    status=g.status,
                    difficulty=g.difficulty,
                    relative_label=self._relative(when),
                    created_at=g.created_at,
                    submitted_at=g.submitted_at,
                )
            )
        return items

    # ── M15.6 ──────────────────────────────────────────────────────────────

    async def resource_intelligence(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        confidence_level: str | None = None,
        revision_due: bool = False,
    ) -> list[ResourceIntelligenceItem]:
        # M17.2 — Topic-first only (no subject-wide OR leak)
        rows = (
            await self.db.scalars(
                select(StudyResource)
                .where(
                    StudyResource.user_id == user_id,
                    StudyResource.subject_code == subject_code,
                    StudyResource.topic_code == topic_code,
                    StudyResource.status != ResourceStatus.ARCHIVED,
                )
                .order_by(StudyResource.order_index.asc(), desc(StudyResource.updated_at))
                .limit(30)
            )
        ).all()
        level = confidence_level or "unknown"
        now = datetime.now(UTC)
        ks_by_resource: dict = {}
        try:
            from app.models.knowledge import KnowledgeSource

            ks_rows = (
                await self.db.scalars(
                    select(KnowledgeSource).where(
                        KnowledgeSource.user_id == user_id,
                        KnowledgeSource.subject_code == subject_code,
                        KnowledgeSource.topic_code == topic_code,
                    )
                )
            ).all()
            ks_by_resource = {s.study_resource_id: s for s in ks_rows}
        except Exception:
            ks_by_resource = {}

        items: list[ResourceIntelligenceItem] = []
        for r in rows:
            label = self._resource_label(
                status=str(r.status),
                confidence_level=level,
                revision_due=revision_due,
                last_opened_at=r.last_opened_at,
                now=now,
            )
            ks = ks_by_resource.get(r.id)
            items.append(
                ResourceIntelligenceItem(
                    id=r.id,
                    title=r.title,
                    resource_type=str(r.resource_type),
                    status=str(r.status),
                    intelligence_label=label,
                    url=r.url,
                    provider=r.provider,
                    knowledge_health=ks.health if ks else None,
                    chunk_count=ks.chunk_count if ks else 0,
                    citation_count=ks.citation_count if ks else 0,
                    quiz_generated_count=ks.quiz_generated_count if ks else 0,
                    used_by_ai=bool(ks.used_by_ai) if ks else False,
                    last_explain_at=(
                        ks.last_explain_at.isoformat()
                        if ks and ks.last_explain_at
                        else None
                    ),
                    last_quiz_at=(
                        ks.last_quiz_at.isoformat()
                        if ks and ks.last_quiz_at
                        else None
                    ),
                )
            )
        # Recently opened first, then order_index already applied by query
        items.sort(
            key=lambda x: (
                0 if "Son kullanılan" in x.intelligence_label else 1,
                x.title.lower(),
            )
        )
        return items

    def _resource_label(
        self,
        *,
        status: str,
        confidence_level: str,
        revision_due: bool,
        last_opened_at: datetime | None = None,
        now: datetime | None = None,
    ) -> str:
        """Honest labels only — no fake AI Suggested / Recommended taxonomy."""
        st = status.split(".")[-1].lower()
        if last_opened_at is not None and now is not None:
            age = now - (
                last_opened_at
                if last_opened_at.tzinfo
                else last_opened_at.replace(tzinfo=UTC)
            )
            if age <= timedelta(days=7):
                return "Son kullanılan"
        if st == "not_started":
            if confidence_level == "low":
                return "Zayıf alan — öncelikli"
            if revision_due:
                return "Tekrar öncesi göz at"
            return "Henüz çalışılmadı"
        if st == "in_progress":
            return "Devam ediyor"
        if st == "completed":
            return "Tamamlandı"
        return "Kaynak hazır"

    # ── M15.4 Home Feed ────────────────────────────────────────────────────

    async def home_feed(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 8,
        subject_codes: set[str] | None = None,
    ) -> list[FeedCard]:
        cards: list[FeedCard] = []
        now = datetime.now(UTC)
        codes = {c.lower() for c in subject_codes} if subject_codes else None
        confs = (
            await self.db.scalars(
                select(TopicConfidence)
                .where(TopicConfidence.user_id == user_id)
                .order_by(desc(TopicConfidence.updated_at))
                .limit(40)
            )
        ).all()
        if codes:
            confs = [c for c in confs if c.subject_code.lower() in codes]

        for c in confs:
            topic = await self.profile_repo.get_topic_by_code(c.topic_code)
            name = topic.name if topic else c.topic_code
            link = f"/subjects/{c.subject_code}/topics/{c.topic_code}"
            if c.trend_direction > 0.15:
                cards.append(
                    FeedCard(
                        id=f"feed-rise:{c.topic_code}",
                        title=name,
                        subtitle="Confidence yükseliyor",
                        kind="confidence",
                        subject_code=c.subject_code,
                        topic_code=c.topic_code,
                        deep_link_hint=link,
                        tone="positive",
                    )
                )
            elif c.days_since_last_evidence is not None and c.days_since_last_evidence >= 5:
                cards.append(
                    FeedCard(
                        id=f"feed-idle:{c.topic_code}",
                        title=name,
                        subtitle=f"{c.days_since_last_evidence} gündür çalışılmadı",
                        kind="insight",
                        subject_code=c.subject_code,
                        topic_code=c.topic_code,
                        deep_link_hint=link,
                        tone="caution",
                    )
                )
            elif c.confidence_level == "low":
                cards.append(
                    FeedCard(
                        id=f"feed-low:{c.topic_code}",
                        title=name,
                        subtitle="Hedefe yaklaşmak için bak",
                        kind="insight",
                        subject_code=c.subject_code,
                        topic_code=c.topic_code,
                        deep_link_hint=link,
                        tone="caution",
                    )
                )

        # Revision due (schedule.due_at)
        from app.models.revision import RevisionSchedule

        due_rows = (
            await self.db.execute(
                select(RevisionItem, RevisionSchedule)
                .join(
                    RevisionSchedule,
                    RevisionSchedule.revision_item_id == RevisionItem.id,
                )
                .where(
                    RevisionItem.user_id == user_id,
                    RevisionItem.deleted_at.is_(None),
                    RevisionItem.status == RevisionItemStatus.ACTIVE,
                    RevisionSchedule.due_at <= now + timedelta(days=1),
                )
                .order_by(RevisionSchedule.due_at.asc())
                .limit(5)
            )
        ).all()
        for r, _sched in due_rows:
            cards.append(
                FeedCard(
                    id=f"feed-rev:{r.id}",
                    title=r.topic or r.subject or "Tekrar",
                    subtitle="Revision zamanı geldi",
                    kind="revision",
                    deep_link_hint="/revisions",
                    tone="caution",
                )
            )

        # Recent quiz outcomes
        quizzes = (
            await self.db.scalars(
                select(TopicQuizGeneration)
                .where(
                    TopicQuizGeneration.user_id == user_id,
                    TopicQuizGeneration.status == QuizGenerationStatus.SUBMITTED,
                )
                .order_by(desc(TopicQuizGeneration.submitted_at))
                .limit(10)
            )
        ).all()
        if codes:
            quizzes = [g for g in quizzes if g.subject_code.lower() in codes]
        for g in quizzes:
            total = max(int(g.valid_item_count or 0), 1)
            pct = round(((g.correct_count or 0) / total) * 100)
            cards.append(
                FeedCard(
                    id=f"feed-quiz:{g.id}",
                    title=g.topic_name or g.topic_code,
                    subtitle=f"Son quiz {g.correct_count}/{total} (%{pct})",
                    kind="quiz",
                    subject_code=g.subject_code,
                    topic_code=g.topic_code,
                    deep_link_hint=(
                        f"/subjects/{g.subject_code}/topics/{g.topic_code}"
                    ),
                    tone="positive" if pct >= 70 else "caution",
                )
            )

        # Dedupe by title+kind, keep order
        seen: set[str] = set()
        unique: list[FeedCard] = []
        for c in cards:
            key = f"{c.kind}:{c.topic_code or c.title}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(c)

        # Soft empty-state cards — kullanıcıya görünür zeka hissi (Decision değil)
        if not unique:
            unique = [
                FeedCard(
                    id="feed-soft-observe",
                    title="Seni tanımaya devam ediyoruz",
                    subtitle="Bir Pomodoro veya quiz sonrası burada kişisel öneriler görünecek",
                    kind="insight",
                    deep_link_hint="/subjects",
                    tone="neutral",
                ),
                FeedCard(
                    id="feed-soft-start",
                    title="Bugün küçük bir adım",
                    subtitle="Derslerinden bir konu seçip 25 dk çalış",
                    kind="subject",
                    deep_link_hint="/subjects",
                    tone="positive",
                ),
            ]
        return unique[:limit]

    async def home_insights(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 4,
        subject_codes: set[str] | None = None,
    ) -> list[InsightCard]:
        """Dashboard insight strip — RuleEngine top rec + confidence signals."""
        cards: list[InsightCard] = []
        try:
            from app.services.ai_insights_service import AiInsightsService

            recs = await AiInsightsService(self.db).get_recommendations(user_id)
            for rec in (recs.items or [])[:3]:
                cards.append(
                    InsightCard(
                        id=f"ai:{rec.code}",
                        code=rec.code,
                        message=rec.message,
                        tone="neutral",
                    )
                )
        except Exception:
            pass

        feed = await self.home_feed(
            user_id, limit=3, subject_codes=subject_codes
        )
        for f in feed:
            if f.kind in ("confidence", "insight") and len(cards) < limit:
                cards.append(
                    InsightCard(
                        id=f"ins:{f.id}",
                        code=f.kind,
                        message=f"{f.title}: {f.subtitle}",
                        subject_code=f.subject_code,
                        topic_code=f.topic_code,
                        topic_name=f.title,
                        tone=f.tone,
                        deep_link_hint=f.deep_link_hint,
                    )
                )
        return cards[:limit]

    # ── M15.7 ──────────────────────────────────────────────────────────────

    async def journey_trends(self, user_id: uuid.UUID) -> JourneyTrendsProjection:
        rows = (
            await self.db.scalars(
                select(TopicConfidence).where(TopicConfidence.user_id == user_id)
            )
        ).all()
        rising: list[ConfidenceTrendItem] = []
        falling: list[ConfidenceTrendItem] = []
        stable: list[ConfidenceTrendItem] = []

        for c in rows:
            topic = await self.profile_repo.get_topic_by_code(c.topic_code)
            name = topic.name if topic else c.topic_code
            if c.trend_direction > 0.15:
                trend, label = "rising", "↑ yükseliyor"
                bucket = rising
            elif c.trend_direction < -0.15:
                trend, label = "falling", "↓ düşüyor"
                bucket = falling
            else:
                trend, label = "stable", "→ dengede"
                bucket = stable
            bucket.append(
                ConfidenceTrendItem(
                    subject_code=c.subject_code,
                    topic_code=c.topic_code,
                    topic_name=name,
                    confidence_level=c.confidence_level,
                    trend=trend,
                    trend_label=label,
                    belief_pct=round(c.belief * 100, 1) if c.belief is not None else None,
                )
            )

        rising.sort(key=lambda x: -(x.belief_pct or 0))
        falling.sort(key=lambda x: (x.belief_pct or 0))
        return JourneyTrendsProjection(
            rising=rising[:10],
            falling=falling[:10],
            stable=stable[:10],
        )

    # ── helpers ────────────────────────────────────────────────────────────

    async def _get_confidence(
        self, user_id: uuid.UUID, topic_code: str
    ) -> TopicConfidence | None:
        return await self.db.scalar(
            select(TopicConfidence).where(
                TopicConfidence.user_id == user_id,
                TopicConfidence.topic_code == topic_code,
            )
        )

    def _relative(self, when: datetime) -> str:
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        now = datetime.now(UTC)
        delta = now - when
        days = delta.days
        if days <= 0:
            hours = delta.seconds // 3600
            if hours <= 0:
                return "Az önce"
            return f"{hours} saat önce"
        if days == 1:
            return "Dün"
        if days < 7:
            return f"{days} gün önce"
        if days < 14:
            return "Geçen hafta"
        weeks = days // 7
        return f"{weeks} hafta önce"
