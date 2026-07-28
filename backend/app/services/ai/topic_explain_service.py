"""
StudyOS — Topic Explain Service (AI Sprint - FAZ 3)
LOS § 5 — EXPLAIN_ONLY Policy için context-aware açıklama servisi.

Bu servis Chat değildir.
Trigger'lar:
  - wrong_question: Yanlış soru çözüldü
  - low_confidence: Confidence düştü (Policy = EXPLAIN_ONLY)
  - user_request: Kullanıcı istedi

Context: TopicContextBuilder üzerinden alınır.
LLM karar vermez; açıklar.

LOS prensibi korunur:
  Explain LLM'e şunları gönderir:
    - Topic, Confidence, Evidence aggregate, Behavioral hint, Kaynaklar
  LLM yalnızca açıklama metni üretir.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.services.ai.topic_context_builder import TopicContextBuilder
from app.services.notification_settings_service import NotificationSettingsService


TriggerType = Literal["wrong_question", "low_confidence", "user_request"]


class ExplainRequest(BaseModel):
    trigger: TriggerType = "user_request"
    wrong_question_text: str | None = None   # Yanlış soru metni (opsiyonel)
    user_question: str | None = None          # Kullanıcının ek sorusu (opsiyonel)


class ExplainCitation(BaseModel):
    source_title: str | None = None
    page_hint: str | None = None
    quote: str | None = None
    relevance: float | None = None


class ExplainResponse(BaseModel):
    topic_code: str
    subject_code: str
    trigger: str
    explanation: str
    key_concepts: list[str]
    suggested_resource_url: str | None = None
    suggested_resource_title: str | None = None
    confidence_level_used: str
    provider: str
    generated_at: str
    # Sprint 19 — kaynak varsa citation zorunlu
    citations: list[ExplainCitation] = []
    used_knowledge: bool = False
    # Sprint 20 — Explain Evolution (follow-up steps)
    coach_follow_ups: list[dict] = []


class TopicExplainService:
    """
    LOS § 5 (EXPLAIN_ONLY) — Context-aware açıklama üretimi.

    Kullanım:
        svc = TopicExplainService(db)
        result = await svc.explain(user_id, subject_code, topic_code, req)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ctx_builder = TopicContextBuilder(db)
        self.notif_svc = NotificationSettingsService(db)

    async def explain(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        req: ExplainRequest,
        *,
        topic_name: str | None = None,
        subject_name: str | None = None,
    ) -> ExplainResponse:
        """
        Topic için context-aware açıklama üret.
        """
        # 1. Topic context'i al
        ctx = await self.ctx_builder.build(
            user_id,
            subject_code,
            topic_code,
            topic_name=topic_name,
            subject_name=subject_name,
        )

        # 2. Prompt oluştur
        system_prompt = self._build_system_prompt(ctx)
        user_prompt = self._build_user_prompt(ctx, req)

        messages = [
            ChatMessageDTO(role="system", content=system_prompt),
            ChatMessageDTO(role="user", content=user_prompt),
        ]

        # 3. AI provider tercihini al
        pref = await self.notif_svc.get_or_create(user_id)

        # 4. LLM çağır
        try:
            result = await generate_with_fallback(
                GenerateRequest(messages=messages, context=ctx.to_prompt_dict()),
                preferred=pref.ai_preferred_provider,
                model=pref.ai_preferred_model,
            )
            explanation_text = result.text
            provider = result.provider
        except Exception:
            explanation_text = self._fallback_explanation(ctx, req)
            provider = "fallback"

        # 5. Key concepts ve kaynak çıkar
        key_concepts = self._extract_key_concepts(ctx)
        suggested = self._suggest_resource(ctx)

        citations: list[ExplainCitation] = []
        used_knowledge = bool(ctx.knowledge_passages)
        if used_knowledge:
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
                    for p in ctx.knowledge_passages
                ]
                await KnowledgeService(self.db).record_citations(
                    user_id,
                    subject_code,
                    topic_code,
                    passages,
                    used_by=CitationUsedBy.EXPLAIN,
                )
                citations = [
                    ExplainCitation(
                        source_title=p.source_title,
                        page_hint=p.page_hint,
                        quote=(p.content[:280] if p.content else None),
                        relevance=p.score,
                    )
                    for p in passages
                ]
            except Exception:
                citations = [
                    ExplainCitation(
                        source_title=p.get("source_title"),
                        page_hint=p.get("page_hint"),
                        quote=(p.get("content") or "")[:280] or None,
                        relevance=p.get("score"),
                    )
                    for p in ctx.knowledge_passages
                ]

        coach_follow_ups: list[dict] = []
        try:
            from app.services.coach_service import CoachService

            steps = await CoachService(self.db).explain_follow_ups(
                user_id,
                subject_code,
                topic_code,
                used_knowledge=used_knowledge,
            )
            coach_follow_ups = [s.model_dump() for s in steps]
        except Exception:
            coach_follow_ups = []

        return ExplainResponse(
            topic_code=topic_code,
            subject_code=subject_code,
            trigger=req.trigger,
            explanation=explanation_text,
            key_concepts=key_concepts,
            suggested_resource_url=suggested.get("url") if suggested else None,
            suggested_resource_title=suggested.get("title") if suggested else None,
            confidence_level_used=ctx.confidence_level,
            provider=provider,
            generated_at=datetime.now(UTC).isoformat(),
            citations=citations,
            used_knowledge=used_knowledge,
            coach_follow_ups=coach_follow_ups,
        )

    def _build_system_prompt(self, ctx) -> str:
        prompt_dict = ctx.to_prompt_dict()
        topic = prompt_dict["topic"]
        confidence = prompt_dict["confidence"]
        evidence = prompt_dict["evidence"]
        behavioral = prompt_dict["behavioral"]
        exam = prompt_dict.get("exam") or {}
        knowledge = prompt_dict.get("knowledge") or {}
        exam_line = ""
        active = exam.get("active_exam_type")
        if active:
            exam_line = (
                f"\nSınav bağlamı: {str(active).upper()}. "
                f"Örnekleri ve dilini bu sınava göre ver; başka sınav formatı kullanma."
            )

        knowledge_block = ""
        passages = knowledge.get("passages") or []
        if passages:
            lines = []
            for i, p in enumerate(passages[:4], start=1):
                title = p.get("source_title") or "Kaynak"
                page = p.get("page_hint")
                loc = f"{title}" + (f" · {page}" if page else "")
                lines.append(f"[{i}] {loc}\n{(p.get('content') or '')[:350]}")
            knowledge_block = (
                "\n\nÖğrencinin kaynaklarından alıntılar (öncelikli bilgi):\n"
                + "\n\n".join(lines)
                + "\n\nAçıklamada mümkünse bu kaynaklara atıf yap "
                "(ör. 'Pegem … sayfa/bölüm …' gibi). Kaynak yokmuş gibi genel bilgi uydurma."
            )
        elif knowledge.get("summary"):
            knowledge_block = f"\n\nKaynak özeti: {knowledge['summary']}"

        return f"""Sen StudyOS öğrencisine yardımcı olan bir öğretmensin.
Konu: {topic['name']} ({topic['subject_name']}){exam_line}

Öğrenci durumu:
- Güven seviyesi: {confidence['level']} (%{confidence['belief_pct']:.0f} inanç)
- İlerleme trendi: {confidence['trend']}
- {evidence['sample_count']} ölçüm, dogruluk: %{confidence.get('belief_pct', 50):.0f}
- Toplam çalışma: {evidence['effort_minutes']:.0f} dk
{f"- Behavioral: {behavioral['hint']}" if behavioral.get('hint') else ''}
{knowledge_block}

Görevin:
1. Bu konuyu net, öz ve anlaşılır şekilde açıkla
2. Öğrencinin mevcut güven seviyesine göre derinliği ayarla
3. Somut örnekler ve mnemonik kullan
4. Yanlış yaptıysa hatayı özellikle vurgula
5. 200-400 kelime arasında tut
6. Kaynak geçtiyse citation dili kullan
Önemli: Karar verme. Yalnızca açıkla."""

    def _build_user_prompt(self, ctx, req: ExplainRequest) -> str:
        parts = []
        if req.trigger == "wrong_question" and req.wrong_question_text:
            parts.append(f"Bu soruyu yanlış yaptım: {req.wrong_question_text}")
            parts.append("Bu konuyu bana açıklar mısın?")
        elif req.user_question:
            parts.append(req.user_question)
        else:
            topic_name = ctx.topic_name or ctx.topic_code
            parts.append(f"{topic_name} konusunu açıkla.")
        return " ".join(parts)

    def _fallback_explanation(self, ctx, req: ExplainRequest) -> str:
        topic_name = ctx.topic_name or ctx.topic_code
        level = ctx.confidence_level
        if level == "low":
            return (
                f"{topic_name} konusunda henüz güven gelişmedi. "
                "Temel kavramları genişletmek için kaynakları inceleyin, "
                "ardından tekrar sorusu çözün."
            )
        return (
            f"{topic_name} konusu hakkında çalışmaya devam edin. "
            "Alıştırmalar yapmak anlayışı güçlendirir."
        )

    def _extract_key_concepts(self, ctx) -> list[str]:
        """Context'ten key concept önerileri (kural bazlı)."""
        # TODO: LLM yanıtından parse edilebilir; şimdilik basit placeholder
        return []

    def _suggest_resource(self, ctx) -> dict | None:
        """Tamamlanmamış kaynağı öner."""
        for r in ctx.resources:
            if r.get("status") in ("not_started", "in_progress"):
                return r
        return None
