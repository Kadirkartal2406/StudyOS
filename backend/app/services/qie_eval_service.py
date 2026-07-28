"""Sprint 25 — QIE human evaluation service."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.assessment import AssessmentQuestion
from app.models.qie_eval import QieHumanEvaluation
from app.models.topic_quiz import TopicQuizItem
from app.schemas.qie_eval import (
    QieEvalCreate,
    QieEvalQueueItem,
    QieEvalRead,
)


class QieEvalService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def queue(self, *, limit: int = 20) -> list[QieEvalQueueItem]:
        limit = max(1, min(limit, 50))
        out: list[QieEvalQueueItem] = []
        rows = (
            await self.db.execute(select(AssessmentQuestion).limit(limit * 3))
        ).scalars().all()
        for q in rows:
            out.append(
                QieEvalQueueItem(
                    question_ref_type="assessment_question",
                    question_ref_id=q.id,
                    stem_preview=(q.stem or "")[:280],
                    choices=dict(q.choices or {}),
                    qie_card=dict(q.qie_card or {}),
                )
            )
            if len(out) >= limit:
                return out
        more = (
            await self.db.execute(select(TopicQuizItem).limit(limit * 2))
        ).scalars().all()
        for q in more:
            out.append(
                QieEvalQueueItem(
                    question_ref_type="topic_quiz_item",
                    question_ref_id=q.id,
                    stem_preview=(q.stem or "")[:280],
                    choices=dict(q.choices or {}),
                    qie_card=dict(q.qie_card or {}),
                )
            )
            if len(out) >= limit:
                break
        return out[:limit]

    async def create(self, user_id: uuid.UUID, body: QieEvalCreate) -> QieEvalRead:
        for field, val in (
            ("exam_feel", body.exam_feel),
            ("language", body.language),
            ("difficulty", body.difficulty),
            ("option_quality", body.option_quality),
            ("objective_fit", body.objective_fit),
            ("overall", body.overall),
        ):
            if val < 1 or val > 5:
                raise ValidationError(f"{field} 1–5 olmalı", field=field)

        stem_preview = body.stem_preview
        card_snap: dict[str, Any] = {}
        if body.question_ref_type == "assessment_question":
            q = await self.db.get(AssessmentQuestion, body.question_ref_id)
            if q is None:
                raise NotFoundError("AssessmentQuestion", str(body.question_ref_id))
            stem_preview = stem_preview or (q.stem or "")[:280]
            card_snap = dict(q.qie_card or {})
        elif body.question_ref_type == "topic_quiz_item":
            q = await self.db.get(TopicQuizItem, body.question_ref_id)
            if q is None:
                raise NotFoundError("TopicQuizItem", str(body.question_ref_id))
            stem_preview = stem_preview or (q.stem or "")[:280]
            card_snap = dict(q.qie_card or {})

        row = QieHumanEvaluation(
            rater_user_id=user_id,
            question_ref_type=body.question_ref_type,
            question_ref_id=body.question_ref_id,
            stem_preview=stem_preview,
            exam_feel=body.exam_feel,
            language=body.language,
            difficulty=body.difficulty,
            option_quality=body.option_quality,
            objective_fit=body.objective_fit,
            overall=body.overall,
            notes=body.notes,
            qie_card_snapshot=card_snap,
        )
        self.db.add(row)
        await self.db.flush()
        return QieEvalRead.model_validate(row)
