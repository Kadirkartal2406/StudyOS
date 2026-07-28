"""
StudyOS — PromptBuilder
Sprint-2.4: standart context helpers; conversation_summary rezerv (J1, G2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.constants import AI_CONTEXT_HISTORY_MESSAGES, AI_SYSTEM_PROMPT_VERSION
from app.models.conversation import Message, MessageRole
from app.providers.ai.base import ChatMessageDTO
from app.services.ai.prompt_templates import get_system_prompt_parts, render_system_prompt


@dataclass(frozen=True)
class PromptPayload:
    messages: list[ChatMessageDTO]
    context: dict[str, Any]
    system_prompt_version: str


def _summary_goals(ctx: dict[str, Any]) -> str:
    goals = ctx.get("goals") or {}
    if not goals.get("active_count"):
        return "aktif hedef yok"
    return "aktif={count}, ortalama=%{avg}, üst={title} (%{progress})".format(
        count=goals.get("active_count"),
        avg=f"{float(goals.get('average_progress') or 0):.0f}",
        title=goals.get("top_title") or "-",
        progress=f"{float(goals.get('top_progress') or 0):.0f}",
    )


def _summary_insights(ctx: dict[str, Any]) -> str:
    insights = ctx.get("insights") or {}
    rec = insights.get("top_recommendation") or "yok"
    return "veri={ok}, öneri={rec}".format(
        ok=insights.get("has_enough_data"),
        rec=rec,
    )


def _summary_stats(ctx: dict[str, Any]) -> str:
    stats = ctx.get("statistics") or {}
    return "streak={streak}, hafta_dk={week}, pomodoro={pomo}".format(
        streak=stats.get("streak_days") or 0,
        week=stats.get("week_study_minutes") or 0,
        pomo=stats.get("total_pomodoros") or 0,
    )


def _summary_memory(ctx: dict[str, Any]) -> str:
    memory = ctx.get("memory") or {}
    if not memory.get("enabled"):
        return "bellek kapalı"
    items = memory.get("items") or []
    if not items:
        return "kayıt yok"
    snippets = [
        "{cat}:{text}".format(
            cat=item.get("category") or "?",
            text=(item.get("content") or "")[:60],
        )
        for item in items[:5]
    ]
    return "adet={n}; {joined}".format(n=len(items), joined=" | ".join(snippets))


def _summary_conversation(ctx: dict[str, Any]) -> str:
    """J1: aktif kullanılmaz; değer yoksa 'yok'."""
    value = ctx.get("conversation_summary")
    if value is None or (isinstance(value, str) and not value.strip()):
        return "yok"
    return str(value)[:400]


def _summary_topic(ctx: dict[str, Any]) -> str:
    topic_ctx = ctx.get("topic") or {}
    if not topic_ctx:
        return "konu belirtilmedi"
    topic = topic_ctx.get("topic", {})
    confidence = topic_ctx.get("confidence", {})
    evidence = topic_ctx.get("evidence", {})
    parts = []
    if topic.get("name"):
        parts.append(f"konu={topic['name']}")
    if confidence.get("level"):
        parts.append(f"güven={confidence['level']}")
    if evidence.get("sample_count"):
        parts.append(f"sample={evidence['sample_count']}")
    return "; ".join(parts) if parts else "bilgi yok"


# Standart context anahtarları — PromptBuilder / provider hazırlık (G2: system'e şişirme yok)
STANDARD_CONTEXT_KEYS: tuple[str, ...] = (
    "context_version",
    "conversation_summary",
    "topic",
    "dashboard",
    "statistics",
    "goals",
    "insights",
    "questions",
    "plans",
    "sessions",
    "activity",
    "notification_preferences",
    "widget",
    "memory",
    "resources",
    "exams",
)


class PromptBuilder:
    def build(
        self,
        *,
        context: dict[str, Any],
        history: list[Message],
        user_message: str,
        prompt_version: str | None = None,
    ) -> PromptPayload:
        version = prompt_version or AI_SYSTEM_PROMPT_VERSION
        parts = get_system_prompt_parts(version)
        values = {
            "context_version": str(context.get("context_version") or "1"),
            "prompt_version": version,
            "goals_summary": _summary_goals(context),
            "insights_summary": _summary_insights(context),
            "stats_summary": _summary_stats(context),
            "memory_summary": _summary_memory(context),
            "conversation_summary": _summary_conversation(context),
            "topic_summary": _summary_topic(context),
        }
        system_text = render_system_prompt(parts, values)

        messages: list[ChatMessageDTO] = [
            ChatMessageDTO(role=MessageRole.SYSTEM.value, content=system_text)
        ]
        recent = history[-AI_CONTEXT_HISTORY_MESSAGES:]
        for msg in recent:
            if msg.role == MessageRole.SYSTEM:
                continue
            messages.append(ChatMessageDTO(role=str(msg.role), content=msg.content))
        messages.append(ChatMessageDTO(role=MessageRole.USER.value, content=user_message))

        return PromptPayload(
            messages=messages,
            context=context,
            system_prompt_version=version,
        )
