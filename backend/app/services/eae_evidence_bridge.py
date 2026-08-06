"""
StudyOS Educational Asset Engine (EAE) — Sub-Node Evidence Bridge
Binds sub-node EAE visual interactions and node-level mistakes to TopicEvidence in EvidenceService.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_evidence import (
    EvidenceCategory,
    EvidenceHorizon,
    EvidenceSourceType,
    TopicEvidence,
)
from app.repositories.topic_evidence_repository import TopicEvidenceRepository
from app.services.evidence_service import EvidenceService


class EAEEvidenceBridge:
    """
    Sub-node evidence bridge binding EAE visual node interaction & mistakes to StudyOS Evidence Engine.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.evidence_repo = TopicEvidenceRepository(db)
        self.evidence_service = EvidenceService(db)

    async def ingest_sub_node_evidence(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        node_id: str,
        is_correct: bool,
        confidence_weight: float = 0.85,
        horizon: EvidenceHorizon = EvidenceHorizon.INSTANT,
        *,
        expected_node_id: str | None = None,
        selected_node_id: str | None = None,
        confusable_pair: bool = False,
    ) -> TopicEvidence:
        """
        Ingests sub-node visual interaction evidence and triggers Confidence Engine update.
        """
        accuracy_value = 1.0 if is_correct else 0.0
        selected = selected_node_id or node_id
        expected = expected_node_id or (node_id if is_correct else None)
        metadata: dict[str, Any] = {
            "eae_sub_node_id": node_id,
            "eae_node_id": selected,
            "is_correct": is_correct,
            "sub_node_signal": True,
        }
        if expected:
            metadata["expected_node_id"] = expected
        if selected:
            metadata["selected_node_id"] = selected
        if expected and selected and expected != selected:
            metadata["misconception_key"] = f"{expected}->{selected}"
            metadata["confusable_pair"] = confusable_pair

        evidence = TopicEvidence(
            user_id=user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.PERFORMANCE,
            horizon=horizon,
            value=accuracy_value,
            quality_weight=round(confidence_weight, 3),
            source_type=EvidenceSourceType.QUESTION_RECORD,
            metadata_=metadata,
            occurred_at=datetime.now(UTC),
        )

        saved = await self.evidence_repo.add_evidence(evidence)
        await self.evidence_service.trigger_confidence_recalculation(
            user_id=user_id,
            subject_code=subject_code,
            topic_code=topic_code,
        )
        return saved

    async def ingest_node_selection(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        expected_node_id: str,
        selected_node_id: str,
        *,
        confusable_with: list[str] | None = None,
        confidence_weight: float = 0.9,
    ) -> TopicEvidence:
        """Record a map-selection answer with misconception tagging for confusable pairs."""
        is_correct = expected_node_id == selected_node_id
        confusable = False
        if not is_correct and confusable_with:
            confusable = selected_node_id in confusable_with
        elif not is_correct:
            # bidirectional key presence is enough for tagging when caller omits list
            confusable = True
        return await self.ingest_sub_node_evidence(
            user_id=user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            node_id=selected_node_id,
            is_correct=is_correct,
            confidence_weight=confidence_weight,
            expected_node_id=expected_node_id,
            selected_node_id=selected_node_id,
            confusable_pair=confusable and not is_correct,
        )
