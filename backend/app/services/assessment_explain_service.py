"""Sprint 23 M23.7 — Wrong-answer explain for assessment items (lazy LLM)."""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.assessment import AssessmentSessionStatus
from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.repositories.assessment_repository import AssessmentRepository
from app.schemas.assessment import (
    AssessmentWrongExplainRequest,
    AssessmentWrongExplainResponse,
)
from app.services.notification_settings_service import NotificationSettingsService

_JSON_RE = re.compile(r"\{[\s\S]*\}")


class AssessmentExplainService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AssessmentRepository(db)
        self.notif = NotificationSettingsService(db)

    async def explain_wrong(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        question_id: uuid.UUID,
        body: AssessmentWrongExplainRequest | None = None,
    ) -> AssessmentWrongExplainResponse:
        session = await self.repo.get_session(session_id, user_id)
        if session is None:
            raise NotFoundError("Assessment", str(session_id))
        if session.status != AssessmentSessionStatus.SUBMITTED:
            raise ValidationError("Açıklama yalnızca gönderilmiş oturumlarda")

        aq = next((q for q in session.questions if q.id == question_id), None)
        if aq is None:
            raise NotFoundError("AssessmentQuestion", str(question_id))

        selected = (body.selected_key if body else None) or aq.selected_key
        # Only wrong / blank — correct items use generation explanation
        if aq.is_correct is True:
            raise ValidationError("Doğru cevaplar için yanlış-cevap açıklaması yok")

        cached = getattr(aq, "wrong_explain", None)
        if cached:
            parsed = _parse_cache(cached)
            if parsed:
                return AssessmentWrongExplainResponse(
                    question_id=aq.id,
                    explanation=parsed.get("explanation") or cached,
                    why_wrong=parsed.get("why_wrong"),
                    why_correct=parsed.get("why_correct"),
                    cached=True,
                    provider=parsed.get("provider") or "cache",
                )

        # Prefer stored generation explanation if rich enough and no wrong-explain yet
        if aq.explanation and len(aq.explanation.strip()) >= 40 and not selected:
            return AssessmentWrongExplainResponse(
                question_id=aq.id,
                explanation=aq.explanation,
                why_wrong=None,
                why_correct=None,
                cached=True,
                provider="generation",
            )

        choices_txt = "\n".join(
            f"{k}) {v}" for k, v in sorted((aq.choices or {}).items())
        )
        system = (
            "Sen bir sınav öğretmenisin. Öğrenciye yanlış yaptığı çoktan seçmeli "
            "soruyu kısa ve net açıkla. Karar / tavsiye verme; sadece çözüm. "
            "Türkçe yaz. JSON döndür: "
            '{"explanation":"...","why_wrong":"...","why_correct":"..."}'
        )
        user = (
            f"Sınav: {session.exam_type.upper()}\n"
            f"Soru: {aq.stem}\n"
            f"Şıklar:\n{choices_txt}\n"
            f"Doğru: {aq.correct_key}\n"
            f"Öğrenci cevabı: {selected or 'boş'}\n"
        )
        pref = await self.notif.get_or_create(user_id)
        result = await generate_with_fallback(
            GenerateRequest(
                messages=[
                    ChatMessageDTO(role="system", content=system),
                    ChatMessageDTO(role="user", content=user),
                ],
                context={"feature": "assessment_wrong_explain"},
            ),
            preferred=pref.ai_preferred_provider,
        )
        text = (result.text or "").strip()
        parsed = _parse_llm_json(text)
        explanation = (parsed.get("explanation") or text or aq.explanation or "").strip()
        why_wrong = (parsed.get("why_wrong") or None) or None
        why_correct = (parsed.get("why_correct") or None) or None
        provider = getattr(result, "provider", None) or "ai"

        cache_blob = json.dumps(
            {
                "explanation": explanation,
                "why_wrong": why_wrong,
                "why_correct": why_correct,
                "provider": provider,
                "generated_at": datetime.now(UTC).isoformat(),
            },
            ensure_ascii=False,
        )
        aq.wrong_explain = cache_blob
        await self.db.flush()

        return AssessmentWrongExplainResponse(
            question_id=aq.id,
            explanation=explanation,
            why_wrong=why_wrong,
            why_correct=why_correct,
            cached=False,
            provider=str(provider),
        )


def _parse_cache(raw: str) -> dict | None:
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("explanation"):
            return data
    except Exception:
        pass
    return None


def _parse_llm_json(text: str) -> dict:
    try:
        m = _JSON_RE.search(text)
        if not m:
            return {}
        data = json.loads(m.group(0))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
