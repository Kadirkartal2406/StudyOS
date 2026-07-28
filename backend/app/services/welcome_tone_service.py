"""RC3 — Welcome tone: güvenli sabit metin (AI prompt sızıntısı yok)."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

_EXAM_SCORE_WORD: dict[str, str] = {
    "kpss": "net",
    "tyt": "net",
    "ayt": "net",
    "yks": "net",
    "lgs": "net",
    "ales": "puan",
    "yds": "puan",
    "dgs": "net",
    "ags": "net",
}

_FALLBACKS: dict[str, str] = {
    "intro": (
        "Merhaba {name}. Ben StudyOS.\n\n"
        "Sana özel plan kurmak için birkaç kısa soru soracağım.\n"
        "Başlayalım mı?"
    ),
    "exam": "Hangi sınava hazırlanıyorsun?",
    "branch": "{branch_q}",
    "education": "Şu an durumun ne?",
    "daily_time": "{exam_label} için her gün yaklaşık kaç saat ayırabilirsin?",
    "target_net": "{exam_label} için hedef {score_word}in yaklaşık kaç olsun?",
    "subject_nets": (
        "Ders ders ortalama {score_word}lerin yaklaşık kaç? "
        "Örn. Matematik 40, Türkçe 55"
    ),
    "strong": (
        "{exam_label} derslerinden hangilerinde kendini daha rahat hissediyorsun?"
    ),
    "weak": "Hangilerinde zorlanıyorsun veya geri kaldığını düşünüyorsun?",
    "studied_before": "Bu sınava daha önce düzenli çalıştın mı?",
    "habit": "Çalışma düzenin nasıl?",
    "motivation": "Seni en çok ne motive ediyor?",
    "style": "Nasıl çalışmayı tercih edersin?",
    "anything_else": "Eklemek istediğin bir şey var mı?",
    "summary": (
        "Teşekkürler {name}. Anlattıklarını not ettim.\n\n"
        "Şimdi kısa bir seviye testi yapalım; "
        "planını gerçek seviyene göre kurayım."
    ),
    "wow": "Sana özel bir çalışma sistemi kuracağız. Hazır olduğunda başlayalım.",
}


def _exam_label(exam: str | None) -> str:
    return (exam or "sınav").upper()


def _branch_question(exam: str | None) -> str:
    e = (exam or "").lower()
    if e in {"yks", "tyt", "ayt"}:
        return "YKS'de hangi alandan giriyorsun?"
    if e == "kpss":
        return "KPSS'de hangi düzeyden gireceksin?"
    return "Bu sınavda hangi alan veya düzeydesin?"


class WelcomeToneRequest(BaseModel):
    step: str = Field(..., max_length=40)
    first_name: str = Field(default="dostum", max_length=80)
    exam_hint: str | None = Field(default=None, max_length=40)
    last_answer: str | None = Field(default=None, max_length=200)


class WelcomeToneResponse(BaseModel):
    text: str
    provider: str = "fallback"
    cached_style: bool = False


class WelcomeToneService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _fallback(self, step: str, name: str, exam: str | None) -> str:
        tpl = _FALLBACKS.get(step, _FALLBACKS["intro"])
        score = _EXAM_SCORE_WORD.get((exam or "").lower(), "net")
        return tpl.format(
            name=name,
            exam_label=_exam_label(exam),
            score_word=score,
            branch_q=_branch_question(exam),
        )

    async def line(self, user_id, body: WelcomeToneRequest) -> WelcomeToneResponse:
        name = (body.first_name or "dostum").strip() or "dostum"
        step = (body.step or "intro").strip().lower()
        exam = (body.exam_hint or "").strip().lower() or None
        return WelcomeToneResponse(
            text=self._fallback(step, name, exam),
            provider="fallback",
        )
