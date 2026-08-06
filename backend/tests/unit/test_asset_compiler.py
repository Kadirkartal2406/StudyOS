"""
Unit tests for EAE Asset Compiler Pipeline, Sanitizer, Spatial Builder, and Packager.
"""

import pytest
from app.core.asset_contracts.validator import ContractValidationError
from app.services.asset_compiler.packager import BundlePackager
from app.services.asset_compiler.pipeline import AssetCompilerPipeline
from app.services.asset_compiler.sanitizer import SVGSanitizer
from app.services.asset_compiler.spatial import SpatialIndexBuilder
from tests.unit.geo_fixture_attrs import geo_node_attrs


@pytest.fixture
def valid_svg():
    return """<svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg">
        <g id="provinces">
            <path id="turkey_admin_v1::province::konya" d="M30 40 L50 60 Z"/>
        </g>
    </svg>"""


@pytest.fixture
def dangerous_svg():
    return """<svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg">
        <script>alert('XSS Attack!');</script>
        <g id="provinces" onclick="javascript:stealCookies()">
            <path id="turkey_admin_v1::province::konya" d="M30 40 L50 60 Z"/>
        </g>
    </svg>"""


@pytest.fixture
def sample_manifest():
    return {
        "schema_version": "1.0",
        "asset_id": "studyos://assets/geography/turkey_admin/v1",
        "version": "1.0.0",
        "domain": "geography",
        "format": "svg",
        "title": {"tr": "Türkiye İdari Haritası"},
        "viewport": {"width": 1000.0, "height": 500.0},
        "layers": [
            {
                "id": "provinces",
                "nodes": [
                    {
                        "id": "turkey_admin_v1::province::konya",
                        "name": {"tr": "Konya"},
                        "bounding_box": [30.0, 40.0, 50.0, 60.0],
                        "attributes": geo_node_attrs("province"),
                    }
                ],
            }
        ],
    }


def test_svg_sanitizer_removes_dangerous_tags_and_events(dangerous_svg):
    sanitizer = SVGSanitizer()
    clean_svg = sanitizer.sanitize(dangerous_svg)

    assert "<script>" not in clean_svg
    assert "alert(" not in clean_svg
    assert "onclick=" not in clean_svg
    assert "javascript:" not in clean_svg
    assert "turkey_admin_v1::province::konya" in clean_svg


def test_spatial_builder_bounding_box_and_tree():
    builder = SpatialIndexBuilder()
    bbox = builder.compute_bounding_box([(10.0, 20.0), (30.0, 40.0), (5.0, 50.0)])
    assert bbox == [5.0, 20.0, 30.0, 50.0]

    tree = builder.build_spatial_tree(
        [{"id": "node_1", "bounding_box": [0.0, 0.0, 10.0, 10.0]}]
    )
    assert tree["count"] == 1
    assert tree["root"]["type"] == "node"
    assert builder.query_bbox(tree, (5.0, 5.0)) == ["node_1"]
    assert builder.query_bbox(tree, (20.0, 20.0)) == []


def test_bundle_packager_compress_and_unpack(sample_manifest):
    packager = BundlePackager()
    bundle = packager.package(
        manifest_dto=sample_manifest,
        sanitized_svg="<svg></svg>",
        spatial_tree={"root": {}},
    )

    assert len(bundle.binary_payload) > 0
    assert len(bundle.hash_sha256) == 64
    assert bundle.compressed_size_bytes < bundle.size_bytes

    unpacked = packager.unpack(bundle.binary_payload)
    assert unpacked["svg_content"] == "<svg></svg>"


def test_full_12_step_compiler_pipeline(valid_svg, sample_manifest):
    pipeline = AssetCompilerPipeline()
    result = pipeline.execute(raw_svg=valid_svg, raw_manifest=sample_manifest)

    assert result.pipeline_steps_completed == 12
    assert result.manifest.asset_id == "studyos://assets/geography/turkey_admin/v1"
    assert "<svg" in result.sanitized_svg
    assert len(result.bundle.hash_sha256) == 64
