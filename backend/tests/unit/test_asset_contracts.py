"""
Unit tests for EAE Asset Contracts, Pydantic Schemas, and Validators.
"""

import pytest
from pydantic import ValidationError

from app.core.asset_contracts.constants import (
    ASSET_URI_PATTERN,
    NODE_ID_PATTERN,
    SEMVER_PATTERN,
)
from app.core.asset_contracts.schemas import AssetManifestSchemaDTO, ViewportSchemaDTO
from app.core.asset_contracts.validator import (
    ContractValidationError,
    validate_asset_manifest,
    validate_asset_uri,
    validate_node_id,
    validate_semver,
)
from tests.unit.geo_fixture_attrs import geo_node_attrs


def test_asset_uri_pattern_valid():
    assert validate_asset_uri("studyos://assets/geography/turkey_admin/v1")
    assert validate_asset_uri("studyos://assets/medicine/human_heart/v2")
    assert validate_asset_uri("studyos://assets/biology/plant_cell/inst_school_123")


def test_asset_uri_pattern_invalid():
    assert not validate_asset_uri("http://assets/geography/turkey")
    assert not validate_asset_uri("studyos://geography/turkey")
    assert not validate_asset_uri("studyos://assets/Geography/Turkey/v1")  # uppercase not allowed


def test_node_id_pattern_valid():
    assert validate_node_id("turkey_admin_v1::province::konya")
    assert validate_node_id("human_heart_v1::chamber::left_ventricle")
    assert validate_node_id("plant_cell_v1::organelle::mitochondrion")


def test_node_id_pattern_invalid():
    assert not validate_node_id("konya")
    assert not validate_node_id("turkey::konya")
    assert not validate_node_id("turkey_admin_v1:province:konya")
    assert not validate_node_id("turkey_admin_v1::PROVINCE::KONYA")  # uppercase not allowed


def test_semver_pattern():
    assert validate_semver("1.0.0")
    assert validate_semver("v1.2.3")
    assert validate_semver("2.0.0-rc1")
    assert not validate_semver("1.0")
    assert not validate_semver("v1")


def test_valid_manifest_dto():
    payload = {
        "schema_version": "1.0",
        "asset_id": "studyos://assets/geography/turkey_admin/v1",
        "version": "1.2.0",
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
                        "attributes": geo_node_attrs(
                            "province",
                            region_codes=["ic_anadolu"],
                            province_codes=["konya"],
                        ),
                    },
                    {
                        "id": "turkey_admin_v1::province::ankara",
                        "name": {"tr": "Ankara", "en": "Ankara"},
                        "bounding_box": [32.5, 39.0, 33.5, 40.0],
                        "attributes": geo_node_attrs(
                            "province",
                            region_codes=["ic_anadolu"],
                            province_codes=["ankara"],
                        ),
                    },
                ],
            }
        ],
        "tags": ["map", "turkey", "provinces"],
        "license_type": "studyos_core",
    }

    dto = validate_asset_manifest(payload)
    assert isinstance(dto, AssetManifestSchemaDTO)
    assert dto.domain == "geography"
    assert len(dto.layers[0].nodes) == 2


def test_duplicate_node_id_raises_contract_error():
    payload = {
        "schema_version": "1.0",
        "asset_id": "studyos://assets/geography/turkey_admin/v1",
        "version": "1.0.0",
        "domain": "geography",
        "format": "svg",
        "title": {"tr": "Harita"},
        "viewport": {"width": 100.0, "height": 100.0},
        "layers": [
            {
                "id": "layer_1",
                "nodes": [
                    {
                        "id": "turkey_admin_v1::province::konya",
                        "name": {"tr": "Konya"},
                        "bounding_box": [0.0, 0.0, 10.0, 10.0],
                        "attributes": geo_node_attrs("province"),
                    },
                    {
                        "id": "turkey_admin_v1::province::konya",  # Duplicate!
                        "name": {"tr": "Konya 2"},
                        "bounding_box": [0.0, 0.0, 10.0, 10.0],
                        "attributes": geo_node_attrs("province"),
                    },
                ],
            }
        ],
    }

    with pytest.raises(ContractValidationError) as exc_info:
        validate_asset_manifest(payload)
    assert "Duplicate Node ID" in str(exc_info.value)


def test_invalid_bbox_raises_error():
    with pytest.raises(ValidationError):
        ViewportSchemaDTO(width=-100.0, height=500.0)
