"""Shared LLM + JSON helpers for Question Author (thin over provider)."""

from __future__ import annotations

import json
import re
from typing import Any, Awaitable, Callable

from app.providers.ai.base import (
    ChatMessageDTO,
    GenerateRequest,
    GenerateResult,
    generate_with_fallback,
)
from app.services.ai.quiz_quality_gate import extract_json_payload

LlmFn = Callable[..., Awaitable[GenerateResult]]


def _as_messages(messages: list[Any]) -> list[ChatMessageDTO]:
    out: list[ChatMessageDTO] = []
    for m in messages:
        if isinstance(m, ChatMessageDTO):
            out.append(m)
            continue
        if isinstance(m, dict):
            role = str(m.get("role") or "user")
            content = str(m.get("content") or "")
            out.append(ChatMessageDTO(role=role, content=content))
            continue
        raise TypeError(f"Unsupported message type: {type(m)!r}")
    return out


async def default_llm(
    messages: list[dict[str, str]] | list[ChatMessageDTO],
    *,
    context: dict[str, Any] | None = None,
    preferred: str | None = None,
    model: str | None = None,
) -> GenerateResult:
    return await generate_with_fallback(
        GenerateRequest(
            messages=_as_messages(list(messages)),
            context=context or {"kind": "question_author"},
        ),
        preferred=preferred,
        model=model,
    )


def parse_json_obj(text: str) -> dict[str, Any]:
    try:
        payload = extract_json_payload(text)
    except Exception:
        payload = None
    if isinstance(payload, dict):
        return payload
    m = re.search(r"\{[\s\S]*\}", text or "")
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {}


def clamp_score(value: Any, default: int = 70) -> int:
    try:
        v = int(round(float(value)))
    except (TypeError, ValueError):
        v = default
    return max(0, min(100, v))
