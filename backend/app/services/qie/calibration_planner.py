"""Calibration Engine v2 — distinct skills per question, no skill repeat."""

from __future__ import annotations

from app.services.qie.distractor_model import pick_distractor
from app.services.qie.planner import _bloom_for
from app.services.qie.types import QuestionPlan

KPSS_TURKCE_SKILLS: list[dict[str, str]] = [
    {"skill": "vocabulary", "stem_type": "vocabulary", "label": "Sözcük"},
    {"skill": "sentence_meaning", "stem_type": "inference", "label": "Cümle"},
    {"skill": "main_idea", "stem_type": "main_idea", "label": "Ana fikir"},
    {"skill": "supporting_idea", "stem_type": "supporting_detail", "label": "Yardımcı düşünce"},
    {"skill": "paragraph_completion", "stem_type": "paragraph_completion", "label": "Paragraf tamamlama"},
    {"skill": "sentence_ordering", "stem_type": "sentence_ordering", "label": "Paragraf sıralama"},
    {"skill": "coherence", "stem_type": "coherence", "label": "Anlatım bozukluğu"},
    {"skill": "grammar", "stem_type": "grammar", "label": "Dil bilgisi"},
    {"skill": "spelling", "stem_type": "spelling", "label": "Yazım"},
    {"skill": "punctuation", "stem_type": "punctuation", "label": "Noktalama"},
    {"skill": "logic", "stem_type": "logic", "label": "Mantık"},
    {"skill": "mixed_reasoning", "stem_type": "comparison", "label": "Karma"},
]

DEFAULT_CALIBRATION_SKILLS = list(KPSS_TURKCE_SKILLS)

_BY_EXAM_SUBJECT: dict[tuple[str, str], list[dict[str, str]]] = {
    ("kpss", "turkce"): KPSS_TURKCE_SKILLS,
    ("kpss", "kpss_turkce"): KPSS_TURKCE_SKILLS,
    ("ags", "turkce"): KPSS_TURKCE_SKILLS,
}


def resolve_skill_catalog(exam: str, subject_code: str) -> list[dict[str, str]]:
    e = (exam or "").lower().strip()
    s = (subject_code or "").lower().strip()
    for (ex, sub), skills in _BY_EXAM_SUBJECT.items():
        if e == ex and (s == sub or sub in s or s.endswith(sub)):
            return skills
    if "turk" in s:
        return KPSS_TURKCE_SKILLS
    return list(DEFAULT_CALIBRATION_SKILLS)


class CalibrationPlanner:
    """Build N plans with unique skills (calibration / level test)."""

    def plan(
        self,
        *,
        exam: str,
        subject_code: str,
        subject_name: str,
        topic_code: str,
        topic_name: str,
        count: int = 12,
        difficulty_band: str = "medium",
        choice_count: int = 5,
        paragraph_length: int = 180,
        reading_time_sec: int = 75,
        start_index: int = 0,
        skill_slice: list[dict[str, str]] | None = None,
        difficulty_override: int | None = None,
    ) -> list[QuestionPlan]:
        catalog = skill_slice or resolve_skill_catalog(exam, subject_code)
        n = max(1, count)
        base_diff = {"easy": 50, "medium": 68, "hard": 82}.get(
            (difficulty_band or "medium").lower(), 68
        )
        # Prefer unique skills when catalog allows
        slots = catalog[:n] if len(catalog) >= n else [
            catalog[i % len(catalog)] for i in range(n)
        ]
        plans: list[QuestionPlan] = []
        used_patterns: list[str] = []
        for i, slot in enumerate(slots):
            difficulty = (
                difficulty_override
                if difficulty_override is not None
                else max(30, min(95, base_diff + ((i * 5) % 17) - 8))
            )
            distractor = pick_distractor(
                index=start_index + i, forbidden=used_patterns
            )
            used_patterns.append(distractor)
            plans.append(
                QuestionPlan(
                    exam=exam,
                    subject_code=subject_code,
                    subject_name=subject_name,
                    topic_code=topic_code,
                    topic_name=topic_name or slot.get("label") or slot["skill"],
                    skill=slot["skill"],
                    difficulty=difficulty,
                    bloom=_bloom_for(difficulty),
                    reasoning_type="inference",
                    paragraph_length=paragraph_length,
                    reading_time_sec=reading_time_sec,
                    stem_type=slot.get("stem_type") or slot["skill"],
                    distractor_pattern=distractor,
                    target_time_sec=max(45, reading_time_sec + 10),
                    target_accuracy=max(0.35, min(0.7, 1.0 - difficulty / 150)),
                    forbidden_recent_patterns=list(used_patterns[-4:]),
                    choice_count=choice_count,
                    index=start_index + i,
                    pack="calibration",
                )
            )
        return plans
