"""
StudyOS — Question Generation Service (AI Sprint - FAZ 4)
LOS § 3+4 — Confidence + Evidence + Behavioral'a dayalı soru üretimi.

LOS prensibi:
  - AI rastgele soru üretmez
  - Soru kalibrasyon: Confidence.belief + difficulty_signature
  - Üretilen soru yanıtlandığında: Evidence sistemi güncellenir
  - RuleEngine / PolicyDecisionEngine DEGİSMEZ
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_question import (
    GeneratedQuestion,
    GeneratedQuestionDifficulty,
    GeneratedQuestionStatus,
)
from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.services.ai.topic_context_builder import TopicContextBuilder
from app.services.notification_settings_service import NotificationSettingsService


QuizMode = Literal["easy", "medium", "hard", "mixed", "adaptive"]


class QuizGenerateRequest(BaseModel):
    mode: QuizMode = "adaptive"  # adaptive = confidence'a göre otomatik
    count: int = 5              # Kac soru üretilsin (1-10)
    trigger: str = "on_demand"  # on_demand | policy_triggered


class QuizGenerateResponse(BaseModel):
    topic_code: str
    subject_code: str
    questions: list[GeneratedQuestionRead]
    mode_used: str
    provider: str
    generated_at: str


class GeneratedQuestionRead(BaseModel):
    id: uuid.UUID
    topic_code: str
    subject_code: str
    question_text: str
    options: dict
    difficulty: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class GeneratedQuestionAnswerRequest(BaseModel):
    user_answer: str  # A | B | C | D | E


class GeneratedQuestionAnswerResponse(BaseModel):
    is_correct: bool
    correct_option: str
    explanation: str | None = None
    evidence_updated: bool = False


class QuestionGenerationService:
    """
    LOS § 3+4 — Soru üretim servisi.

    Kullanım:
        svc = QuestionGenerationService(db)
        result = await svc.generate(user_id, subject_code, topic_code, req)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ctx_builder = TopicContextBuilder(db)
        self.notif_svc = NotificationSettingsService(db)

    async def generate(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        req: QuizGenerateRequest,
        *,
        topic_name: str | None = None,
        subject_name: str | None = None,
    ) -> QuizGenerateResponse:
        """Confidence + Evidence bazlı soru üret ve DB'ye kaydet."""
        # 1. Topic context
        ctx = await self.ctx_builder.build(
            user_id, subject_code, topic_code,
            topic_name=topic_name, subject_name=subject_name,
        )

        # 2. Mode belirleme
        mode = req.mode
        if mode == "adaptive":
            mode = ctx.quiz_difficulty  # easy | medium | hard

        count = max(1, min(req.count, 10))

        # 3. Prompt oluştur (Knowledge-first; yoksa genel fallback)
        system_prompt = self._build_system_prompt(ctx, mode)
        user_prompt = self._build_user_prompt(ctx, mode, count)

        messages = [
            ChatMessageDTO(role="system", content=system_prompt),
            ChatMessageDTO(role="user", content=user_prompt),
        ]

        # 4. LLM çağır
        pref = await self.notif_svc.get_or_create(user_id)
        provider_name = "fallback"
        raw_questions = []

        try:
            result = await generate_with_fallback(
                GenerateRequest(messages=messages, context=ctx.to_prompt_dict()),
                preferred=pref.ai_preferred_provider,
                model=pref.ai_preferred_model,
            )
            provider_name = result.provider
            raw_questions = self._parse_questions(result.text)
        except Exception:
            raw_questions = await self._get_pool_questions(ctx, count)

        if not raw_questions:
            raw_questions = await self._get_pool_questions(ctx, count)

        # Sprint 19 — Knowledge citation kaydı (Decision yok)
        if ctx.knowledge_passages:
            try:
                from app.models.knowledge import CitationUsedBy
                from app.schemas.knowledge import KnowledgePassageRead
                from app.services.knowledge_service import KnowledgeService

                passages = [
                    KnowledgePassageRead(
                        content=p.get("content") or "",
                        score=float(p.get("score") or 0),
                        source_title=p.get("source_title") or "Kaynak",
                        page_hint=p.get("page_hint"),
                        source_id=(
                            uuid.UUID(p["source_id"])
                            if p.get("source_id")
                            else None
                        ),
                        chunk_id=(
                            uuid.UUID(p["chunk_id"]) if p.get("chunk_id") else None
                        ),
                    )
                    for p in ctx.knowledge_passages[:3]
                ]
                await KnowledgeService(self.db).record_citations(
                    user_id,
                    subject_code,
                    topic_code,
                    passages,
                    used_by=CitationUsedBy.QUIZ,
                )
            except Exception:
                pass

        # 5. DB'ye kaydet
        saved: list[GeneratedQuestion] = []
        generation_ctx = {
            "confidence_level": ctx.confidence_level,
            "belief": ctx.belief,
            "sample_count": ctx.performance_sample_count,
            "mode": mode,
        }

        for q_data in raw_questions[:count]:
            q = GeneratedQuestion(
                user_id=user_id,
                subject_code=subject_code,
                topic_code=topic_code,
                question_text=q_data.get("question", ""),
                options=q_data.get("options", {}),
                correct_option=q_data.get("correct", "A"),
                explanation=q_data.get("explanation"),
                difficulty=mode if mode in ("easy", "medium", "hard") else GeneratedQuestionDifficulty.MEDIUM,
                confidence_level_at_generation=ctx.confidence_level,
                belief_at_generation=ctx.belief,
                status=GeneratedQuestionStatus.PENDING,
                generation_trigger=req.trigger,
                ai_provider=provider_name,
                generation_context=generation_ctx,
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
            self.db.add(q)
            saved.append(q)

        try:
            await self.db.flush()
        except Exception:
            pass

        return QuizGenerateResponse(
            topic_code=topic_code,
            subject_code=subject_code,
            questions=[
                GeneratedQuestionRead(
                    id=q.id,
                    topic_code=q.topic_code,
                    subject_code=q.subject_code,
                    question_text=q.question_text,
                    options=q.options,
                    difficulty=q.difficulty,
                    status=q.status,
                    created_at=q.created_at,
                )
                for q in saved
            ],
            mode_used=mode,
            provider=provider_name,
            generated_at=datetime.now(UTC).isoformat(),
        )

    async def answer_question(
        self,
        question_id: uuid.UUID,
        user_id: uuid.UUID,
        ans: GeneratedQuestionAnswerRequest,
    ) -> GeneratedQuestionAnswerResponse:
        """Soru yanıtla ve Evidence'a geri besle."""
        stmt = select(GeneratedQuestion).where(
            GeneratedQuestion.id == question_id,
            GeneratedQuestion.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        q = result.scalar_one_or_none()

        if q is None:
            return GeneratedQuestionAnswerResponse(
                is_correct=False,
                correct_option="?",
                explanation="Soru bulunamadı.",
            )

        is_correct = ans.user_answer.upper() == q.correct_option.upper()
        q.user_answer = ans.user_answer.upper()
        q.is_correct = is_correct
        q.status = GeneratedQuestionStatus.ANSWERED
        q.answered_at = datetime.now(UTC)

        evidence_updated = False
        try:
            await self.db.flush()
            # Evidence'a geri besle
            await self._feed_evidence(q, is_correct)
            evidence_updated = True
        except Exception:
            pass

        return GeneratedQuestionAnswerResponse(
            is_correct=is_correct,
            correct_option=q.correct_option,
            explanation=q.explanation,
            evidence_updated=evidence_updated,
        )

    async def list_pending(
        self,
        user_id: uuid.UUID,
        topic_code: str,
    ) -> list[GeneratedQuestion]:
        """Topic için bekleyen soruları getir."""
        stmt = (
            select(GeneratedQuestion)
            .where(
                GeneratedQuestion.user_id == user_id,
                GeneratedQuestion.topic_code == topic_code,
                GeneratedQuestion.status == GeneratedQuestionStatus.PENDING,
            )
            .order_by(GeneratedQuestion.created_at.desc())
            .limit(20)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # ── Private helpers ────────────────────────────────────────

    def _build_system_prompt(self, ctx, mode: str) -> str:
        topic_name = ctx.topic_name or ctx.topic_code
        subject_name = ctx.subject_name or ctx.subject_code
        level_desc = {
            "easy": "temel, hatırlatma odaklı, tek adımlı",
            "medium": "kavrayış gerektiren, birkaç adımlı",
            "hard": "analiz, sentez, üst düzey düşünme",
        }.get(mode, "karmaşık")

        knowledge_block = ""
        if ctx.knowledge_passages:
            lines = []
            for i, p in enumerate(ctx.knowledge_passages[:4], start=1):
                title = p.get("source_title") or "Kaynak"
                page = p.get("page_hint")
                loc = f"{title}" + (f" · {page}" if page else "")
                lines.append(f"[{i}] {loc}\n{(p.get('content') or '')[:300]}")
            knowledge_block = (
                "\nÖncelikli kaynak metinleri (bunlardan üret; uydurma):\n"
                + "\n\n".join(lines)
            )
        elif ctx.knowledge_summary:
            knowledge_block = f"\nKaynak özeti: {ctx.knowledge_summary}"

        return f"""Sen türk sınav sistemi için ({subject_name} dersi, {topic_name} konusu) soru hazırlayan bir akademisyensin.

Soru seviyesi: {mode} - {level_desc}
Öğrenci confidence: {ctx.confidence_level} (%{ctx.belief * 100:.0f} inanç)
Doğruluk geçmişi: {'%' + str(round(ctx.weighted_accuracy * 100)) if ctx.weighted_accuracy else 'Yok'}
{knowledge_block}

JSON formatında sorular üret:
[
  {{
    "question": "Soru metni",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct": "A",
    "explanation": "Neden doğru?"
  }}
]
Yalnızca JSON dön, açıklama ekleme."""

    def _build_user_prompt(self, ctx, mode: str, count: int) -> str:
        topic_name = ctx.topic_name or ctx.topic_code
        if ctx.knowledge_ready:
            return (
                f"{topic_name} konusundan, verilen kaynaklara dayalı "
                f"{count} adet {mode} seviyeli çoktan seçmeli soru üret."
            )
        return f"{topic_name} konusundan {count} adet {mode} seviyeli çoktan seçmeli soru üret."

    def _parse_questions(self, text: str) -> list[dict]:
        """LLM çıktısından JSON soru listesi parse et."""
        try:
            # JSON çıkar: [...]
            start = text.find('[')
            end = text.rfind(']') + 1
            if start == -1 or end == 0:
                return []
            return json.loads(text[start:end])
        except Exception:
            return []

    async def _get_pool_questions(self, ctx, count: int) -> list[dict]:
        """Fetch pre-generated questions from QuestionPoolCard DB table on AI error/rate limit."""
        try:
            from sqlalchemy import func, select
            from app.models.question_pool import QuestionPoolCard

            stmt = (
                select(QuestionPoolCard)
                .where(
                    QuestionPoolCard.subject_code == ctx.subject_code,
                    QuestionPoolCard.topic_code == ctx.topic_code,
                )
                .order_by(func.random())
                .limit(count)
            )
            rows = list((await self.db.execute(stmt)).scalars().all())
            if not rows:
                stmt = (
                    select(QuestionPoolCard)
                    .where(QuestionPoolCard.subject_code == ctx.subject_code)
                    .order_by(func.random())
                    .limit(count)
                )
                rows = list((await self.db.execute(stmt)).scalars().all())
            if not rows:
                stmt = (
                    select(QuestionPoolCard)
                    .order_by(func.random())
                    .limit(count)
                )
                rows = list((await self.db.execute(stmt)).scalars().all())

            if rows:
                return [
                    {
                        "question": r.stem,
                        "options": r.choices or {},
                        "correct": r.correct_key,
                        "explanation": r.explanation or f"{ctx.topic_name or ctx.topic_code} konusunun çözümü.",
                    }
                    for r in rows
                ]
        except Exception:
            pass
        return self._fallback_questions(ctx, "medium", count)

    def _fallback_questions(self, ctx, mode: str, count: int) -> list[dict]:
        """LLM başarısız olursa template soru."""
        topic_name = ctx.topic_name or ctx.topic_code
        return [
            {
                "question": f"{topic_name} konusunda hangi ifade doğrudur?",
                "options": {
                    "A": "Temel kavram doğru uygulanır",
                    "B": "Kavram yanlış uygulanır",
                    "C": "Her iki ifade de doğrucur",
                    "D": "Hiçbir ifade doğru değildir",
                },
                "correct": "A",
                "explanation": f"{topic_name} konusunun temel kavramlarını tekrar gözden geçirin.",
            }
        ] * min(count, 1)

    async def _feed_evidence(
        self, q: GeneratedQuestion, is_correct: bool
    ) -> None:
        """
        Soru yanıtlandı → Evidence sistemine geri besle.
        LOS § 3 — EvidenceSourceType.AI_QUESTION.
        Fire-and-forget.
        """
        try:
            from app.models.topic_evidence import (
                EvidenceCategory, EvidenceHorizon, EvidenceSourceType, TopicEvidence
            )

            ev = TopicEvidence(
                user_id=q.user_id,
                subject_code=q.subject_code,
                topic_code=q.topic_code,
                category=EvidenceCategory.PERFORMANCE,
                horizon=EvidenceHorizon.INSTANT,
                value=1.0 if is_correct else 0.0,
                quality_weight=0.7,  # AI soru: orta kalite (insan sorusundan az)
                source_type=EvidenceSourceType.AI_QUESTION,
                source_id=q.id,
                metadata_={
                    "question_id": str(q.id),
                    "difficulty": q.difficulty,
                    "is_correct": is_correct,
                    "ai_generated": True,
                },
                occurred_at=datetime.now(UTC),
            )
            self.db.add(ev)
            await self.db.flush()

            # Confidence Engine'i tetikle
            from app.services.confidence_engine import ConfidenceEngine
            await ConfidenceEngine(self.db).recalculate(
                q.user_id, q.subject_code, q.topic_code
            )
        except Exception:
            pass
