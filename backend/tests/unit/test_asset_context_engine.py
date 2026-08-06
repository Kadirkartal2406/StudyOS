"""
Unit tests for EAE Asset Context Engine (AI Layer).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.educational_asset import EducationalAsset, EducationalAssetNode
from app.services.ai.asset_context_engine import AssetContextEngine
from app.services.question_intelligence.eae_node_verifier import EAENodeVerifier


@pytest.fixture
def mock_asset():
    asset = EducationalAsset(
        asset_id="studyos://assets/geography/turkey_admin/v1",
        version="1.0.0",
        domain="geography",
        format="svg",
        title={"tr": "Türkiye Haritası"},
        viewport={"width": 1000, "height": 500},
        tags=["map"],
    )
    asset.nodes = [
        EducationalAssetNode(
            node_id="turkey_admin_v1::province::konya",
            name={"tr": "Konya"},
            bounding_box=[32.0, 36.5, 34.5, 38.5],
            attributes={"region": "Central Anatolia"},
        ),
        EducationalAssetNode(
            node_id="turkey_admin_v1::province::ankara",
            name={"tr": "Ankara"},
            bounding_box=[32.5, 39.0, 33.5, 40.0],
            attributes={"region": "Central Anatolia"},
        ),
    ]
    return asset


@pytest.mark.asyncio
async def test_get_asset_context(mock_asset):
    db_mock = AsyncMock()
    # Mock the execute result for sqlalchemy
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_asset
    db_mock.execute.return_value = mock_result

    engine = AssetContextEngine(db_mock)
    context = await engine.get_asset_context("studyos://assets/geography/turkey_admin/v1")
    
    assert context is not None
    assert context["asset_id"] == "studyos://assets/geography/turkey_admin/v1"
    assert len(context["nodes"]) == 2
    assert context["nodes"][0]["node_id"] == "turkey_admin_v1::province::konya"


def test_inject_to_prompt():
    engine = AssetContextEngine(MagicMock())
    context = {
        "asset_id": "test_asset",
        "title": {"en": "Test"},
        "viewport": {},
        "format": "svg",
        "nodes": [
            {"node_id": "node1", "name": {"en": "Node 1"}, "bounding_box": [], "attributes": {}}
        ]
    }
    
    base_prompt = "You are a teacher."
    result = engine.inject_to_prompt(base_prompt, context)
    
    assert base_prompt in result
    assert "EDUCATIONAL ASSET CONTEXT" in result
    assert "node1" in result




