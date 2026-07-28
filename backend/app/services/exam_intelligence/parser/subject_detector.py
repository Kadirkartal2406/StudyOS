"""Subject / topic keyword detectors against Exam Intelligence catalog codes."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Keyword → (subject_code hint, topic slug hint, skill)
# Codes align with exam_catalog / topic_catalog conventions ({subject}__{slug}).
_SUBJECT_KEYWORDS: list[tuple[str, list[str]]] = [
    ("turkce", ["türkçe", "turkce", "paragraf", "dil bilgisi", "anlatım", "noktalama", "yazım"]),
    ("matematik", ["matematik", "problem", "denklem", "fonksiyon", "permutasyon", "olasılık", "türev", "integral"]),
    ("geometri", ["geometri", "üçgen", "ucgen", "çember", "cember", "çokgen", "katı cisim"]),
    ("fizik", ["fizik", "kuvvet", "hareket", "enerji", "elektrik", "optik", "basınç"]),
    ("kimya", ["kimya", "mol", "asit", "baz", "organik", "reaksiyon", "periyodik"]),
    ("biyoloji", ["biyoloji", "hücre", "hucre", "dna", "ekosistem", "kalıtım", "enzim"]),
    ("tarih", ["tarih", "osmanlı", "osmanli", "inkılap", "inkilap", "cumhuriyet", "selçuklu"]),
    ("cografya", ["coğrafya", "cografya", "iklim", "nüfus", "nufus", "harita", "yer şekli"]),
    ("felsefe", ["felsefe", "bilgi felsefesi", "ahlak", "varlık"]),
    ("din", ["din kültürü", "islam", "vahiy", "ahlak"]),
    ("vatandaslik", ["vatandaşlık", "vatandaslik", "anayasa", "hukuk", "demokrasi"]),
    ("edebiyat", ["edebiyat", "şiir", "siir", "roman", "divan"]),
    ("ingilizce", ["english", "vocabulary", "grammar", "reading passage", "cloze"]),
]

_TOPIC_KEYWORDS: list[tuple[str, str, list[str]]] = [
    ("turkce", "paragraf", ["paragraf", "ana düşünce", "ana fikir", "yardımcı düşünce"]),
    ("turkce", "dil_bilgisi", ["fiilimsiler", "ekler", "cümle ögeleri", "dil bilgisi"]),
    ("turkce", "yazim", ["yazım", "yazim", "büyük harf"]),
    ("turkce", "noktalama", ["noktalama", "virgül", "noktalı virgül"]),
    ("matematik", "problemler", ["problem", "işçi", "havuz", "yaş", "yüzde"]),
    ("matematik", "fonksiyonlar", ["fonksiyon", "f(x)", "bileşke"]),
    ("geometri", "ucgenler", ["üçgen", "ucgen", "açıortay", "kenarortay"]),
    ("fizik", "hareket", ["hız", "ivme", "hareket", "konum"]),
    ("kimya", "mol", ["mol", "mol kütle", "avogadro"]),
    ("biyoloji", "hucre", ["hücre", "hucre", "organel", "mitokondri"]),
    ("tarih", "osmanli", ["osmanlı", "osmanli", "padişah"]),
    ("cografya", "iklim", ["iklim", "yağış", "basınç kuşak"]),
]


@dataclass
class Detection:
    subject_code: str | None
    topic_code: str | None
    confidence: float
    skill_type: str


def _exam_prefix(exam_code: str) -> str:
    e = (exam_code or "").lower()
    if e in ("tyt", "ayt", "ydt"):
        return e
    if e == "kpss":
        return "kpss"
    if e == "lgs":
        return "lgs"
    if e in ("ales", "dgs", "ags"):
        return e
    if e in ("yds", "yokdil"):
        return e
    return e or "gen"


def detect_subject_topic(exam_code: str, transient_text: str) -> Detection:
    low = (transient_text or "").lower()
    prefix = _exam_prefix(exam_code)

    best_sub: str | None = None
    best_sub_score = 0
    for sub, kws in _SUBJECT_KEYWORDS:
        score = sum(1 for k in kws if k in low)
        if score > best_sub_score:
            best_sub_score = score
            best_sub = sub

    best_topic_slug: str | None = None
    best_topic_score = 0
    for sub, slug, kws in _TOPIC_KEYWORDS:
        if best_sub and sub != best_sub:
            continue
        score = sum(1 for k in kws if k in low)
        if score > best_topic_score:
            best_topic_score = score
            best_topic_slug = slug
            if not best_sub:
                best_sub = sub

    subject_code = f"{prefix}_{best_sub}" if best_sub else None
    topic_code = None
    conf = 0.0
    if best_sub and best_topic_slug:
        topic_code = f"{subject_code}__{best_topic_slug}"
        conf = min(0.95, 0.35 + 0.2 * best_topic_score + 0.1 * best_sub_score)
    elif best_sub:
        conf = min(0.7, 0.3 + 0.15 * best_sub_score)

    skill = "general"
    if best_topic_slug == "paragraf" or "paragraf" in low:
        skill = "inference"
    elif best_topic_slug == "problemler" or "problem" in low:
        skill = "problem_solving"
    elif best_topic_slug in ("dil_bilgisi", "yazim", "noktalama"):
        skill = "language_rules"
    elif any(x in low for x in ("passage", "reading", "cloze")):
        skill = "reading_comprehension"

    return Detection(
        subject_code=subject_code,
        topic_code=topic_code,
        confidence=round(conf, 3),
        skill_type=skill,
    )


def detect_subjects_from_pages(exam_code: str, pages: list[str]) -> list[str]:
    """Ordered unique subjects seen via section headers / keywords."""
    order: list[str] = []
    header = re.compile(
        r"(?im)^\s*(TÜRKÇE|TURKCE|MATEMATİK|MATEMATIK|GEOMETRİ|GEOMETRI|"
        r"FİZİK|FIZIK|KİMYA|KIMYA|BİYOLOJİ|BIYOLOJI|TARİH|TARIH|"
        r"COĞRAFYA|COGRAFYA|FELSEFE|İNGİLİZCE|INGILIZCE)\s*$"
    )
    mapping = {
        "türkçe": "turkce",
        "turkce": "turkce",
        "matematik": "matematik",
        "geometri": "geometri",
        "fizik": "fizik",
        "kimya": "kimya",
        "biyoloji": "biyoloji",
        "tarih": "tarih",
        "coğrafya": "cografya",
        "cografya": "cografya",
        "felsefe": "felsefe",
        "ingilizce": "ingilizce",
    }
    prefix = _exam_prefix(exam_code)
    for page in pages:
        for m in header.finditer(page or ""):
            key = m.group(1).lower().replace("İ", "i").replace("I", "i")
            # normalize turkish
            key = (
                key.replace("ı", "i")
                .replace("ğ", "g")
                .replace("ü", "u")
                .replace("ş", "s")
                .replace("ö", "o")
                .replace("ç", "c")
            )
            sub = mapping.get(key) or mapping.get(m.group(1).lower())
            if not sub:
                for k, v in mapping.items():
                    if k in m.group(1).lower():
                        sub = v
                        break
            if sub:
                code = f"{prefix}_{sub}"
                if code not in order:
                    order.append(code)
    return order
