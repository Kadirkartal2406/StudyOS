"""
Unit tests for EAE Sub-Node Evidence Bridge.
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.topic_evidence import TopicEvidence
from app.services.eae_evidence_bridge import EAEEvidenceBridge


@pytest.mark.asyncio
async def test_ingest_sub_node_evidence():
    db_mock = AsyncMock()
    bridge = EAEEvidenceBridge(db_mock)

    user_id = uuid.uuid4()
    mock_evidence = TopicEvidence(
        id=uuid.uuid4(),
        user_id=user_id,
        subject_code="geography",
        topic_code="turkey_provinces",
        category="performance",
        value=1.0,
        quality_weight=0.85,
        metadata_={"eae_sub_node_id": "turkey_admin_v1::province::konya"},
    )

    bridge.evidence_repo.add_evidence = AsyncMock(return_value=mock_evidence)
    bridge.evidence_service.trigger_confidence_recalculation = AsyncMock()

    result = await bridge.ingest_sub_node_evidence(
        user_id=user_id,
        subject_code="geography",
        topic_code="turkey_provinces",
        node_id="turkey_admin_v1::province::konya",
        is_correct=True,
    )

    assert result.user_id == user_id
    assert result.metadata_["eae_sub_node_id"] == "turkey_admin_v1::province::konya"
    bridge.evidence_repo.add_evidence.assert_called_once()
    bridge.evidence_service.trigger_confidence_recalculation.assert_called_once_with(
        user_id=user_id,
        subject_code="geography",
        topic_code="turkey_provinces",
    )


@pytest.mark.asyncio
async def test_ingest_node_selection_misconception():
    db_mock = AsyncMock()
    bridge = EAEEvidenceBridge(db_mock)
    user_id = uuid.uuid4()

    async def _capture(evidence):
        return evidence

    bridge.evidence_repo.add_evidence = AsyncMock(side_effect=_capture)
    bridge.evidence_service.trigger_confidence_recalculation = AsyncMock()

    result = await bridge.ingest_node_selection(
        user_id=user_id,
        subject_code="geography",
        topic_code="hidrografya",
        expected_node_id="turkey_hydro_v1::river::kizilirmak",
        selected_node_id="turkey_hydro_v1::river::sakarya",
        confusable_with=["turkey_hydro_v1::river::sakarya"],
    )

    assert result.value == 0.0
    assert result.metadata_["misconception_key"] == (
        "turkey_hydro_v1::river::kizilirmak->turkey_hydro_v1::river::sakarya"
    )
    assert result.metadata_["confusable_pair"] is True
