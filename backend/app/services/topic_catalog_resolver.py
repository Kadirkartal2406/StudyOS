"""Faz 1 — read-only topic catalog resolver.

Applies the Faz 0 mapping contract without writing DB rows.

Allowed in the resolver:
  exam_catalog_alias, identity, display_name_only, ascii_rename, catalog_only.

Never in the resolver (to_topic is null / do_not_auto_migrate):
  TYT Mat 10 LP-only, YDS subject collapse, Dik Üçgen and other fold candidates.
"""

from __future__ import annotations

from app.core.config import settings

# Canonical ASCII (exam_catalog) ↔ LP Turkish-ı pair. Dual-read only.
CANONICAL_ASCII_TOPIC = "tyt_geometri__kati_cisimler"
LEGACY_ASCII_TOPIC = "tyt_geometri__katı_cisimler"
ASCII_TOPIC_READ_GROUP: frozenset[str] = frozenset(
    {CANONICAL_ASCII_TOPIC, LEGACY_ASCII_TOPIC}
)

# Faz 0 blocked FROM codes — never remap, never emit as canonical via fold.
BLOCKED_LEGACY_TOPIC_CODES: frozenset[str] = frozenset(
    {
        "tyt_matematik__sayi_basamaklari",
        "tyt_matematik__bolme_bolunebilme",
        "tyt_matematik__obeb_okek",
        "tyt_matematik__rasyonel_sayilar",
        "tyt_matematik__mutlak_deger",
        "tyt_matematik__carpanlara_ayirma",
        "tyt_matematik__kumeler",
        "tyt_matematik__polinomlar",
        "tyt_matematik__ikinci_derece",
        "tyt_matematik__permutasyon_kombinasyon",
        "tyt_geometri__dik_ucgen",
        "tyt_turkce__ses_bilgisi",
        "kpss_cografya__turkiye",
        "kpss_tarih__cumhuriyet",
        "kpss_tarih__kultur",
        "kpss_vatandaslik__temel_haklar",
        "kpss_vatandaslik__idare",
        "yds_cloze__cloze_practice",
        "yds_grammar__tenses",
        "yds_grammar__conditionals",
        "yds_grammar__relative_clauses",
        "yds_grammar__passive",
        "yds_reading__inference",
        "yds_reading__vocabulary_in_context",
        "yds_reading__paragraph_completion",
        "yds_reading__main_idea",
        "yds_reading__detail",
        "yds_translation__tr_en",
        "yds_translation__en_tr",
        "yds_vocabulary__synonyms",
        "yds_vocabulary__collocations",
        "yds_vocabulary__academic_words",
    }
)

# Suggested folds from Faz 0 — must never become resolver to_topic.
FORBIDDEN_PRODUCT_FOLDS: dict[str, str] = {
    "tyt_matematik__sayi_basamaklari": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__bolme_bolunebilme": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__obeb_okek": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__rasyonel_sayilar": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__mutlak_deger": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__carpanlara_ayirma": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__kumeler": "tyt_matematik__temel_kavramlar",
    "tyt_matematik__polinomlar": "tyt_matematik__fonksiyonlar",
    "tyt_matematik__ikinci_derece": "tyt_matematik__fonksiyonlar",
    "tyt_matematik__permutasyon_kombinasyon": "tyt_matematik__olasilik",
    "tyt_geometri__dik_ucgen": "tyt_geometri__ucgenler",
    "tyt_turkce__ses_bilgisi": "tyt_turkce__dil_bilgisi",
    "kpss_cografya__turkiye": "kpss_cografya__genel_cografya",
    "kpss_tarih__cumhuriyet": "kpss_tarih__inkilap",
    "kpss_tarih__kultur": "kpss_tarih__genel_tarih",
    "kpss_vatandaslik__temel_haklar": "kpss_vatandaslik__anayasa",
    "kpss_vatandaslik__idare": "kpss_vatandaslik__devlet_yapisi",
}

YDS_ORPHAN_SUBJECTS: frozenset[str] = frozenset(
    {
        "yds_reading",
        "yds_vocabulary",
        "yds_grammar",
        "yds_cloze",
        "yds_translation",
    }
)

YDS_SKILL_FOLD: dict[str, str] = {
    "yds_reading": "yds_ingilizce__reading",
    "yds_vocabulary": "yds_ingilizce__vocabulary",
    "yds_grammar": "yds_ingilizce__grammar",
    "yds_cloze": "yds_ingilizce__cloze_test",
    "yds_translation": "yds_ingilizce__translation",
}

_YKS_EXAMS = frozenset(
    {
        "tyt",
        "ayt",
        "ydt",
        "yks",
        "ayt_sayisal",
        "ayt_ea",
        "ayt_sozel",
        "ydt_ingilizce",
    }
)


def topic_catalog_ssot_enabled() -> bool:
    return bool(getattr(settings, "TOPIC_CATALOG_SSOT", False))


def exam_code_filter_for_list_topics(exam: str) -> str:
    """WHERE EiTopic.exam_code. Flag off keeps the raw key (legacy 404 for tyt)."""
    raw = (exam or "").strip().lower()
    if topic_catalog_ssot_enabled():
        return catalog_exam_code_for_read(raw)
    return raw


def catalog_exam_code_for_read(exam: str) -> str:
    """Map mobile/user exam to EiTopic.exam_code. Does not rewrite pool exam."""
    e = (exam or "").strip().lower()
    if e in _YKS_EXAMS:
        return "yks"
    if e in {"yds", "yds_ingilizce"}:
        return "yds"
    if e == "kpss" or e.startswith("kpss_"):
        return "kpss"
    if e.startswith("yokdil"):
        return "yokdil"
    if e.startswith("lgs"):
        return "lgs"
    if e.startswith("ales"):
        return "ales"
    if e.startswith("dgs"):
        return "dgs"
    if e in {"ags", "ags_genel"}:
        return "ags"
    return e


def topic_codes_for_dual_read(topic_code: str) -> tuple[str, ...]:
    """Expand ASCII pair for SELECT IN (...). Identity codes stay singleton."""
    code = (topic_code or "").strip()
    if not code:
        return ()
    if code in ASCII_TOPIC_READ_GROUP:
        return tuple(sorted(ASCII_TOPIC_READ_GROUP))
    return (code,)


def canonical_topic_code_for_display(topic_code: str) -> str:
    """Picker/hub emit canonical ASCII; never the Turkish-ı LP slug."""
    code = (topic_code or "").strip()
    if code in ASCII_TOPIC_READ_GROUP:
        return CANONICAL_ASCII_TOPIC
    return code


def is_blocked_legacy_topic(topic_code: str) -> bool:
    return (topic_code or "").strip() in BLOCKED_LEGACY_TOPIC_CODES


def is_yds_orphan_subject(subject_code: str) -> bool:
    return (subject_code or "").strip().lower() in YDS_ORPHAN_SUBJECTS


def resolver_to_topic(from_topic: str) -> str | None:
    """Faz 0 to_topic for resolver. None = do not remap (blocked / unknown)."""
    code = (from_topic or "").strip()
    if not code:
        return None
    if code in BLOCKED_LEGACY_TOPIC_CODES:
        return None
    if code == LEGACY_ASCII_TOPIC:
        return CANONICAL_ASCII_TOPIC
    if code in FORBIDDEN_PRODUCT_FOLDS:
        return None
    return code


def assert_no_forbidden_fold(from_topic: str, to_topic: str | None) -> None:
    """Raise if a product-decision fold leaked into the resolver."""
    expected = FORBIDDEN_PRODUCT_FOLDS.get(from_topic)
    if expected is not None and to_topic == expected:
        raise AssertionError(
            f"forbidden product fold leaked: {from_topic} → {to_topic}"
        )
    skill = YDS_SKILL_FOLD.get(from_topic.split("__", 1)[0] if from_topic else "")
    if skill and to_topic == skill:
        raise AssertionError(
            f"forbidden YDS collapse leaked: {from_topic} → {to_topic}"
        )
