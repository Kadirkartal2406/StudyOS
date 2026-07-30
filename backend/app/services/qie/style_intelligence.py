"""Exam Style Intelligence v2 — statistical DNA for prompts (no copyrighted text)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exam_style_service import ExamStyleService


class StyleIntelligence:
    """Read exam style DNA; never stores real exam stems."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._svc = ExamStyleService(db)

    async def ensure_synced(self) -> None:
        try:
            await self._svc.ensure_synced()
        except Exception:
            pass

    async def dna(
        self,
        exam: str,
        *,
        subject_code: str | None = None,
        difficulty: str | None = None,
    ) -> dict[str, Any]:
        await self.ensure_synced()
        profile = await self._svc.get_profile(exam)
        stat = None
        if subject_code:
            stat = await self._svc.get_stat(exam, subject_code=subject_code)
        if profile is None:
            return self._fallback_dna(exam, difficulty=difficulty)

        base = self._svc.profile_to_prompt_dict(
            profile, stat=stat, difficulty=difficulty
        )
        meta = dict(getattr(profile, "style_rules", None) or {})
        profile_meta = {}
        # v2 DNA fields live in style_rules / avoid + expanded seed metadata
        if hasattr(profile, "notes") and profile.notes:
            pass

        dna: dict[str, Any] = {
            **base,
            "exam_code": getattr(profile, "exam_code", exam),
            "paragraph_length_avg": float(
                (stat.paragraph_length_avg if stat else None)
                or ((profile.paragraph_words_min + profile.paragraph_words_max) / 2)
            ),
            "paragraph_length_range": [
                profile.paragraph_words_min,
                profile.paragraph_words_max,
            ],
            "sentence_count": float(
                (stat.sentence_count_avg if stat else None) or 6.0
            ),
            "option_length": {
                "min": profile.option_words_min,
                "max": profile.option_words_max,
            },
            "option_similarity": meta.get("option_similarity", "medium"),
            "distractor_patterns": list(
                getattr(profile, "distractor_types", None) or []
            ),
            "vocabulary_level": (
                (stat.vocabulary_level if stat else None)
                or profile.language_level
            ),
            "reading_time": int(
                (stat.reading_time_sec_avg if stat else None)
                or profile.reading_time_sec_avg
            ),
            "bloom_distribution": meta.get(
                "bloom_distribution",
                {profile.bloom_default: 0.6, "apply": 0.25, "understand": 0.15},
            ),
            "reasoning_distribution": meta.get(
                "reasoning_distribution",
                {"inference": 0.45, "comparison": 0.2, "elimination": 0.35},
            ),
            "skill_distribution": meta.get("skill_distribution", {}),
            "difficulty_distribution": meta.get(
                "difficulty_distribution",
                {"easy": 0.2, "medium": 0.45, "hard": 0.35},
            ),
            "stem_type_distribution": meta.get("stem_type_distribution", {}),
            "option_style": meta.get("option_style", "parallel_length"),
            "wording_style": meta.get("wording_style", profile.language_level),
            "abstraction_level": meta.get("abstraction_level", "moderate"),
            "inference_ratio": float(meta.get("inference_ratio", 0.55)),
            "elimination_ratio": float(meta.get("elimination_ratio", 0.4)),
            "reading_time_sec_avg": int(profile.reading_time_sec_avg),
        }
        # Merge seed DNA from style_rules if present
        for key in (
            "bloom_distribution",
            "reasoning_distribution",
            "skill_distribution",
            "difficulty_distribution",
            "stem_type_distribution",
            "option_style",
            "wording_style",
            "abstraction_level",
            "inference_ratio",
            "elimination_ratio",
            "option_similarity",
        ):
            if key in meta:
                dna[key] = meta[key]
        if profile_meta:
            dna.update(profile_meta)
        return dna

    def _fallback_dna(
        self, exam: str, *, difficulty: str | None = None
    ) -> dict[str, Any]:
        return {
            "exam_code": (exam or "kpss").lower(),
            "choice_count": 4 if (exam or "").strip().lower() == "lgs" else 5,
            "difficulty": difficulty or "medium",
            "paragraph_length_avg": 160,
            "paragraph_length_range": [80, 220],
            "sentence_count": 7,
            "option_length": {"min": 3, "max": 28},
            "option_similarity": "medium",
            "distractor_patterns": [
                "meaning_shift",
                "half_correct",
                "scope_shift",
                "terminology_confusion",
            ],
            "vocabulary_level": "formal_tr",
            "reading_time": 75,
            "bloom_distribution": {"analyze": 0.5, "apply": 0.3, "understand": 0.2},
            "reasoning_distribution": {"inference": 0.5, "elimination": 0.3},
            "skill_distribution": {},
            "difficulty_distribution": {"easy": 0.2, "medium": 0.5, "hard": 0.3},
            "stem_type_distribution": {},
            "option_style": "parallel_length",
            "wording_style": "formal_osym",
            "abstraction_level": "moderate",
            "inference_ratio": 0.55,
            "elimination_ratio": 0.4,
            "reading_time_sec_avg": 75,
            "paragraph_words": "80-220",
        }
