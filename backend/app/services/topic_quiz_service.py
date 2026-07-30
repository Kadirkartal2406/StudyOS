"""
Sprint 14 — Topic Quiz Generation Service.
Sprint 25 — generation delegated to Question Intelligence Engine (QIE).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.question_pool import QuestionPoolCard
from app.services.qie.types import QuestionCard, QuestionPlan

from app.core.exceptions import NotFoundError, ValidationError
from app.models.topic_quiz import (
    QuizGenerationStatus,
    TopicQuizGeneration,
    TopicQuizItem,
)
from app.repositories.learning_profile_repository import LearningProfileRepository
from app.schemas.topic_quiz import (
    QuizGenerateRequest,
    QuizGenerationRead,
    QuizItemPublic,
    QuizItemReview,
    QuizSubmitRequest,
    QuizSubmitResult,
)
from app.services.notification_settings_service import NotificationSettingsService
from app.services.qie import GenerateContext, QieOrchestrator
from app.services.qie.types import QuestionPlan


class TopicQuizService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = LearningProfileRepository(db)

    async def generate(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        data: QuizGenerateRequest,
        *,
        plans: list[QuestionPlan] | None = None,
        kind: str = "topic_quiz",
    ) -> QuizGenerationRead:
        sub = subject_code.strip()
        top = topic_code.strip()
        if not sub or not top:
            raise ValidationError("subject_code ve topic_code gerekli")

        catalog_subject = await self.profile_repo.get_catalog_by_code(sub)
        catalog_topic = await self.profile_repo.get_topic_by_code(top)
        sub_name = catalog_subject.name if catalog_subject else sub
        top_name = catalog_topic.name if catalog_topic else top

        exam_type = data.exam_type
        if not exam_type:
            from app.services.learning_profile_service import LearningProfileService

            lp = LearningProfileService(self.db)
            student = await lp.ensure_student(user_id)
            targets = await lp.repo.list_exam_targets(user_id)
            exam_type = lp.resolve_active_exam_type(student, targets)

        gen = TopicQuizGeneration(
            user_id=user_id,
            subject_code=sub,
            topic_code=top,
            subject_name=sub_name,
            topic_name=top_name,
            requested_count=data.count,
            difficulty=data.difficulty,
            exam_type=exam_type,
            status=QuizGenerationStatus.PENDING,
        )
        self.db.add(gen)
        await self.db.flush()

        pref = await NotificationSettingsService(self.db).get_or_create(user_id)
        ctx = GenerateContext(
            exam=(exam_type or "kpss").lower(),
            subject_code=sub,
            subject_name=sub_name,
            topic_code=top,
            topic_name=top_name,
            count=data.count,
            difficulty_band=data.difficulty or "medium",
            user_id=user_id,
            preferred_provider=pref.ai_preferred_provider,
            preferred_model=pref.ai_preferred_model,
            plans=plans,
            kind=kind,
        )

        try:
            cards, fingerprint, result = await QieOrchestrator(self.db).generate_batch(
                ctx
            )
            gen.prompt_fingerprint = fingerprint
            if result is not None:
                gen.provider = result.provider
                gen.model = result.model
            gen.raw_item_count = len(cards)

            from app.services.deduplication_service import get_user_seen_stem_hashes, compute_stem_hash
            seen_hashes = await get_user_seen_stem_hashes(self.db, user_id)
            if cards and seen_hashes:
                unseen = [c for c in cards if compute_stem_hash(c.stem) not in seen_hashes]
                if unseen:
                    cards = unseen

            if not cards:
                # 3-Tier Fallback: Try fetching pre-generated pool cards from QuestionPoolCard
                pool_q = (
                    select(QuestionPoolCard)
                    .where(
                        func.lower(QuestionPoolCard.exam) == (exam_type or "kpss").lower(),
                        QuestionPoolCard.topic_code == top,
                    )
                    .order_by(QuestionPoolCard.use_count.asc(), func.random())
                    .limit(data.count or 5)
                )
                pool_rows = list((await self.db.execute(pool_q)).scalars().all())

                if not pool_rows:
                    pool_q = (
                        select(QuestionPoolCard)
                        .where(
                            func.lower(QuestionPoolCard.exam) == (exam_type or "kpss").lower(),
                            QuestionPoolCard.subject_code == sub,
                        )
                        .order_by(QuestionPoolCard.use_count.asc(), func.random())
                        .limit(data.count or 5)
                    )
                    pool_rows = list((await self.db.execute(pool_q)).scalars().all())

                if not pool_rows:
                    pool_q = (
                        select(QuestionPoolCard)
                        .where(
                            func.lower(QuestionPoolCard.exam) == (exam_type or "kpss").lower(),
                        )
                        .order_by(QuestionPoolCard.use_count.asc(), func.random())
                        .limit(data.count or 5)
                    )
                    pool_rows = list((await self.db.execute(pool_q)).scalars().all())

                if pool_rows:
                    cards = [
                        QuestionCard(
                            stem=r.stem,
                            choices=r.choices or {},
                            correct_key=r.correct_key,
                            explanation=r.explanation,
                        )
                        for r in pool_rows
                    ]

            if not cards:
                gen.status = QuizGenerationStatus.FAILED
                gen.error_message = "QIE kalite kapısı: geçerli soru yok"
                await self.db.flush()
                raise ValidationError(
                    "Soru üretimi başarısız: AI sağlayıcı gerçek soru üretemedi "
                    "veya kalite kontrolünden geçemedi. Ayarlar → AI sağlayıcı "
                    "(Gemini) seçili olduğundan emin olup tekrar deneyin.",
                    field="generation",
                )

            for i, card in enumerate(cards):
                self.db.add(
                    TopicQuizItem(
                        generation_id=gen.id,
                        ord_index=i,
                        stem=card.stem,
                        choices=card.choices,
                        correct_key=card.correct_key,
                        explanation=card.explanation,
                        qie_card=card.to_persist_dict(),
                    )
                )
            gen.valid_item_count = len(cards)
            gen.status = QuizGenerationStatus.READY
            gen.error_message = None
            await self.db.flush()
            return await self.get(user_id, gen.id)
        except ValidationError:
            raise
        except Exception as e:
            gen.status = QuizGenerationStatus.FAILED
            gen.error_message = str(e)[:400]
            await self.db.flush()
            raise ValidationError(
                "Soru üretimi kalite kontrolünden geçemedi. Tekrar deneyin.",
                field="generation",
            ) from e

    async def get(self, user_id: uuid.UUID, generation_id: uuid.UUID) -> QuizGenerationRead:
        gen = await self._load(user_id, generation_id)
        return self._to_read(gen)

    async def submit(
        self,
        user_id: uuid.UUID,
        generation_id: uuid.UUID,
        data: QuizSubmitRequest,
    ) -> QuizSubmitResult:
        gen = await self._load(user_id, generation_id)
        if gen.status == QuizGenerationStatus.SUBMITTED:
            raise ValidationError("Bu quiz zaten gönderildi")
        if gen.status != QuizGenerationStatus.READY:
            raise ValidationError("Quiz çözüme hazır değil")

        answer_map = {a.item_id: a.selected_key for a in data.answers}

        correct = wrong = blank = 0
        for item in gen.items:
            selected = answer_map.get(item.id)
            item.selected_key = selected
            if selected is None:
                item.is_correct = False
                blank += 1
            elif selected == item.correct_key:
                item.is_correct = True
                correct += 1
            else:
                item.is_correct = False
                wrong += 1

        total = max(len(gen.items), 1)
        gen.correct_count = correct
        gen.wrong_count = wrong
        gen.blank_count = blank
        gen.status = QuizGenerationStatus.SUBMITTED
        gen.submitted_at = datetime.now(UTC)
        await self.db.flush()

        try:
            from app.services.evidence_service import EvidenceService

            await EvidenceService(self.db).ingest_quiz_generation(gen)
        except Exception:
            pass

        accuracy = round((correct / total) * 100, 1)
        review = [
            QuizItemReview(
                id=it.id,
                ord_index=it.ord_index,
                stem=it.stem,
                choices=dict(it.choices),
                correct_key=it.correct_key,
                explanation=it.explanation,
                selected_key=it.selected_key,
                is_correct=it.is_correct,
            )
            for it in gen.items
        ]
        return QuizSubmitResult(
            generation=self._to_read(gen),
            correct_count=correct,
            wrong_count=wrong,
            blank_count=blank,
            accuracy_pct=accuracy,
            review_items=review,
        )

    async def _load(
        self, user_id: uuid.UUID, generation_id: uuid.UUID
    ) -> TopicQuizGeneration:
        stmt = (
            select(TopicQuizGeneration)
            .where(
                TopicQuizGeneration.id == generation_id,
                TopicQuizGeneration.user_id == user_id,
            )
            .options(selectinload(TopicQuizGeneration.items))
        )
        gen = await self.db.scalar(stmt)
        if gen is None:
            raise NotFoundError("Quiz", str(generation_id))
        return gen

    def _to_read(self, gen: TopicQuizGeneration) -> QuizGenerationRead:
        items = [
            QuizItemPublic(
                id=it.id,
                ord_index=it.ord_index,
                stem=it.stem,
                choices=dict(it.choices),
            )
            for it in (gen.items or [])
        ]
        return QuizGenerationRead(
            id=gen.id,
            subject_code=gen.subject_code,
            topic_code=gen.topic_code,
            subject_name=gen.subject_name,
            topic_name=gen.topic_name,
            requested_count=gen.requested_count,
            difficulty=gen.difficulty,
            exam_type=gen.exam_type,
            status=gen.status,
            provider=gen.provider,
            valid_item_count=gen.valid_item_count,
            correct_count=gen.correct_count,
            wrong_count=gen.wrong_count,
            blank_count=gen.blank_count,
            error_message=gen.error_message,
            created_at=gen.created_at,
            items=items,
        )
