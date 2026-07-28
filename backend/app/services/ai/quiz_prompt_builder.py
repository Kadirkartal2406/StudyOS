"""
Sprint 14 — System Prompt Builder for Topic Quiz.
Kullanıcı prompt yazmaz; Intent + Topic bağlamı yeter.
"""

from __future__ import annotations

import hashlib
import json

from app.providers.ai.base import ChatMessageDTO


def build_quiz_messages(
    *,
    subject_name: str,
    topic_name: str,
    count: int,
    difficulty: str,
    exam_type: str | None = None,
) -> tuple[list[ChatMessageDTO], str]:
    """Returns (messages, prompt_fingerprint)."""
    exam_line = f"Sınav bağlamı: {exam_type.upper()}." if exam_type else ""
    system = (
        "Sen StudyOS sınav sorusu üreticisisin. "
        "Yalnızca geçerli JSON üret. Markdown açıklama yazma. "
        "Kullanıcı prompt'u yok; verilen intent'e uy. "
        "Her soru çoktan seçmeli, tam 4 şık (A,B,C,D), tam 1 doğru cevap. "
        "Sorular verilen derse ve konuya sıkı bağlı olsun. "
        "Türkçe yaz."
    )
    schema_hint = {
        "questions": [
            {
                "stem": "soru metni",
                "choices": {"A": "...", "B": "...", "C": "...", "D": "..."},
                "correct_key": "A",
                "explanation": "kısa açıklama (opsiyonel)",
            }
        ]
    }
    user = (
        f"Ders: {subject_name}\n"
        f"Konu: {topic_name}\n"
        f"Adet: {count}\n"
        f"Zorluk: {difficulty}\n"
        f"{exam_line}\n"
        f"Çıktı şeması (örnek):\n{json.dumps(schema_hint, ensure_ascii=False)}\n"
        f"Tam {count} soru üret. Başka metin ekleme."
    )
    messages = [
        ChatMessageDTO(role="system", content=system),
        ChatMessageDTO(role="user", content=user),
    ]
    fingerprint = hashlib.sha256(
        f"{subject_name}|{topic_name}|{count}|{difficulty}|{exam_type or ''}".encode()
    ).hexdigest()[:32]
    return messages, fingerprint
