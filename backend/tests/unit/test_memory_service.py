"""
StudyOS — MemoryWriter / MemoryRetriever unit tests
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryCategory, MemorySource
from app.models.user import User, UserRole, UserStatus
from app.schemas.memory import MemoryCreate
from app.services.ai.memory_retriever import MemoryRetriever
from app.services.ai.memory_writer import MemoryWriter
from app.services.ai.prompt_builder import PromptBuilder
from app.services.memory_service import MemoryService


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Mem",
        last_name="Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_memory_writer_extracts_exam(db_session: AsyncSession):
    user = await _user(db_session, "mem.writer@studyos.dev")
    writer = MemoryWriter(db_session)
    mem = await writer.extract_from_chat(
        user.id, "YKS sınavına hazırlanıyorum, deneme çözüyorum"
    )
    assert mem is not None
    assert mem.category == MemoryCategory.EXAM
    assert mem.source == MemorySource.AI_CHAT
    assert mem.metadata_.get("embedding_ready") is False


@pytest.mark.asyncio
async def test_memory_writer_skips_short(db_session: AsyncSession):
    user = await _user(db_session, "mem.short@studyos.dev")
    mem = await MemoryWriter(db_session).extract_from_chat(user.id, "Merhaba")
    assert mem is None


@pytest.mark.asyncio
async def test_memory_retriever_orders_and_touches(db_session: AsyncSession):
    user = await _user(db_session, "mem.ret@studyos.dev")
    svc = MemoryService(db_session)
    await svc.create_memory(
        user.id,
        MemoryCreate(
            category=MemoryCategory.GOAL,
            content="Haftalık 300 soru hedefim var",
            importance=0.9,
        ),
    )
    await svc.create_memory(
        user.id,
        MemoryCreate(
            category=MemoryCategory.CUSTOM,
            content="Düşük önem notu",
            importance=0.2,
        ),
    )
    items = await MemoryRetriever(db_session).retrieve_for_context(user.id)
    assert len(items) >= 2
    assert items[0].importance >= items[1].importance
    assert items[0].access_count >= 1


def test_prompt_builder_includes_memory_summary():
    payload = PromptBuilder().build(
        context={
            "context_version": "1",
            "goals": {"active_count": 0},
            "insights": {},
            "statistics": {},
            "memory": {
                "enabled": True,
                "items": [
                    {
                        "category": "weak_subject",
                        "content": "Matematikte zorlanıyorum",
                    }
                ],
            },
        },
        history=[],
        user_message="Ne çalışayım?",
    )
    system = payload.messages[0].content
    assert "weak_subject" in system
    assert "Matematik" in system
