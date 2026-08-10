"""Sprint 23 — Exam Style Intelligence service (read + seed)."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam_style import ExamStyleProfile, ExamStyleStat
from app.services.exam_style.seed import build_exam_style_seed

logger = logging.getLogger("studyos.exam_style")


class ExamStyleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ensure_synced(self) -> int:
        """Idempotent upsert of style profiles + stats. Returns profile count touched."""
        seed = build_exam_style_seed()
        n = 0
        for row in seed:
            await self._upsert_profile(row)
            n += 1
            for st in row.get("stats") or []:
                await self._upsert_stat(row["exam_code"], st)
        await self.db.flush()
        return n

    async def get_profile(self, exam_code: str) -> ExamStyleProfile | None:
        code = (exam_code or "").strip().lower()
        if not code:
            return None
        
        # Try exact match first
        result = await self.db.execute(
            select(ExamStyleProfile).where(
                ExamStyleProfile.exam_code == code,
                ExamStyleProfile.is_active.is_(True),
            )
        )
        profile = result.scalar_one_or_none()
        
        # Fallbacks for variants to base exam styles
        if profile is None:
            base_code = code
            if code.startswith("kpss_"):
                base_code = "kpss"
            elif code.startswith("ayt_"):
                base_code = "ayt"
            elif code.startswith("yds_"):
                base_code = "yds"
            elif code.startswith("yokdil_"):
                base_code = "yokdil"
            elif code.startswith("ydt_"):
                base_code = "ydt"
            elif code.startswith("ales_"):
                base_code = "ales"
            elif code.startswith("dgs_"):
                base_code = "dgs"
            elif code == "yks":
                base_code = "tyt"
                
            if base_code != code:
                result = await self.db.execute(
                    select(ExamStyleProfile).where(
                        ExamStyleProfile.exam_code == base_code,
                        ExamStyleProfile.is_active.is_(True),
                    )
                )
                profile = result.scalar_one_or_none()
                
        return profile

    async def get_stat(
        self,
        exam_code: str,
        *,
        subject_code: str | None = None,
        skill_type: str | None = None,
    ) -> ExamStyleStat | None:
        code = (exam_code or "").strip().lower()
        
        # First try exact
        q = select(ExamStyleStat).where(ExamStyleStat.exam_code == code)
        if subject_code:
            q = q.where(ExamStyleStat.subject_code == subject_code)
        if skill_type:
            q = q.where(ExamStyleStat.skill_type == skill_type)
        q = q.limit(1)
        result = await self.db.execute(q)
        stat = result.scalar_one_or_none()
        
        # Fallback to base
        if stat is None:
            base_code = code
            if code.startswith("kpss_"):
                base_code = "kpss"
            elif code.startswith("ayt_"):
                base_code = "ayt"
            elif code.startswith("yds_"):
                base_code = "yds"
            elif code.startswith("yokdil_"):
                base_code = "yokdil"
            elif code.startswith("ydt_"):
                base_code = "ydt"
            elif code.startswith("ales_"):
                base_code = "ales"
            elif code.startswith("dgs_"):
                base_code = "dgs"
                
            if base_code != code:
                q = select(ExamStyleStat).where(ExamStyleStat.exam_code == base_code)
                if subject_code:
                    q = q.where(ExamStyleStat.subject_code == subject_code)
                if skill_type:
                    q = q.where(ExamStyleStat.skill_type == skill_type)
                q = q.limit(1)
                result = await self.db.execute(q)
                stat = result.scalar_one_or_none()
                
        return stat

    def profile_to_prompt_dict(
        self,
        profile: ExamStyleProfile,
        *,
        stat: ExamStyleStat | None = None,
        difficulty: str | None = None,
        bloom: str | None = None,
    ) -> dict[str, Any]:
        para_min = profile.paragraph_words_min
        para_max = profile.paragraph_words_max
        if stat and stat.paragraph_length_avg:
            avg = int(stat.paragraph_length_avg)
            para_min = max(para_min, int(avg * 0.85))
            para_max = max(para_max, int(avg * 1.15))
        return {
            "exam": profile.exam_code.upper(),
            "exam_name": profile.name,
            "question_format": profile.question_format,
            "paragraph_words": f"{para_min}-{para_max}",
            "stem_words": f"{profile.stem_words_min}-{profile.stem_words_max}",
            "option_words": f"{profile.option_words_min}-{profile.option_words_max}",
            "choice_count": profile.choice_count,
            "distractor_strength": profile.distractor_strength,
            "distractor_types": list(profile.distractor_types or []),
            "bloom": bloom or (stat.reasoning_type if stat else None) or profile.bloom_default,
            "language_level": profile.language_level,
            "reading_time_sec": int(
                (stat.reading_time_sec_avg if stat else None)
                or profile.reading_time_sec_avg
            ),
            "difficulty": difficulty or profile.difficulty_band_default,
            "style_rules": dict(profile.style_rules or {}),
            "avoid": list(profile.avoid_patterns or []),
            "reasoning_type": (stat.reasoning_type if stat else None) or "inference",
            "vocabulary_level": (stat.vocabulary_level if stat else None)
            or profile.language_level,
            "source": profile.source,
        }

    async def _upsert_profile(self, data: dict[str, Any]) -> ExamStyleProfile:
        code = data["exam_code"].lower()
        result = await self.db.execute(
            select(ExamStyleProfile).where(ExamStyleProfile.exam_code == code)
        )
        row = result.scalar_one_or_none()
        fields = {
            "name": data["name"],
            "question_format": data.get("question_format") or "mixed",
            "paragraph_words_min": int(data.get("paragraph_words_min") or 40),
            "paragraph_words_max": int(data.get("paragraph_words_max") or 120),
            "stem_words_min": int(data.get("stem_words_min") or 12),
            "stem_words_max": int(data.get("stem_words_max") or 80),
            "option_words_min": int(data.get("option_words_min") or 2),
            "option_words_max": int(data.get("option_words_max") or 25),
            "choice_count": int(data.get("choice_count") or 5),
            "distractor_strength": data.get("distractor_strength") or "strong",
            "bloom_default": data.get("bloom_default") or "analyze",
            "language_level": data.get("language_level") or "formal_tr",
            "reading_time_sec_avg": int(data.get("reading_time_sec_avg") or 60),
            "difficulty_band_default": data.get("difficulty_band_default") or "high",
            "style_rules": data.get("style_rules") or {},
            "avoid_patterns": data.get("avoid_patterns") or [],
            "distractor_types": data.get("distractor_types") or [],
            "source": data.get("source") or "estimated",
            "is_active": True,
        }
        if row is None:
            row = ExamStyleProfile(exam_code=code, **fields)
            self.db.add(row)
        else:
            for k, v in fields.items():
                setattr(row, k, v)
        return row

    async def _upsert_stat(self, exam_code: str, data: dict[str, Any]) -> ExamStyleStat:
        code = exam_code.lower()
        subject = data.get("subject_code")
        skill = data.get("skill_type") or "general"
        q = select(ExamStyleStat).where(
            ExamStyleStat.exam_code == code,
            ExamStyleStat.skill_type == skill,
        )
        if subject:
            q = q.where(ExamStyleStat.subject_code == subject)
        else:
            q = q.where(ExamStyleStat.subject_code.is_(None))
        result = await self.db.execute(q)
        row = result.scalar_one_or_none()
        fields = {
            "subject_code": subject,
            "skill_type": skill,
            "paragraph_length_avg": float(data.get("paragraph_length_avg") or 0),
            "sentence_count_avg": float(data.get("sentence_count_avg") or 0),
            "distractor_pattern": data.get("distractor_pattern") or "plausible",
            "reasoning_type": data.get("reasoning_type") or "inference",
            "vocabulary_level": data.get("vocabulary_level") or "formal",
            "option_distribution": data.get("option_distribution") or {},
            "reading_time_sec_avg": float(data.get("reading_time_sec_avg") or 60),
            "difficulty_band": data.get("difficulty_band") or "medium",
            "sample_size": int(data.get("sample_size") or 0),
            "source": data.get("source") or "estimated",
            "metadata_": data.get("metadata") or {},
        }
        if row is None:
            row = ExamStyleStat(exam_code=code, **fields)
            self.db.add(row)
        else:
            for k, v in fields.items():
                setattr(row, k, v)
        return row
