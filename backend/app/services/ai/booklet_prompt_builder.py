"""Sprint 23 — Prompt Builder v2 (style profile + blueprint driven)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.providers.ai.base import ChatMessageDTO

BOOKLET_CONTENT_VERSION = "gemini-v4-style"

BOOKLET_CHUNK_SIZE = 20
BOOKLET_CHUNK_MAX_TOKENS = 32768
BOOKLET_CHUNK_TIMEOUT_SECONDS = 180.0


def build_booklet_chunk_messages(
    *,
    exam_type: str,
    subject_name: str,
    topic_name: str,
    count: int,
    difficulty: str = "medium",
    style: dict[str, Any] | None = None,
    blueprint_hint: str | None = None,
) -> tuple[list[ChatMessageDTO], str]:
    """Style-aware official-exam prompt. Never ask to copy real questions."""
    exam = (exam_type or "").strip().upper() or "SINAV"
    style = style or {}
    choice_count = int(style.get("choice_count") or 5)
    keys = ["A", "B", "C", "D"] + (["E"] if choice_count >= 5 else [])
    choices_schema = {k: "..." for k in keys}

    schema_hint = {
        "questions": [
            {
                "stem": "Paragraf (gerekirse) + soru — tek self-contained metin",
                "choices": choices_schema,
                "correct_key": "A",
                "explanation": "kısa çözüm (1-2 cümle)",
                "skill_type": style.get("reasoning_type") or "inference",
            }
        ]
    }

    para = style.get("paragraph_words") or "80-200"
    opt = style.get("option_words") or "3-25"
    bloom = style.get("bloom") or "analyze"
    distractor = style.get("distractor_strength") or "strong"
    reading = style.get("reading_time_sec") or 75
    avoid = style.get("avoid") or []
    dtypes = style.get("distractor_types") or []
    rules = style.get("style_rules") or {}

    system = (
        f"Sen {exam} resmi sınav üreticisisin. ÖSYM/MEB tarzını TAKLİT et; "
        "mevcut soruları ASLA kopyalama veya yeniden yazma. "
        "Yalnızca geçerli JSON üret; markdown yok.\n"
        f"Style: Official {exam}\n"
        f"Paragraph length: {para} words (when reading/paragraph skill)\n"
        f"Option length: {opt} words\n"
        f"Choices: exactly {choice_count} ({', '.join(keys)})\n"
        f"Distractor: {distractor} — types: {', '.join(map(str, dtypes)) or 'plausible'}\n"
        f"Bloom: {bloom}\n"
        f"Reading time target: ~{reading} sec\n"
        f"Difficulty: {style.get('difficulty') or difficulty}\n"
        f"Language: {style.get('language_level') or 'formal_tr'}\n"
        "Rules:\n"
        "- Stem must be self-contained (no 'yukarıdaki paragraf' without text inside stem).\n"
        "- Strong distractors: one partially true, one scope trap, avoid silly wrong answers.\n"
        "- Avoid textbook/ChatGPT filler.\n"
        f"- Avoid: {'; '.join(map(str, avoid))}\n"
        f"- Extra: {json.dumps(rules, ensure_ascii=False)}\n"
        "Never copy existing questions. Generate original."
    )
    user = (
        f"Exam: {exam}\n"
        f"Subject: {subject_name}\n"
        f"Topic: {topic_name}\n"
        f"Count: {count}\n"
        f"Difficulty: {difficulty}\n"
        f"Blueprint: {blueprint_hint or style.get('reasoning_type') or 'topic coverage'}\n\n"
        f"Output schema:\n{json.dumps(schema_hint, ensure_ascii=False)}\n"
        f"Generate exactly {count} original questions."
    )
    messages = [
        ChatMessageDTO(role="system", content=system),
        ChatMessageDTO(role="user", content=user),
    ]
    fp = hashlib.sha256(
        f"booklet-v4|{exam}|{subject_name}|{topic_name}|{count}|{difficulty}|{BOOKLET_CONTENT_VERSION}".encode()
    ).hexdigest()[:32]
    return messages, fp
