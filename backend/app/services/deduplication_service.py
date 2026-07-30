"""
StudyOS — Strict Deduplication Service (Sprint 32)
Enforces zero duplicate questions across exams, calibrations, topic quizes, and AI generations per user.
"""

from __future__ import annotations

import hashlib
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import AssessmentQuestion, AssessmentSession
from app.models.question_record import QuestionRecord
from app.models.topic_quiz import TopicQuizGeneration, TopicQuizItem


def compute_stem_hash(stem: str | None) -> str:
    """Compute clean SHA-256 fingerprint for a question stem."""
    if not stem:
        return ""
    normalized = " ".join(stem.strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


async def get_user_seen_stem_hashes(db: AsyncSession, user_id: uuid.UUID) -> set[str]:
    """
    Fetch all stem hashes previously seen by the user across:
    1. QuestionRecord (historical solved questions)
    2. TopicQuizItem (topic quizzes)
    3. AssessmentSessionQuestion (exam sessions & calibrations)
    """
    seen: set[str] = set()

    # 1. QuestionRecord
    stmt1 = select(QuestionRecord.question_text).where(QuestionRecord.user_id == user_id)
    for text in (await db.execute(stmt1)).scalars().all():
        if text:
            seen.add(compute_stem_hash(text))

    # 2. TopicQuizItem
    stmt2 = (
        select(TopicQuizItem.stem)
        .join(TopicQuizGeneration, TopicQuizItem.generation_id == TopicQuizGeneration.id)
        .where(TopicQuizGeneration.user_id == user_id)
    )
    for text in (await db.execute(stmt2)).scalars().all():
        if text:
            seen.add(compute_stem_hash(text))

    # 3. AssessmentQuestion
    stmt3 = (
        select(AssessmentQuestion.stem)
        .join(AssessmentSession, AssessmentQuestion.session_id == AssessmentSession.id)
        .where(AssessmentSession.user_id == user_id)
    )
    for text in (await db.execute(stmt3)).scalars().all():
        if text:
            seen.add(compute_stem_hash(text))

    return seen


def filter_unseen_questions(
    items: list[dict],
    seen_hashes: set[str],
    stem_key: str = "stem",
) -> list[dict]:
    """Filter out any question dict whose stem hash is in seen_hashes."""
    unseen: list[dict] = []
    for item in items:
        text = item.get(stem_key) or item.get("question")
        h = compute_stem_hash(text)
        if h and h not in seen_hashes:
            unseen.append(item)
            seen_hashes.add(h)
    return unseen
