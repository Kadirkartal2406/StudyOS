"""
Unit tests for EAE Asset Registry, Search, and Version Services.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.core.asset_contracts.schemas import AssetManifestSchemaDTO
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.educational_asset import (
    EducationalAsset,
    EducationalAssetNode,
    EducationalAssetVersion,
)
from app.schemas.educational_asset import AssetSearchQueryDTO
from app.services.asset_registry_service import AssetRegistryService
from app.services.asset_search_service import AssetSearchService
from app.services.asset_version_service import AssetVersionService
from tests.unit.geo_fixture_attrs import geo_node_attrs


@pytest.fixture
def sample_manifest_v1():
    return {
        "schema_version": "1.0",
        "asset_id": "studyos://assets/geography/turkey_admin/v1",
        "version": "1.0.0",
        "domain": "geography",
        "format": "svg",
        "title": {"tr": "Türkiye İdari Haritası", "en": "Administrative Map of Turkey"},
        "viewport": {
            "width": 1000.0,
            "height": 500.0,
            "default_scale": 1.0,
            "max_scale": 8.0,
        },
        "layers": [
            {
                "id": "provinces_layer",
                "z_index": 1,
                "min_lod": 1.0,
                "nodes": [
                    {
                        "id": "turkey_admin_v1::province::konya",
                        "name": {"tr": "Konya", "en": "Konya"},
                        "bounding_box": [32.0, 36.5, 34.5, 38.5],
                        "attributes": geo_node_attrs("province"),
                    },
                    {
                        "id": "turkey_admin_v1::province::ankara",
                        "name": {"tr": "Ankara", "en": "Ankara"},
                        "bounding_box": [32.5, 39.0, 33.5, 40.0],
                        "attributes": geo_node_attrs("province"),
                    },
                ],
            }
        ],
        "tags": ["map", "turkey", "provinces"],
        "license_type": "studyos_core",
    }


@pytest.mark.asyncio
async def test_register_asset_new(sample_manifest_v1):
    db_mock = AsyncMock()
    service = AssetRegistryService(db_mock)
    service.repo.get_by_asset_id = AsyncMock(return_value=None)
    service.repo.create_asset = AsyncMock()

    mock_created = EducationalAsset(
        id=uuid.uuid4(),
        asset_id=sample_manifest_v1["asset_id"],
        version="1.0.0",
        domain="geography",
        format="svg",
        title=sample_manifest_v1["title"],
        viewport=sample_manifest_v1["viewport"],
        tags=sample_manifest_v1["tags"],
        license_type="studyos_core",
    )
    service.repo.create_asset.return_value = mock_created

    asset = await service.register_asset_manifest(sample_manifest_v1)
    assert asset.asset_id == "studyos://assets/geography/turkey_admin/v1"
    assert service.repo.create_asset.called


@pytest.mark.asyncio
async def test_get_asset_by_id_not_found():
    db_mock = AsyncMock()
    service = AssetRegistryService(db_mock)
    service.repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.get_asset_by_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_upgrade_lower_version_conflict(sample_manifest_v1):
    db_mock = AsyncMock()
    version_svc = AssetVersionService(db_mock)

    existing = EducationalAsset(
        id=uuid.uuid4(),
        asset_id=sample_manifest_v1["asset_id"],
        version="1.2.0",
        domain="geography",
        format="svg",
        title=sample_manifest_v1["title"],
        viewport=sample_manifest_v1["viewport"],
        tags=sample_manifest_v1["tags"],
        nodes=[],
    )

    new_manifest_lower = AssetManifestSchemaDTO.model_validate(sample_manifest_v1)
    new_manifest_lower.version = "1.0.0"

    with pytest.raises(ConflictError):
        await version_svc.upgrade_asset_version(
            existing_asset=existing, new_manifest=new_manifest_lower
        )


@pytest.mark.asyncio
async def test_deprecate_asset():
    db_mock = AsyncMock()
    version_svc = AssetVersionService(db_mock)
    mock_asset = EducationalAsset(
        id=uuid.uuid4(),
        asset_id="studyos://assets/geography/turkey_admin/v1",
        version="1.0.0",
        domain="geography",
        format="svg",
        title={"tr": "Test"},
        viewport={"width": 100, "height": 100},
        tags=[],
        is_deprecated=False,
    )
    version_svc.repo.get_by_asset_id = AsyncMock(return_value=mock_asset)

    deprecated = await version_svc.deprecate_asset("studyos://assets/geography/turkey_admin/v1")
    assert deprecated.is_deprecated


@pytest.mark.asyncio
async def test_search_service_calls_repo():
    db_mock = AsyncMock()
    search_svc = AssetSearchService(db_mock)
    search_svc.repo.search_assets = AsyncMock(return_value=([], 0))

    query_dto = AssetSearchQueryDTO(domain="geography", q="Konya")
    items, total = await search_svc.search(query_dto)
    assert items == []
    assert total == 0
    search_svc.repo.search_assets.assert_called_once_with(query_dto)
