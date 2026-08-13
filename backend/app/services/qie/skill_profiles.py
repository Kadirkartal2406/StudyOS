"""Domain-aware skill / stem profiles for QuestionPlanner.

Priority: topic-specific → subject/domain → controlled generic.
Generic fallback must NEVER be the Turkish language skill cycle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Language-only cycle (Türkçe / dil bilgisi). Must not leak to other domains.
LANGUAGE_SKILLS: tuple[str, ...] = (
    "vocabulary",
    "sentence_meaning",
    "main_idea",
    "supporting_idea",
    "paragraph_completion",
    "sentence_ordering",
    "coherence",
    "grammar",
    "spelling",
    "punctuation",
    "logic",
    "mixed_reasoning",
)

LANGUAGE_STEMS: tuple[str, ...] = (
    "inference",
    "main_idea",
    "supporting_detail",
    "comparison",
    "sentence_ordering",
    "paragraph_completion",
    "vocabulary",
    "grammar",
    "cause_effect",
    "tone",
)

# Skills that are language-form focused (must not appear outside language domains).
LANGUAGE_FORM_SKILLS: frozenset[str] = frozenset(
    {
        "vocabulary",
        "sentence_meaning",
        "main_idea",
        "supporting_idea",
        "paragraph_completion",
        "sentence_ordering",
        "coherence",
        "grammar",
        "spelling",
        "punctuation",
    }
)

# Safe fallback when domain cannot be resolved — not Türkçe.
GENERIC_SKILLS: tuple[str, ...] = (
    "problem_solving",
    "logical_reasoning",
    "analysis",
    "application",
    "comparison",
    "inference",
)

GENERIC_STEMS: tuple[str, ...] = (
    "problem_solving",
    "application",
    "inference",
    "comparison",
    "cause_effect",
    "analysis",
)


@dataclass(frozen=True)
class SkillProfile:
    domain: str
    skills: tuple[str, ...]
    stem_types: tuple[str, ...]
    allows_language_dna: bool = False


_PROFILES: dict[str, SkillProfile] = {
    "turkce": SkillProfile(
        domain="turkce",
        skills=LANGUAGE_SKILLS,
        stem_types=LANGUAGE_STEMS,
        allows_language_dna=True,
    ),
    "edebiyat": SkillProfile(
        domain="edebiyat",
        skills=(
            "literary_analysis",
            "main_idea",
            "supporting_idea",
            "vocabulary",
            "tone",
            "period_style",
            "genre_recognition",
            "poetry_analysis",
            "mixed_reasoning",
        ),
        stem_types=(
            "literary_analysis",
            "main_idea",
            "supporting_detail",
            "vocabulary",
            "tone",
            "comparison",
            "inference",
        ),
        allows_language_dna=True,
    ),
    "matematik": SkillProfile(
        domain="matematik",
        skills=(
            "arithmetic",
            "algebra",
            "equations",
            "inequalities",
            "functions",
            "problem_solving",
            "geometry_application",
            "probability",
            "calculus",
            "number_theory",
        ),
        stem_types=(
            "calculation",
            "equation_solving",
            "problem_solving",
            "interpretation",
            "application",
            "multi_step",
        ),
    ),
    "geometri": SkillProfile(
        domain="geometri",
        skills=(
            "angles",
            "triangles",
            "quadrilaterals",
            "circles",
            "analytic_geometry",
            "area_volume",
            "similarity",
            "solid_geometry",
            "problem_solving",
        ),
        stem_types=(
            "calculation",
            "spatial_reasoning",
            "theorem_application",
            "problem_solving",
            "interpretation",
        ),
    ),
    "fizik": SkillProfile(
        domain="fizik",
        skills=(
            "mechanics",
            "energy",
            "electricity",
            "optics",
            "waves",
            "thermodynamics",
            "modern_physics",
            "problem_solving",
        ),
        stem_types=(
            "calculation",
            "concept_application",
            "problem_solving",
            "interpretation",
            "cause_effect",
        ),
    ),
    "kimya": SkillProfile(
        domain="kimya",
        skills=(
            "atom",
            "periodic_system",
            "bonds",
            "reactions",
            "stoichiometry",
            "solutions",
            "organic",
            "problem_solving",
        ),
        stem_types=(
            "calculation",
            "concept_application",
            "problem_solving",
            "interpretation",
            "cause_effect",
        ),
    ),
    "biyoloji": SkillProfile(
        domain="biyoloji",
        skills=(
            "cell",
            "genetics",
            "systems",
            "ecology",
            "evolution",
            "physiology",
            "classification",
            "concept_application",
        ),
        stem_types=(
            "concept_application",
            "interpretation",
            "cause_effect",
            "comparison",
            "inference",
        ),
    ),
    "fen": SkillProfile(
        domain="fen",
        skills=(
            "mechanics",
            "energy",
            "matter",
            "cell",
            "ecology",
            "earth_science",
            "problem_solving",
            "concept_application",
        ),
        stem_types=(
            "concept_application",
            "problem_solving",
            "interpretation",
            "cause_effect",
            "calculation",
        ),
    ),
    "tarih": SkillProfile(
        domain="tarih",
        skills=(
            "chronology",
            "cause_effect",
            "political_developments",
            "wars_treaties",
            "reforms",
            "ottoman_history",
            "republic_history",
            "cultural_history",
            "concept_recall",
        ),
        stem_types=(
            "factual_recall",
            "chronology",
            "cause_effect",
            "interpretation",
            "comparison",
            "inference",
        ),
    ),
    "cografya": SkillProfile(
        domain="cografya",
        skills=(
            "physical_geography",
            "climate",
            "population",
            "settlement",
            "economy_geography",
            "maps",
            "regions",
            "turkey_geography",
            "human_geography",
        ),
        stem_types=(
            "factual_recall",
            "map_data",
            "interpretation",
            "cause_effect",
            "comparison",
            "inference",
        ),
    ),
    "felsefe": SkillProfile(
        domain="felsefe",
        skills=(
            "concepts",
            "philosophers",
            "schools",
            "arguments",
            "epistemology",
            "ethics",
            "ontology",
            "critical_reasoning",
        ),
        stem_types=(
            "concept_application",
            "interpretation",
            "comparison",
            "argument_analysis",
            "inference",
        ),
    ),
    "din": SkillProfile(
        domain="din",
        skills=(
            "concepts",
            "interpretation",
            "islamic_history",
            "values",
            "worship",
            "ethics",
            "scripture_knowledge",
        ),
        stem_types=(
            "factual_recall",
            "interpretation",
            "concept_application",
            "comparison",
            "inference",
        ),
    ),
    "vatandaslik": SkillProfile(
        domain="vatandaslik",
        skills=(
            "constitution",
            "rights_duties",
            "state_structure",
            "democracy",
            "law_basics",
            "public_administration",
            "concept_recall",
        ),
        stem_types=(
            "factual_recall",
            "concept_application",
            "interpretation",
            "comparison",
            "inference",
        ),
    ),
    "guncel": SkillProfile(
        domain="guncel",
        skills=(
            "current_affairs",
            "institutions",
            "international_relations",
            "economy_affairs",
            "science_tech_affairs",
            "concept_recall",
        ),
        stem_types=(
            "factual_recall",
            "interpretation",
            "comparison",
            "cause_effect",
            "inference",
        ),
    ),
    "english": SkillProfile(
        domain="english",
        skills=(
            "vocabulary",
            "grammar",
            "reading",
            "cloze",
            "translation",
            "sentence_completion",
            "dialogue",
            "restatement",
        ),
        stem_types=(
            "vocabulary",
            "grammar",
            "reading_comprehension",
            "cloze",
            "sentence_completion",
            "translation",
            "inference",
        ),
        allows_language_dna=True,
    ),
    "quantitative": SkillProfile(
        domain="quantitative",
        skills=(
            "quantitative_reasoning",
            "arithmetic",
            "algebra",
            "problem_solving",
            "data_interpretation",
            "logical_reasoning",
            "geometry_application",
        ),
        stem_types=(
            "calculation",
            "problem_solving",
            "data_interpretation",
            "logical_reasoning",
            "multi_step",
            "application",
        ),
    ),
    "verbal_reasoning": SkillProfile(
        domain="verbal_reasoning",
        skills=(
            "logical_reasoning",
            "sentence_meaning",
            "main_idea",
            "comparison",
            "inference",
            "argument_analysis",
            "mixed_reasoning",
        ),
        stem_types=(
            "inference",
            "main_idea",
            "comparison",
            "logical_reasoning",
            "argument_analysis",
            "sentence_meaning",
        ),
    ),
    "unknown": SkillProfile(
        domain="unknown",
        skills=GENERIC_SKILLS,
        stem_types=GENERIC_STEMS,
    ),
}

# Topic slug / name keywords → domain or skill-subset override.
# Checked before subject-level domain when match is strong.
_TOPIC_DOMAIN_HINTS: list[tuple[tuple[str, ...], str]] = [
    (("paragraf", "anlam", "okuma", "reading", "passage", "metin", "clozer"), "turkce"),
    (("yazim", "yazım", "noktalama", "dil_bilgisi", "dilbilgisi"), "turkce"),
    (("ucgen", "üçgen", "cember", "çember", "aci", "açı", "analitik"), "geometri"),
    (("turev", "türev", "integral", "limit", "fonksiyon", "denklem", "olusallik", "olasılık"), "matematik"),
    (("osmanli", "osmanlı", "cumhuriyet", "inkilap", "inkılap", "selcuklu"), "tarih"),
    (("nufus", "nüfus", "iklim", "harita", "yerlesme", "yerleşme", "bolge", "bölge"), "cografya"),
    (("hucre", "hücre", "dna", "genetik", "ekosistem"), "biyoloji"),
    (("hareket", "elektrik", "optik", "kuvvet", "enerji"), "fizik"),
    (("mol", "asit", "baz", "organik", "periyodik"), "kimya"),
]

_SUBJECT_ALIASES: dict[str, str] = {
    "turkce": "turkce",
    "edebiyat": "edebiyat",
    "matematik": "matematik",
    "geometri": "geometri",
    "fizik": "fizik",
    "kimya": "kimya",
    "biyoloji": "biyoloji",
    "fen": "fen",
    "tarih": "tarih",
    "cografya": "cografya",
    "felsefe": "felsefe",
    "din": "din",
    "vatandaslik": "vatandaslik",
    "guncel": "guncel",
    "ingilizce": "english",
    "english": "english",
    "sayisal": "quantitative",
    "sozel": "verbal_reasoning",
    "inkilap": "tarih",
}


def _normalize(text: str | None) -> str:
    s = (text or "").strip().lower()
    return (
        s.replace("ı", "i")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ş", "s")
        .replace("ö", "o")
        .replace("ç", "c")
    )


def _subject_leaf(subject_code: str | None) -> str:
    code = _normalize(subject_code)
    if not code:
        return ""
    for prefix in (
        "kpss_",
        "tyt_",
        "ayt_",
        "lgs_",
        "ags_",
        "ydt_",
        "yds_",
        "yokdil_",
        "ales_",
        "dgs_",
    ):
        if code.startswith(prefix):
            code = code[len(prefix) :]
            break
    # ayt_tarih_1 → tarih, cografya_2 → cografya
    code = re.sub(r"_\d+$", "", code)
    return code


def _topic_slug(topic_code: str | None) -> str:
    code = _normalize(topic_code)
    if "__" in code:
        return code.split("__", 1)[1]
    return code


def resolve_topic_domain(
    *,
    topic_code: str | None,
    topic_name: str | None,
) -> str | None:
    """Topic-specific domain when topic clearly implies a skill family."""
    blob = f"{_topic_slug(topic_code)} {_normalize(topic_name)}"
    if not blob.strip():
        return None
    for keys, domain in _TOPIC_DOMAIN_HINTS:
        if any(k in blob for k in keys):
            return domain
    return None


def resolve_domain(
    *,
    exam: str | None = None,
    subject_code: str | None = None,
    subject_name: str | None = None,
    topic_code: str | None = None,
    topic_name: str | None = None,
) -> str:
    """Resolve planner domain. Topic hint can refine but subject wins for cross-domain topics."""
    exam_n = _normalize(exam)
    leaf = _subject_leaf(subject_code)
    name = _normalize(subject_name)

    # Explicit English exams
    if exam_n in {"yds", "ydt", "yokdil", "yds_ingilizce", "ydt_ingilizce"} or leaf in {
        "ingilizce",
        "english",
    }:
        return "english"
    if "ingilizce" in name or "english" in name:
        return "english"

    # ALES/DGS branch subjects are themselves domain codes
    if leaf in _SUBJECT_ALIASES:
        domain = _SUBJECT_ALIASES[leaf]
    elif leaf:
        # Unknown leaf → try name keywords, else unknown
        domain = "unknown"
        for key, mapped in _SUBJECT_ALIASES.items():
            if key in name or key in leaf:
                domain = mapped
                break
    else:
        domain = "unknown"
        for key, mapped in _SUBJECT_ALIASES.items():
            if key in name:
                domain = mapped
                break

    # Topic-specific override only when it matches / refines same family,
    # or when subject domain is unknown.
    topic_domain = resolve_topic_domain(topic_code=topic_code, topic_name=topic_name)
    if topic_domain:
        if domain == "unknown":
            return topic_domain
        # Allow turkce topic refinement only for language subjects
        if topic_domain == domain:
            return domain
        # Geometry topic under matematik subject → geometri skills
        if domain == "matematik" and topic_domain == "geometri":
            return "geometri"
        # Reading/language topic under turkce → turkce
        if domain == "turkce" and topic_domain == "turkce":
            return "turkce"

    return domain if domain in _PROFILES else "unknown"


def get_skill_profile(
    *,
    exam: str | None = None,
    subject_code: str | None = None,
    subject_name: str | None = None,
    topic_code: str | None = None,
    topic_name: str | None = None,
) -> SkillProfile:
    domain = resolve_domain(
        exam=exam,
        subject_code=subject_code,
        subject_name=subject_name,
        topic_code=topic_code,
        topic_name=topic_name,
    )
    return _PROFILES.get(domain, _PROFILES["unknown"])


# Topic slug/name → preferred skill(s) within the resolved domain profile.
_TOPIC_SKILL_BOOSTS: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (("nufus", "nüfus", "population"), ("population", "human_geography", "settlement")),
    (("iklim", "climate"), ("climate", "physical_geography")),
    (("harita", "map"), ("maps", "regions")),
    (("osmanli", "osmanlı"), ("ottoman_history", "chronology", "reforms")),
    (("cumhuriyet",), ("republic_history", "reforms", "political_developments")),
    (("paragraf", "anlam", "okuma", "reading", "passage"), ("main_idea", "supporting_idea", "paragraph_completion")),
    (("yazim", "yazım", "spelling"), ("spelling",)),
    (("noktalama",), ("punctuation",)),
    (("dil_bilgisi", "dilbilgisi", "grammar"), ("grammar",)),
    (("fonksiyon",), ("functions", "algebra")),
    (("denklem",), ("equations", "algebra")),
    (("ucgen", "üçgen"), ("triangles", "angles")),
    (("cember", "çember"), ("circles",)),
    (("turev", "türev", "integral", "limit"), ("calculus", "functions")),
    (("hucre", "hücre"), ("cell",)),
    (("genetik", "dna"), ("genetics",)),
    (("hareket",), ("mechanics",)),
    (("elektrik",), ("electricity",)),
    (("vocabulary", "kelime"), ("vocabulary",)),
    (("cloze",), ("cloze", "grammar")),
]


def _boost_topic_skills(
    skills: list[str],
    *,
    topic_code: str | None,
    topic_name: str | None,
) -> list[str]:
    blob = f"{_topic_slug(topic_code)} {_normalize(topic_name)}"
    if not blob.strip():
        return skills
    preferred: list[str] = []
    for keys, boosts in _TOPIC_SKILL_BOOSTS:
        if any(k in blob for k in keys):
            for s in boosts:
                if s in skills and s not in preferred:
                    preferred.append(s)
    if not preferred:
        return skills
    rest = [s for s in skills if s not in preferred]
    return preferred + rest


def skill_pool_for_context(
    profile: SkillProfile,
    style: dict | None = None,
    *,
    topic_code: str | None = None,
    topic_name: str | None = None,
) -> list[str]:
    """Build ordered skill pool. DNA skill_distribution only for language domains."""
    style = style or {}
    base = list(profile.skills)
    if profile.allows_language_dna:
        dist = style.get("skill_distribution") or {}
        if isinstance(dist, dict) and dist:
            allowed = set(profile.skills)
            dna_keys = [k for k in dist.keys() if k in allowed]
            if dna_keys:
                extras = [s for s in base if s not in dna_keys]
                base = dna_keys + extras
    return _boost_topic_skills(base, topic_code=topic_code, topic_name=topic_name)


def stem_cycle_for_profile(profile: SkillProfile) -> list[str]:
    return list(profile.stem_types)


def is_language_form_skill(skill: str) -> bool:
    return skill in LANGUAGE_FORM_SKILLS


LANGUAGE_DOMAINS: frozenset[str] = frozenset({"turkce", "edebiyat", "english"})

# Language-only stem types that must not appear on non-language pool cards.
LANGUAGE_FORM_STEMS: frozenset[str] = frozenset(
    {
        "vocabulary",
        "grammar",
        "main_idea",
        "supporting_detail",
        "paragraph_completion",
        "sentence_ordering",
        "tone",
        "cloze",
        "reading_comprehension",
        "literary_analysis",
    }
)


def pool_card_compatible(
    *,
    exam: str | None,
    subject_code: str | None,
    topic_code: str | None = None,
    topic_name: str | None = None,
    skill: str | None = None,
    stem_type: str | None = None,
) -> bool:
    """True if a pool card's skill/stem may be served for this subject/topic.

    Language domains (Türkçe / Edebiyat / English) keep their form skills.
    Verbal reasoning may use meaning skills (main_idea, sentence_meaning)
    but never spelling/grammar/vocabulary leftovers.
    All other domains reject language-form skills and stems.
    """
    profile = get_skill_profile(
        exam=exam,
        subject_code=subject_code,
        subject_name=None,
        topic_code=topic_code,
        topic_name=topic_name,
    )
    skill_s = (skill or "").strip()
    stem_s = (stem_type or "").strip()
    if profile.domain in LANGUAGE_DOMAINS:
        return True
    if profile.domain == "verbal_reasoning":
        if skill_s in LANGUAGE_FORM_SKILLS and skill_s not in profile.skills:
            return False
        if stem_s in LANGUAGE_FORM_STEMS and stem_s not in profile.stem_types:
            return False
        if skill_s and skill_s not in profile.skills and skill_s in LANGUAGE_SKILLS:
            return False
        return True
    if skill_s in LANGUAGE_FORM_SKILLS:
        return False
    if stem_s in LANGUAGE_FORM_STEMS:
        return False
    if skill_s and skill_s not in profile.skills and skill_s in LANGUAGE_SKILLS:
        return False
    return True


def pool_row_compatible(
    row: Any,
    *,
    exam: str | None = None,
    subject_code: str | None = None,
    topic_code: str | None = None,
    topic_name: str | None = None,
) -> bool:
    qie = getattr(row, "qie_card", None) or {}
    skill = ""
    stem_type = ""
    if isinstance(qie, dict):
        skill = str(qie.get("skill") or "")
        stem_type = str(qie.get("stem_type") or "")
    skill = skill or str(getattr(row, "skill", None) or "")
    return pool_card_compatible(
        exam=exam or getattr(row, "exam", None),
        subject_code=subject_code or getattr(row, "subject_code", None),
        topic_code=topic_code or getattr(row, "topic_code", None),
        topic_name=topic_name,
        skill=skill,
        stem_type=stem_type,
    )


# Stem types that naturally need a long passage. Do not shorten these.
LONG_STEM_TYPES: frozenset[str] = frozenset(
    {
        "reading_comprehension",
        "paragraph_completion",
        "sentence_ordering",
        "main_idea",
        "supporting_detail",
        "cloze",
        "literary_analysis",
        "paragraph_analysis",
    }
)

# Stem types that should stay short/medium (knowledge / calculation).
SHORT_STEM_TYPES: frozenset[str] = frozenset(
    {
        "factual_recall",
        "calculation",
        "equation_solving",
        "application",
        "concept_application",
        "chronology",
        "theorem_application",
        "multi_step",
        "map_data",
    }
)

_DOMAIN_INSTRUCTIONS: dict[str, str] = {
    "tarih": (
        "Bu soru tarih alanına aittir. Tarih bilgisini ölç. "
        "İmla, dilbilgisi, kelime bilgisi veya genel paragraf-anlam sorusu üretme."
    ),
    "cografya": (
        "Bu soru coğrafya alanına aittir. Coğrafya bilgisini ölç. "
        "İmla, dilbilgisi, kelime bilgisi veya genel paragraf-anlam sorusu üretme."
    ),
    "matematik": (
        "Bu soru matematik alanına aittir. Matematiksel problem/akıl yürütme üret. "
        "Türkçe dilbilgisi, imla, kelime veya paragraf-anlam sorusu üretme. "
        "Soruyu matematik problemi olarak yaz; gereksiz hikâye/paragraf anlatımı kullanma. "
        "Gerekliyse LaTeX kullan; JSON içinde backslash kaçır (\\\\frac, \\\\sqrt). "
        "Düz metne veya Unicode kesire çevirme. Hesaplar tutarlı olsun; tek doğru cevap. "
        "Çeldiriciler tipik işlem/işaret/formül hatalarına dayansın. "
        "Çok adımlı sorularda her adım çözülebilir olsun. "
        "Zorluğu metin uzunluğuyla değil işlem/akıl yürütme yüküyle artır."
    ),
    "geometri": (
        "Bu soru geometri alanına aittir. Geometrik muhakeme/hesap üret. "
        "İmla, dilbilgisi, kelime veya paragraf-anlam sorusu üretme. "
        "Şekil/kenar/açı verilerini net ver; gereksiz paragraf anlatımı yok. "
        "Matematiksel ifadeleri LaTeX olarak yaz; JSON içinde backslash kaçır. "
        "Tek doğru cevap; çeldiriciler tipik geometri hatalarına dayansın. "
        "Zorluğu uzun metinle değil muhakeme adımlarıyla artır."
    ),
    "fizik": (
        "Bu soru fizik alanına aittir. Fizik kavramı veya hesabı ölç. "
        "İmla, dilbilgisi veya paragraf-anlam sorusu üretme. "
        "Gerekli büyüklük/birimleri ver; formülleri LaTeX olarak yaz; JSON içinde backslash kaçır. "
        "Hesap tutarlı olsun; tek doğru cevap; çeldiriciler birim/formül hatalarına dayansın. "
        "Zorluğu uzun anlatımla değil fiziksel muhakeme ile artır."
    ),
    "kimya": (
        "Bu soru kimya alanına aittir. Kimya kavramı veya hesabı ölç. "
        "İmla, dilbilgisi veya paragraf-anlam sorusu üretme. "
        "Formül/denklem/stokiyometri net olsun; tek doğru cevap. "
        "Çeldiriciler tipik mol/oran/işaret hatalarına dayansın. "
        "Gereksiz hikâye anlatımı yok."
    ),
    "biyoloji": (
        "Bu soru biyoloji alanına aittir. Biyoloji bilgisini ölç. "
        "İmla, dilbilgisi veya genel paragraf-anlam sorusu üretme. "
        "Kavram/süreç/ilişki sor; gereksiz edebi paragraf üretme. "
        "Tek doğru cevap; çeldiriciler yakın ama yanlış biyolojik ifadeler olsun."
    ),
    "fen": (
        "Bu soru fen bilimleri alanına aittir. Fen kavramı veya hesabı ölç. "
        "İmla, dilbilgisi veya paragraf-anlam sorusu üretme. "
        "Gerekiyorsa LaTeX kullan; tek doğru cevap; gereksiz hikâye yok."
    ),
    "felsefe": (
        "Bu soru felsefe alanına aittir. Felsefi kavram/argüman ölç. "
        "İmla, dilbilgisi veya genel paragraf-anlam sorusu üretme."
    ),
    "din": (
        "Bu soru din kültürü alanına aittir. İlgili kavram/bilgiyi ölç. "
        "İmla, dilbilgisi veya genel paragraf-anlam sorusu üretme."
    ),
    "vatandaslik": (
        "Bu soru vatandaşlık alanına aittir. Anayasa/devlet bilgisi ölç. "
        "İmla, dilbilgisi veya genel paragraf-anlam sorusu üretme."
    ),
    "guncel": (
        "Bu soru güncel bilgiler alanına aittir. "
        "İmla, dilbilgisi veya genel paragraf-anlam sorusu üretme."
    ),
    "quantitative": (
        "Bu soru sayısal muhakeme alanına aittir. Hesap/problem üret. "
        "Türkçe dilbilgisi, imla veya paragraf-anlam sorusu üretme. "
        "Kısa problem kökü kullan; gereksiz paragraf anlatımı yok. "
        "Matematiksel ifadeleri LaTeX olarak yaz; JSON içinde backslash kaçır. "
        "Hesap tutarlı; tek doğru cevap; çeldiriciler işlem hatalarına dayansın. "
        "Zorluğu uzun metinle değil adım sayısıyla artır."
    ),
    "verbal_reasoning": (
        "Bu soru sözel muhakeme alanına aittir. Mantık/anlam ilişkisi ölç. "
        "Yazım/noktalama (imla) sorusu üretme."
    ),
    "english": (
        "This question belongs to an English-language exam. "
        "Write the stem and choices in English. "
        "Do not produce Turkish spelling/grammar/paragraph items."
    ),
    "turkce": (
        "Bu soru Türkçe alanına aittir. Dil/anlam becerisini ölç."
    ),
    "edebiyat": (
        "Bu soru edebiyat alanına aittir. Edebi metin/dönem/tür bilgisini ölç."
    ),
    "unknown": (
        "Konuya uygun bir sınav sorusu yaz. "
        "İmla, dilbilgisi veya konu dışı paragraf-anlam sorusu üretme."
    ),
}


def domain_prompt_instruction(
    *,
    exam: str | None = None,
    subject_code: str | None = None,
    subject_name: str | None = None,
    topic_code: str | None = None,
    topic_name: str | None = None,
) -> str:
    """Short domain constraint for compact prompts. Uses resolver, not a second planner."""
    domain = resolve_domain(
        exam=exam,
        subject_code=subject_code,
        subject_name=subject_name,
        topic_code=topic_code,
        topic_name=topic_name,
    )
    return _DOMAIN_INSTRUCTIONS.get(domain, _DOMAIN_INSTRUCTIONS["unknown"])


def paragraph_length_for_stem(
    *,
    stem_type: str,
    para_avg: int,
    is_reading_topic: bool,
) -> int:
    """Keep reading stems long; cap knowledge/calc stems. No global shorten."""
    st = (stem_type or "").strip().lower()
    if is_reading_topic or st in LONG_STEM_TYPES:
        return max(40, int(para_avg))
    if st in SHORT_STEM_TYPES:
        return min(max(25, int(para_avg)), 50)
    return max(30, min(int(para_avg), 70))
