"""Question intent catalogs — heuristic, exam/topic keyed (no stems)."""

from __future__ import annotations

from typing import Any


# Primary intents by topic slug / skill
_TOPIC_INTENTS: dict[str, list[str]] = {
    "paragraf": ["ana_fikir", "yardimci_fikir", "cikarim", "anlatim", "baglam"],
    "dil_bilgisi": ["dil_bilgisi", "yapı", "kural_uygulama"],
    "yazim": ["yazim", "kural_uygulama"],
    "noktalama": ["noktalama", "kural_uygulama"],
    "problemler": ["problem", "modelleme", "islem", "akil_yurutme"],
    "fonksiyonlar": ["modelleme", "islem", "akil_yurutme"],
    "ucgenler": ["sekil", "uzamsal", "ispat_yaklasimi"],
    "hareket": ["modelleme", "islem", "neden_sonuc"],
    "mol": ["islem", "modelleme"],
    "hucre": ["hatirlama", "iliski_kurma"],
    "osmanli": ["hatirlama", "neden_sonuc", "karsilastirma"],
    "iklim": ["yorumlama", "iliski_kurma"],
    "anayasa": ["hatirlama", "kural_uygulama"],
    "reading": ["cikarim", "ana_fikir", "kelime", "baglam"],
    "fen": ["yorumlama", "islem", "cikarim"],
    "genel": ["genel_anlama", "uygulama"],
}

_EXAM_DEFAULT_INTENTS: dict[str, list[str]] = {
    "kpss": ["ana_fikir", "cikarim", "anlatim", "dil_bilgisi", "hatirlama"],
    "ales": ["mantik", "iliski_kurma", "tablo_yorumlama", "cok_adimli_cikarim"],
    "tyt": ["problem", "modelleme", "islem", "akil_yurutme", "cikarim"],
    "ayt": ["derin_uygulama", "ispat_yaklasimi", "modelleme"],
    "ydt": ["reading", "cikarim", "kelime", "baglam"],
    "yds": ["reading", "cikarim", "kelime"],
    "yokdil": ["reading", "alan_kelime", "cikarim"],
    "dgs": ["problem", "mantik", "cikarim"],
    "lgs": ["temel_uygulama", "cikarim", "sekil"],
    "ags": ["anlama", "uygulama", "cikarim"],
}

_SKILL_INTENTS: dict[str, list[str]] = {
    "inference": ["cikarim", "ana_fikir", "baglam"],
    "problem_solving": ["problem", "modelleme", "islem", "akil_yurutme"],
    "reading_comprehension": ["reading", "cikarim", "kelime"],
    "language_rules": ["dil_bilgisi", "yazim", "noktalama"],
    "recall": ["hatirlama", "tanim"],
    "general": ["genel_anlama"],
}


def analyze_question_intent(
    *,
    exam_code: str,
    topic_code: str | None,
    skill_type: str | None = None,
    subject_code: str | None = None,
) -> dict[str, Any]:
    exam = (exam_code or "").lower()
    topic_slug = (topic_code or "").split("__")[-1] if topic_code else "genel"
    subject_slug = ""
    if subject_code and "_" in subject_code:
        subject_slug = subject_code.split("_", 1)[-1]
    elif topic_code and "__" in topic_code:
        left = topic_code.split("__", 1)[0]
        subject_slug = left.split("_", 1)[-1] if "_" in left else left

    intents: list[str] = []
    intents.extend(_TOPIC_INTENTS.get(topic_slug, []))
    if skill_type:
        intents.extend(_SKILL_INTENTS.get(skill_type, []))
    if subject_slug == "geometri" and "sekil" not in intents:
        intents.extend(["sekil", "uzamsal", "ispat_yaklasimi"])
    if not intents:
        intents = list(_EXAM_DEFAULT_INTENTS.get(exam, ["genel_anlama"]))

    # de-dupe preserve order
    seen: set[str] = set()
    ordered: list[str] = []
    for i in intents:
        if i not in seen:
            seen.add(i)
            ordered.append(i)

    primary = ordered[0] if ordered else "genel_anlama"
    return {
        "primary": primary,
        "intents": ordered,
        "exam_defaults": list(_EXAM_DEFAULT_INTENTS.get(exam, [])),
        "topic_slug": topic_slug,
        "subject_slug": subject_slug,
    }
