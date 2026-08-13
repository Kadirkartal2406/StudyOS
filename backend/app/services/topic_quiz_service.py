"""
Sprint 14 — Topic Quiz Generation Service.
Sprint 25 — generation delegated to Question Intelligence Engine (QIE).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import TOPIC_QUIZ_RECENT_STEM_LIMIT, normalize_exam_code
from app.core.exceptions import AIProviderError, NotFoundError, ValidationError
from app.providers.ai.base import sanitize_ai_model
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

logger = logging.getLogger("studyos.topic_quiz")


def _resolve_item_asset_uri(it: object) -> str | None:
    """Extract asset_uri from an item, tolerating None values everywhere."""
    row_eae = getattr(it, "eae_interaction", None)
    if row_eae and isinstance(row_eae, dict):
        return row_eae.get("asset_uri")
    qie = getattr(it, "qie_card", None) or {}
    eae = qie.get("eae_interaction") or {}
    return eae.get("asset_uri") or qie.get("target_asset_id") or None


def _resolve_item_correct_node(it: object) -> str | None:
    """Extract correct_node_id from an item, tolerating None values everywhere."""
    row_eae = getattr(it, "eae_interaction", None)
    if row_eae and isinstance(row_eae, dict):
        return row_eae.get("expected_node_id")
    qie = getattr(it, "qie_card", None) or {}
    eae = qie.get("eae_interaction") or {}
    return eae.get("expected_node_id") or qie.get("correct_node_id") or None


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

        recent_stems = await self._recent_stems_for_topic(user_id, top)
        pref = await NotificationSettingsService(self.db).get_or_create(user_id)
        resolved_model = sanitize_ai_model(pref.ai_preferred_model)
        if pref.ai_preferred_model and resolved_model is None:
            logger.info(
                "topic_quiz drop placeholder preferred_model=%s user=%s",
                pref.ai_preferred_model,
                user_id,
            )
            pref.ai_preferred_model = None
            await self.db.flush()
        ctx = GenerateContext(
            exam=normalize_exam_code(exam_type or "kpss"),
            subject_code=sub,
            subject_name=sub_name,
            topic_code=top,
            topic_name=top_name,
            count=data.count,
            difficulty_band=data.difficulty or "medium",
            user_id=user_id,
            preferred_provider=pref.ai_preferred_provider,
            preferred_model=resolved_model,
            existing_stems=recent_stems,
            plans=plans,
            kind=kind,
        )
        logger.info(
            "topic_quiz new_generation generation_id=%s exam=%s subject=%s topic=%s "
            "count=%s replay=false recent_stems=%s provider=%s model=%s",
            gen.id,
            ctx.exam,
            sub,
            top,
            data.count,
            len(recent_stems),
            pref.ai_preferred_provider,
            resolved_model or "default",
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
            logger.info(
                "topic_quiz ready generation_id=%s exam=%s subject=%s topic=%s "
                "items=%s replay=false",
                gen.id,
                ctx.exam,
                sub,
                top,
                len(cards),
            )
            return await self.get(user_id, gen.id)
        except ValidationError:
            raise
        except AIProviderError as e:
            gen.status = QuizGenerationStatus.FAILED
            gen.error_message = str(e)[:400]
            await self.db.flush()
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
        logger.info(
            "topic_quiz load generation_id=%s exam=%s subject=%s topic=%s status=%s",
            gen.id,
            gen.exam_type,
            gen.subject_code,
            gen.topic_code,
            gen.status,
        )
        return self._to_read(gen)

    async def _recent_stems_for_topic(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        limit: int = TOPIC_QUIZ_RECENT_STEM_LIMIT,
    ) -> list[str]:
        """Stems recently shown to this user on this topic (READY + SUBMITTED).

        Used only as pool/author exclude_stems. Does not delete history.
        """
        if not hasattr(self.db, "execute"):
            return []
        try:
            stmt = (
                select(TopicQuizItem.stem)
                .join(
                    TopicQuizGeneration,
                    TopicQuizItem.generation_id == TopicQuizGeneration.id,
                )
                .where(
                    TopicQuizGeneration.user_id == user_id,
                    TopicQuizGeneration.topic_code == topic_code,
                    TopicQuizGeneration.status.in_(
                        (QuizGenerationStatus.READY, QuizGenerationStatus.SUBMITTED)
                    ),
                )
                .order_by(
                    TopicQuizGeneration.created_at.desc(),
                    TopicQuizItem.ord_index.asc(),
                )
                .limit(limit)
            )
            rows = (await self.db.execute(stmt)).scalars().all()
        except Exception:
            logger.exception(
                "topic_quiz recent_stems failed user=%s topic=%s",
                user_id,
                topic_code,
            )
            return []
        seen: list[str] = []
        blocked: set[str] = set()
        for raw in rows:
            stem = (raw or "").strip()
            key = stem.lower()
            if stem and key not in blocked:
                blocked.add(key)
                seen.append(stem)
        return seen

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
        node_map = {
            a.item_id: a.selected_node_id
            for a in data.answers
            if a.selected_node_id
        }

        correct = wrong = blank = 0
        for item in gen.items:
            selected = answer_map.get(item.id)
            selected_node = node_map.get(item.id)
            expected_node = None
            if item.eae_interaction:
                expected_node = item.eae_interaction.get("expected_node_id")
            elif item.qie_card and item.qie_card.get("eae_interaction"):
                expected_node = item.qie_card.get("eae_interaction", {}).get("expected_node_id")
            
            if not expected_node:
                expected_node = (item.qie_card or {}).get("correct_node_id")

            item.selected_key = selected

            # EAE node selection can grade independently of letter keys
            if selected_node and expected_node:
                item.is_correct = selected_node == expected_node
                if item.is_correct:
                    correct += 1
                else:
                    wrong += 1
                # Persist node answer into item metadata for evidence bridge
                card = dict(item.qie_card or {})
                card["selected_node_id"] = selected_node
                card["expected_node_id"] = expected_node
                if "eae_interaction" not in card:
                    card["eae_interaction"] = {}
                card["eae_interaction"]["selected_node_id"] = selected_node
                card["eae_interaction"]["expected_node_id"] = expected_node
                item.qie_card = card
            elif selected is None:
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

        # EAE misconception evidence for node-graded items
        try:
            from app.services.eae_evidence_bridge import EAEEvidenceBridge

            bridge = EAEEvidenceBridge(self.db)
            for it in gen.items:
                card = it.qie_card or {}
                selected_node = None
                expected_node = None
                
                if it.eae_interaction:
                    selected_node = card.get("eae_interaction", {}).get("selected_node_id") or card.get("selected_node_id")
                    expected_node = it.eae_interaction.get("expected_node_id")
                elif card.get("eae_interaction"):
                    eae = card.get("eae_interaction", {})
                    selected_node = eae.get("selected_node_id") or card.get("selected_node_id")
                    expected_node = eae.get("expected_node_id")
                
                if not expected_node:
                    selected_node = card.get("selected_node_id")
                    expected_node = card.get("correct_node_id")

                if not selected_node or not expected_node:
                    continue
                confusable = []
                # confusable list may live on asset nodes; pass empty → bridge still tags pair
                await bridge.ingest_node_selection(
                    user_id=user_id,
                    subject_code=gen.subject_code,
                    topic_code=gen.topic_code,
                    expected_node_id=str(expected_node),
                    selected_node_id=str(selected_node),
                    confusable_with=confusable or None,
                )
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
                target_asset_id=_resolve_item_asset_uri(it),
                correct_node_id=_resolve_item_correct_node(it),
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
                eae_interaction=getattr(it, "eae_interaction", None),
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
