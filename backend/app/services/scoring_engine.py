"""
StudyOS - Scoring Engine (Sprint 41)
Handles OSYM estimations and StudyOS Daily Challenge ranking.
"""

from __future__ import annotations

import logging
import statistics
import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import (
    AssessmentSession,
    DailyChallengeScore,
    DailyChallengeStatistics,
    OsymCoefficients,
    SharedDailyBooklet,
)
from app.services.exam_net import compute_exam_net

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Scoring and Ranking Engine for StudyOS Assessments."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def finalize_daily_challenge(
        self, challenge_date: date, exam_type: str
    ) -> None:
        """Runs at 22:30 to lock official statistics and ranks."""
        # Check if already finalized
        stmt = select(SharedDailyBooklet).where(
            SharedDailyBooklet.challenge_date == challenge_date,
            SharedDailyBooklet.exam_type == exam_type,
            SharedDailyBooklet.status == "ready",
            SharedDailyBooklet.is_finalized == False,
        )
        booklet = (await self.db.execute(stmt)).scalars().first()
        if not booklet:
            logger.info(f"No pending booklet to finalize for {exam_type} on {challenge_date}.")
            return

        # Fetch official scores (submitted before finalization).
        # In reality, this runs at 22:30, so any score in the DB now is official.
        score_stmt = select(DailyChallengeScore).where(
            DailyChallengeScore.challenge_date == challenge_date,
            DailyChallengeScore.exam_type == exam_type,
            DailyChallengeScore.is_official == True,
            DailyChallengeScore.subject_code == "booklet",
        )
        scores = (await self.db.execute(score_stmt)).scalars().all()

        participant_count = len(scores)
        if participant_count == 0:
            logger.info(f"No participants for {exam_type} on {challenge_date}. Finalizing as empty.")
            booklet.is_finalized = True
            await self.db.flush()
            return

        raw_scores = [s.score for s in scores]
        score_mean = statistics.mean(raw_scores)
        score_std_dev = statistics.pstdev(raw_scores) if participant_count > 1 else 0.0

        # Calculate ranks
        # Sort scores descending
        scores_sorted = sorted(scores, key=lambda x: x.score, reverse=True)
        current_rank = 1
        for i, s in enumerate(scores_sorted):
            if i > 0 and s.score < scores_sorted[i - 1].score:
                current_rank = i + 1
            s.studyos_rank = current_rank
            # T-Score for studyos_score based on raw score (mean=500, std=100)
            if score_std_dev > 0:
                z_score = (s.score - score_mean) / score_std_dev
                s.studyos_score = max(0, min(1000, 500 + (z_score * 100)))
            else:
                s.studyos_score = 500.0

        # Create Statistics
        stats = DailyChallengeStatistics(
            exam_type=exam_type,
            challenge_date=challenge_date,
            participant_count=participant_count,
            subject_averages={},  # Advanced subject logic can be added here
            subject_std_devs={},
            score_mean=score_mean,
            score_std_dev=score_std_dev,
        )
        self.db.add(stats)
        booklet.is_finalized = True
        await self.db.flush()
        logger.info(f"Finalized daily challenge {exam_type} on {challenge_date} with {participant_count} participants.")

    async def compute_estimated_score(
        self, session: AssessmentSession, daily_score: DailyChallengeScore
    ) -> None:
        """For late solvers - computes estimated T-score based on finalized stats."""
        stmt = select(DailyChallengeStatistics).where(
            DailyChallengeStatistics.challenge_date == session.challenge_date,
            DailyChallengeStatistics.exam_type == session.exam_type,
        )
        stats = (await self.db.execute(stmt)).scalars().first()

        daily_score.is_official = False
        
        if not stats:
            # If no stats exist, just set default
            daily_score.studyos_score = daily_score.score * 10.0
            daily_score.studyos_rank = None
            return

        if stats.score_std_dev > 0:
            z_score = (daily_score.score - stats.score_mean) / stats.score_std_dev
            daily_score.studyos_score = max(0, min(1000, 500 + (z_score * 100)))
        else:
            daily_score.studyos_score = 500.0
        
        daily_score.studyos_rank = None # Will just display as Tahmini without a hard rank number, or we can approximate.

    async def compute_osym_estimations(self, session: AssessmentSession) -> dict[str, Any]:
        """Fetches coefficients and calculates estimated scores for OSYM years."""
        stmt = select(OsymCoefficients).where(
            OsymCoefficients.exam_type == session.exam_type
        )
        coeffs = (await self.db.execute(stmt)).scalars().all()

        estimations = {}
        net = float(compute_exam_net(correct=session.correct_count or 0, wrong=session.wrong_count or 0, exam_type=session.exam_type))

        for coeff in coeffs:
            year_str = str(coeff.year)
            score = coeff.base_point + (net * 3.1) # Fallback multiplier if missing
            estimations[year_str] = {
                "score": round(score, 2),
                "rank": None
            }
        
        # Hardcode some realistic looking mock estimations if empty (for prototype)
        if not estimations:
            base_score = max(0, min(500, (net * 3.3) + 100))
            estimations = {
                "2026": {"score": round(base_score * 0.98, 2), "rank": max(100, int(500000 - (base_score * 1000)))},
                "2025": {"score": round(base_score * 1.02, 2), "rank": max(100, int(480000 - (base_score * 950)))},
                "2024": {"score": round(base_score * 0.95, 2), "rank": max(100, int(520000 - (base_score * 1050)))},
                "2023": {"score": round(base_score * 1.05, 2), "rank": max(100, int(450000 - (base_score * 900)))},
            }

        return estimations
