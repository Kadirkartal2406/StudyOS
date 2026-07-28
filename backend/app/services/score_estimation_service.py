"""
Sprint 18 — Score estimation & same-exam ranking (istatistiksel; ÖSYM değil).
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import EstimatedScoreSnapshot
from app.repositories.assessment_repository import AssessmentRepository


class ScoreEstimationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AssessmentRepository(db)

    async def refresh(
        self, user_id: uuid.UUID, exam_type: str
    ) -> EstimatedScoreSnapshot:
        sessions = await self.repo.list_submitted_for_exam(user_id, exam_type)
        accuracies = [
            float(s.accuracy)
            for s in sessions
            if s.accuracy is not None
        ]
        if not accuracies:
            success = 0.0
            score = 0.0
            strongest = None
            weakest = None
            commentary = "Henüz assessment sonucu yok — mini deneme ile başla."
        else:
            success = sum(accuracies) / len(accuracies)
            score = round(success * 100, 1)
            by_subject: dict[str, list[float]] = {}
            for s in sessions:
                if s.subject_name and s.accuracy is not None:
                    by_subject.setdefault(s.subject_name, []).append(float(s.accuracy))
            avg_sub = {
                k: sum(v) / len(v) for k, v in by_subject.items() if v
            }
            strongest = max(avg_sub, key=avg_sub.get) if avg_sub else None
            # Below 70% accuracy only — relative min of strong subjects is not "weak"
            weakest_candidate = min(avg_sub, key=avg_sub.get) if avg_sub else None
            weakest = (
                weakest_candidate
                if weakest_candidate is not None
                and avg_sub[weakest_candidate] < 0.70
                else None
            )
            commentary = (
                f"Tahmini başarı %{score:.0f}."
                + (f" En güçlü: {strongest}." if strongest else "")
                + (
                    f" Hedefe uzak: {weakest}."
                    if weakest and weakest != strongest
                    else ""
                )
            )

        peers = await self.repo.list_peer_accuracies(exam_type)
        sample = len(peers)
        if sample < 1 or not accuracies:
            rank_pct = 50.0
        else:
            my = sum(accuracies) / len(accuracies)
            below = sum(1 for p in peers if p < my)
            rank_pct = round((1 - (below / sample)) * 100, 1)
            rank_pct = min(max(rank_pct, 1.0), 99.0)

        snap = EstimatedScoreSnapshot(
            user_id=user_id,
            exam_type=exam_type,
            estimated_score=score if accuracies else 0.0,
            estimated_success_pct=round(success * 100, 1) if accuracies else 0.0,
            estimated_rank_pct=rank_pct,
            peer_sample_size=sample,
            strongest_subject=strongest,
            weakest_subject=weakest,
            commentary=commentary,
            metadata_={
                "session_count": len(sessions),
                "mean_accuracy": round(success, 4) if accuracies else 0,
            },
        )
        self.db.add(snap)
        await self.db.flush()
        return snap
