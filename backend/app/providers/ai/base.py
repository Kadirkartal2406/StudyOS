"""
StudyOS — AIProvider soyutlaması
Sprint-2.2: ChatMessageDTO + generate; Null şablon.
Sprint-2.4: gerçek HTTP provider factory + B1 Null fallback.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from app.core.exceptions import AIProviderError, AIUnavailableError

logger = logging.getLogger("studyos.ai")


@dataclass
class ChatMessageDTO:
    role: str  # system | user | assistant
    content: str


@dataclass
class GenerateRequest:
    messages: list[ChatMessageDTO]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerateResult:
    text: str
    provider: str
    model: str | None = None
    used_fallback: bool = False


class AIProvider(ABC):
    """LLM adaptör sözleşmesi."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str | None:
        return None

    @abstractmethod
    async def generate(self, request: GenerateRequest) -> str:
        """Tek seferde assistant metni üretir."""
        ...

    async def stream(self, request: GenerateRequest) -> AsyncIterator[str]:
        """Streaming hazırlığı — varsayılan: tek chunk olarak generate sonucu."""
        text = await self.generate(request)
        yield text


class NullAIProvider(AIProvider):
    """Gerçek LLM yok — ContextBuilder özetinden şablon Türkçe cevap."""

    @property
    def provider_name(self) -> str:
        return "null"

    @property
    def model_name(self) -> str | None:
        return "template"

    async def generate(self, request: GenerateRequest) -> str:
        ctx = request.context or {}
        kind = str(ctx.get("kind") or "")
        # Question Author / Review must never silently use chat templates
        if kind.startswith("author_") or kind.startswith("review_"):
            raise AIUnavailableError(
                f"NullAIProvider cannot satisfy kind={kind}; configure a real AI provider"
            )
        # Sprint 14 — Quality Gate'in geçebileceği deterministik quiz JSON
        if kind == "topic_quiz":
            import json

            topic = ctx.get("topic_name") or ctx.get("topic_code") or "Konu"
            count = max(1, min(int(ctx.get("count") or 5), 15))
            questions = []
            for i in range(count):
                questions.append(
                    {
                        "stem": f"{topic} ile ilgili {i + 1}. soru: hangi ifade doğrudur?",
                        "choices": {
                            "A": f"{topic} temel kavramı doğru uygulanır",
                            "B": "Kavram yanlış uygulanır",
                            "C": "Her iki ifade de doğrudur",
                            "D": "Hiçbir ifade doğru değildir",
                        },
                        "correct_key": "A",
                        "explanation": f"{topic} konusunun temel kavramlarını gözden geçirin.",
                    }
                )
            return json.dumps({"questions": questions}, ensure_ascii=False)

        user_text = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_text = msg.content.strip()
                break

        # Chat / explain: kullanıcı mesajına bağlı, tekrarlamayan şablon
        return self._chat_style_reply(user_text=user_text, ctx=ctx)

    def _chat_style_reply(self, *, user_text: str, ctx: dict) -> str:
        goals = ctx.get("goals") or {}
        insights = ctx.get("insights") or {}
        stats = ctx.get("statistics") or {}
        topic = ctx.get("topic") or {}

        q = (user_text or "").strip()
        q_l = q.lower()

        # Doğrudan soruya cevap veren çekirdek
        if not q:
            core = (
                "Mesajını göremedim. Ne çalışmak istediğini veya hangi konuda "
                "takıldığını yaz, ona göre net bir sonraki adım veririm."
            )
        elif any(k in q_l for k in ("merhaba", "selam", "hey", "hi ")):
            core = (
                "Merhaba — StudyOS koçuyum. Bugün hangi ders/konuda ilerlemek "
                "istiyorsun? Kısa yazman yeterli (ör. «türev tekrar»)."
            )
        elif any(k in q_l for k in ("plan", "program", "nasıl çalış", "ne çalışayım")):
            core = (
                f"«{q[:120]}» için pratik öneri: 25 dk odak + 10 dk soru. "
                "Önce zayıf konundan 5 soru çöz, sonra kısa özet yaz. "
                "Plan sekmesinden «Önerilen plan» da üretebilirsin."
            )
        elif any(k in q_l for k in ("soru", "quiz", "test", "deneme")):
            core = (
                f"«{q[:120]}» için: Work Surface’te ilgili konuyu açıp Quiz üret. "
                "5 soruluk seti bitir, yanlışları Evidence’a işle, sonra aynı "
                "konuda 1 kısa anlatım iste."
            )
        elif "?" in q or any(
            k in q_l
            for k in ("nedir", "nasıl", "neden", "anlat", "açıkla", "farkı")
        ):
            topic_name = (
                topic.get("topic_name")
                or topic.get("name")
                or goals.get("top_title")
                or "bu konu"
            )
            core = (
                f"Soran: «{q[:160]}». Kısa çerçeve ({topic_name}): "
                "1) tanımı kendi cümlelerinle yaz, 2) 1 örnek çöz, "
                "3) 3 benzer soru dene. Takıldığın adımı yazarsan orayı derinleştiririm."
            )
        else:
            core = (
                f"Mesajın: «{q[:160]}». Şu anki odağın için net adım: "
                "bugün 1 pomodoro + 5 soru. Bitince sonucu (doğru/yanlış) yaz; "
                "bir sonraki seti buna göre ayarlarız."
            )

        extras: list[str] = []
        rec = insights.get("top_recommendation")
        if rec:
            extras.append(f"Sistem notu: {rec}")
        streak = stats.get("streak_days")
        if streak:
            extras.append(f"Streak: {streak} gün — koparma.")
        top_title = goals.get("top_title")
        top_progress = goals.get("top_progress")
        if top_title:
            if top_progress is not None:
                extras.append(
                    "Aktif hedef: «{title}» (%{pct}).".format(
                        title=top_title,
                        pct=f"{float(top_progress):.0f}",
                    )
                )
            else:
                extras.append(f"Aktif hedef: «{top_title}».")
        top_remaining = goals.get("top_remaining")
        eta_hint = goals.get("eta_hint")
        if top_remaining is not None and float(top_remaining) > 0 and eta_hint:
            extras.append(str(eta_hint))

        if extras:
            return core + " " + " ".join(extras)
        return core


def _normalize_name(name: str | None) -> str:
    return (name or "null").strip().lower()


def create_provider(name: str | None, model: str | None = None) -> AIProvider:
    """İsimden provider örneği; bilinmeyen → Null."""
    n = _normalize_name(name)
    if n in ("", "null", "none"):
        return NullAIProvider()
    if n == "gemini":
        from app.providers.ai.gemini_provider import GeminiProvider

        return GeminiProvider(model=model)
    if n == "openai":
        from app.providers.ai.openai_provider import OpenAIProvider

        return OpenAIProvider(model=model)
    if n == "claude":
        from app.providers.ai.claude_provider import ClaudeProvider

        return ClaudeProvider(model=model)
    return NullAIProvider()


def get_ai_provider(
    preferred: str | None = None,
    model: str | None = None,
) -> AIProvider:
    """Tercih → env AI_PROVIDER → null.

    preferred null/none/boş ise env varsayılanına düşer (string \"null\"
    env Gemini'yi ezmesin diye).
    """
    from app.core.config import settings

    pref = _normalize_name(preferred) if preferred is not None else ""
    if pref in ("", "null", "none"):
        name = settings.AI_PROVIDER or "null"
    else:
        name = preferred
    return create_provider(name, model=model or (settings.AI_MODEL or None))


async def generate_with_fallback(
    request: GenerateRequest,
    *,
    preferred: str | None = None,
    model: str | None = None,
) -> GenerateResult:
    """
    Primary generate; başarısızsa B1 → NullAIProvider.
    API key asla loglanmaz.
    M32: budget gate + cost logger; background kinds blocked when flags off.
    """
    import time

    from app.core.config import settings
    from app.core.exceptions import AIQuotaExceededError, AIUnavailableError
    from app.services.ai_cost.budget import get_daily_budget
    from app.services.ai_cost.cost_logger import AiCostEvent, estimate_cost, get_cost_logger
    from app.services.ai_cost.flags import background_ai_enabled
    from app.services.ai_cost.metrics import get_metrics

    kind = str((request.context or {}).get("kind") or "")
    # Block background / booklet auto kinds unless explicitly enabled
    if kind in (
        "daily_booklet",
        "booklet",
        "shared_booklet",
        "ai_warmup",
        "midnight_booklet",
    ) and not background_ai_enabled():
        raise AIUnavailableError(
            f"M32 background AI disabled for kind={kind}"
        )

    primary = get_ai_provider(preferred=preferred, model=model)
    # Accept dict messages from callers that don't use ChatMessageDTO yet
    normalized: list[ChatMessageDTO] = []
    for m in request.messages:
        if isinstance(m, ChatMessageDTO):
            normalized.append(m)
        elif isinstance(m, dict):
            normalized.append(
                ChatMessageDTO(
                    role=str(m.get("role") or "user"),
                    content=str(m.get("content") or ""),
                )
            )
        else:
            raise TypeError(f"Unsupported AI message type: {type(m)!r}")
    request = GenerateRequest(messages=normalized, context=request.context)

    # Budget: real providers only (null templates don't count)
    if primary.provider_name not in ("null",) and not get_daily_budget().allow_ai_call():
        get_metrics().record_budget_block()
        raise AIUnavailableError("AI daily budget exhausted — pool-only mode")

    t0 = time.perf_counter()
    try:
        text = await primary.generate(request)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        if primary.provider_name != "null":
            get_metrics().record_gemini(duration_ms)
            approx_prompt = sum(len(m.content) for m in request.messages) // 4
            approx_out = len(text or "") // 4
            get_cost_logger().record(
                AiCostEvent(
                    timestamp=__import__("datetime")
                    .datetime.now(__import__("datetime").UTC)
                    .isoformat(),
                    module="generate_with_fallback",
                    model=primary.model_name,
                    duration_ms=round(duration_ms, 2),
                    prompt_tokens=approx_prompt,
                    completion_tokens=approx_out,
                    cache_hit=False,
                    estimated_cost_usd=estimate_cost(approx_prompt, approx_out),
                    provider=primary.provider_name,
                    kind=kind or None,
                    success=True,
                )
            )
        return GenerateResult(
            text=text,
            provider=primary.provider_name,
            model=primary.model_name,
            used_fallback=False,
        )
    except AIProviderError as exc:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        get_cost_logger().record(
            AiCostEvent(
                timestamp=__import__("datetime")
                .datetime.now(__import__("datetime").UTC)
                .isoformat(),
                module="generate_with_fallback",
                model=primary.model_name,
                duration_ms=round(duration_ms, 2),
                cache_hit=False,
                provider=primary.provider_name,
                kind=kind or None,
                success=False,
                error=str(exc)[:200],
            )
        )
        if settings.DEBUG:
            logger.debug(
                "ai_fallback from=%s code=%s",
                primary.provider_name,
                exc.code,
            )
        # Author/Review pipelines must fail loudly — Null chat templates are not questions
        if kind.startswith("author_") or kind.startswith("review_") or kind in (
            "batch_generate",
            "author_compact",
        ):
            raise
        if isinstance(exc, AIQuotaExceededError) and (
            kind in ("topic_quiz", "qie", "calibration") or "quiz" in kind
        ):
            raise
        fallback_name = settings.AI_FALLBACK_PROVIDER or "null"
        if _normalize_name(fallback_name) == _normalize_name(primary.provider_name):
            fallback_name = "null"
        fallback = create_provider(fallback_name)
        text = await fallback.generate(request)
        return GenerateResult(
            text=text,
            provider=fallback.provider_name,
            model=fallback.model_name,
            used_fallback=True,
        )
