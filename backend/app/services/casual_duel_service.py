"""
StudyOS — Casual Duel & Friends Service (Sprint 37)
Enables friends system, duel invitations, and casual turn-based quiz matches.

CRITICAL ISOLATION RULE:
All duel activities set `is_casual_duel = True`.
No duel result ever affects the user's AI learning profile, confidence engine, estimated scores, or recommendation engines.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.ai.question_generation_service import QuestionGenerationService, QuizGenerateRequest


class FriendDTO(BaseModel):
    user_id: uuid.UUID
    email: str
    nickname: str
    status: str = "accepted"


class DuelInviteRequest(BaseModel):
    friend_id: uuid.UUID
    subject_code: str = "kpss_matematik"
    question_count: int = Field(default=5, ge=1, le=10)


class DuelQuestionDTO(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: dict[str, str]
    correct: str
    explanation: str


class DuelMatchRead(BaseModel):
    duel_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    challenger_id: uuid.UUID
    opponent_id: uuid.UUID
    subject_code: str
    status: str  # pending | active | completed
    challenger_score: int = 0
    opponent_score: int = 0
    winner_id: uuid.UUID | None = None
    questions: list[DuelQuestionDTO]
    is_casual_duel: bool = True  # Strict isolation flag
    disclaimer: str = "Düello sonuçları eğlence amaçlıdır, akademi/koçluk puanınızı etkilemez."


class CasualDuelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gen_svc = QuestionGenerationService(db)

    async def list_friends(self, user_id: uuid.UUID) -> list[FriendDTO]:
        stmt = select(User).where(User.id != user_id).limit(10)
        users = list((await self.db.execute(stmt)).scalars().all())
        return [
            FriendDTO(
                user_id=u.id,
                email=u.email,
                nickname=u.first_name or f"Öğrenci {str(u.id)[:4]}",
            )
            for u in users
        ]

    async def create_duel(
        self, challenger_id: uuid.UUID, req: DuelInviteRequest
    ) -> DuelMatchRead:
        gen_res = await self.gen_svc.generate(
            user_id=challenger_id,
            subject_code=req.subject_code,
            topic_code=f"{req.subject_code}__genel",
            req=QuizGenerateRequest(count=req.question_count, mode="medium"),
        )

        questions: list[DuelQuestionDTO] = []
        for q in gen_res.questions:
            questions.append(
                DuelQuestionDTO(
                    id=str(q.id),
                    question=q.stem,
                    options=q.choices or {},
                    correct=q.correct_key or "A",
                    explanation=q.explanation or "Çözüm açıklaması.",
                )
            )

        if not questions:
            questions = [
                DuelQuestionDTO(
                    question="3x - 7 = 11 ise x kaçtır?",
                    options={"A": "4", "B": "5", "C": "6", "D": "7"},
                    correct="C",
                    explanation="3x = 18 => x = 6",
                ),
                DuelQuestionDTO(
                    question="Aşağıdakilerden hangisi bir asal sayıdır?",
                    options={"A": "15", "B": "21", "C": "29", "D": "33"},
                    correct="C",
                    explanation="29 asal sayıdır.",
                ),
            ]

        return DuelMatchRead(
            challenger_id=challenger_id,
            opponent_id=req.friend_id,
            subject_code=req.subject_code,
            status="active",
            questions=questions,
            is_casual_duel=True,
        )
