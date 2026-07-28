"""
StudyOS — PromptBuilder / ContextBuilder / NullAIProvider unit tests
"""

import pytest

from app.providers.ai.base import ChatMessageDTO, GenerateRequest, NullAIProvider
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.prompt_templates import get_system_prompt_parts, render_system_prompt


def test_render_system_prompt_uses_format_map():
    parts = get_system_prompt_parts("v1")
    text = render_system_prompt(
        parts,
        {
            "context_version": "1",
            "prompt_version": "v1",
            "goals_summary": "aktif=1",
            "insights_summary": "öneri=x",
            "stats_summary": "streak=2",
            "memory_summary": "adet=1; exam:YKS",
            "conversation_summary": "yok",
        },
    )
    assert "StudyOS AI Çalışma Koçusun" in text
    assert "aktif=1" in text
    assert "streak=2" in text
    assert "YKS" in text
    assert "Sohbet özeti" in text


def test_prompt_builder_builds_system_and_user():
    payload = PromptBuilder().build(
        context={
            "context_version": "1",
            "goals": {"active_count": 0},
            "insights": {},
            "statistics": {},
        },
        history=[],
        user_message="Merhaba koç",
    )
    assert payload.messages[0].role == "system"
    assert payload.messages[-1].role == "user"
    assert payload.messages[-1].content == "Merhaba koç"


@pytest.mark.asyncio
async def test_null_provider_mentions_goal_progress():
    reply = await NullAIProvider().generate(
        GenerateRequest(
            messages=[ChatMessageDTO(role="user", content="Hedeflerim nasıl?")],
            context={
                "goals": {
                    "active_count": 1,
                    "top_title": "Haftalık 500 soru",
                    "top_progress": 64.0,
                    "top_remaining": 180.0,
                    "eta_hint": "Günde ~30 soru",
                },
                "insights": {"top_recommendation": "Ritmini koru"},
                "statistics": {"streak_days": 3},
            },
        )
    )
    assert "64" in reply
    assert "Haftalık 500 soru" in reply
