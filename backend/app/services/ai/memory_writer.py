"""
StudyOS — MemoryWriter
Sprint-2.3: AI Chat kullanıcı mesajından kural tabanlı bellek çıkarımı.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryCategory, MemorySource
from app.repositories.memory_repository import MemoryRepository

_DEFAULT_META = {"embedding_ready": False}


@dataclass(frozen=True)
class _Rule:
    category: MemoryCategory
    importance: float
    patterns: tuple[str, ...]


# Türkçe anahtar kelime kuralları — ilk eşleşen kazanır (öncelik sırası)
_RULES: tuple[_Rule, ...] = (
    _Rule(
        MemoryCategory.EXAM,
        0.85,
        (r"\bysk\b", r"\btayt\b", r"\bayt\b", r"sınav", r"deneme", r"yks"),
    ),
    _Rule(
        MemoryCategory.WEAK_SUBJECT,
        0.8,
        (r"zayıf", r"anlamıyorum", r"zorlanıyorum", r"başaramıyorum", r"kötüyüm"),
    ),
    _Rule(
        MemoryCategory.STRONG_SUBJECT,
        0.7,
        (r"güçlü", r"iyi yapıyorum", r"kolay geliyor", r"başarılıyım"),
    ),
    _Rule(
        MemoryCategory.GOAL,
        0.75,
        (r"hedef", r"amacım", r"kazanmak istiyorum", r"net yapmak"),
    ),
    _Rule(
        MemoryCategory.SCHEDULE,
        0.65,
        (r"her gün", r"her hafta", r"sabah", r"akşam", r"program", r"saat"),
    ),
    _Rule(
        MemoryCategory.STUDY_HABIT,
        0.7,
        (r"alışkanlık", r"pomodoro", r"odaklan", r"erteleme", r"düzenli çalış"),
    ),
    _Rule(
        MemoryCategory.PREFERENCE,
        0.6,
        (r"tercih", r"sevmiyorum", r"seviyorum", r"tercihim", r"istemiyorum"),
    ),
    _Rule(
        MemoryCategory.MOTIVATION,
        0.55,
        (r"motive", r"motivasyon", r"yorgunum", r"vazgeç", r"moral"),
    ),
)


class MemoryWriter:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MemoryRepository(db)

    def _match(self, text: str) -> _Rule | None:
        lowered = text.casefold()
        for rule in _RULES:
            for pat in rule.patterns:
                if re.search(pat, lowered, flags=re.IGNORECASE):
                    return rule
        return None

    async def extract_from_chat(
        self,
        user_id: uuid.UUID,
        message: str,
        *,
        conversation_id: uuid.UUID | None = None,
    ) -> Memory | None:
        text = message.strip()
        if len(text) < 8:
            return None

        rule = self._match(text)
        if rule is None:
            # Genel konuşma belleği — daha düşük importance
            if len(text) < 40:
                return None
            category = MemoryCategory.CONVERSATION
            importance = 0.4
        else:
            category = rule.category
            importance = rule.importance

        # İçeriği kısalt / normalize
        content = text[:500]
        existing = await self.repo.find_similar_active(user_id, category, content)
        if existing is not None:
            existing.importance = max(float(existing.importance), importance)
            await self.db.flush()
            return existing

        meta = dict(_DEFAULT_META)
        if conversation_id is not None:
            meta["conversation_id"] = str(conversation_id)

        mem = Memory(
            user_id=user_id,
            category=category,
            importance=importance,
            content=content,
            source=MemorySource.AI_CHAT,
            metadata_=meta,
            is_active=True,
        )
        return await self.repo.add(mem)
