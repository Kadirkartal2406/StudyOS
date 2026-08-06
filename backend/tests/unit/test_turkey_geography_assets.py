"""Sprint 8 — Turkey geography ontology, builder, and confusable distractors."""

from __future__ import annotations

from app.core.asset_contracts.constants import TURKEY_GEOGRAPHY_PACKAGES
from app.core.asset_contracts.validator import validate_asset_manifest
from app.services.geography.turkey_catalog import (
    CONFUSABLE_PAIRS,
    PROVINCES,
    build_all_package_specs,
    confusable_map,
)
from app.services.question_author.confusable_distractors import pick_confusable_distractors


def test_turkey_has_81_provinces():
    assert len(PROVINCES) == 81
    slugs = [p[0] for p in PROVINCES]
    assert len(set(slugs)) == 81
    assert "konya" in slugs
    assert "rize" in slugs


def test_confusable_pairs_are_bidirectional():
    cmap = confusable_map()
    for a, b in CONFUSABLE_PAIRS:
        assert b in cmap[a]
        assert a in cmap[b]


def test_build_all_twelve_packages_validate():
    packages = build_all_package_specs()
    assert len(packages) == len(TURKEY_GEOGRAPHY_PACKAGES)
    names = {p["uri_name"] for p in packages}
    assert names == set(TURKEY_GEOGRAPHY_PACKAGES)
    for pkg in packages:
        dto = validate_asset_manifest(pkg["manifest"])
        assert dto.domain == "geography"
        assert "<svg" in pkg["svg"]
        assert sum(len(layer.nodes) for layer in dto.layers) >= 1


def test_pick_confusable_distractors_prefers_attributes():
    correct = "turkey_hydro_v1::river::kizilirmak"
    distractors = pick_confusable_distractors(
        correct,
        node_attributes={
            "layer_type": "river",
            "confusable_with": [
                "turkey_hydro_v1::river::sakarya",
                "turkey_hydro_v1::river::yesilirmak",
            ],
        },
        limit=2,
    )
    assert distractors == [
        "turkey_hydro_v1::river::sakarya",
        "turkey_hydro_v1::river::yesilirmak",
    ]


def test_node_ids_unique_across_all_packages():
    seen: set[str] = set()
    for pkg in build_all_package_specs():
        for layer in pkg["manifest"]["layers"]:
            for node in layer["nodes"]:
                assert node["id"] not in seen
                seen.add(node["id"])
    assert len(seen) > 100


def test_built_packages_on_disk_smoke():
    """End-to-end smoke: 12 built packages exist and validate."""
    import json

    from app.services.geography.turkey_catalog import DATA_ROOT

    built = DATA_ROOT / "built"
    assert built.exists(), "Run scripts/geography/build_turkey_assets.py first"
    dirs = sorted(p for p in built.iterdir() if p.is_dir())
    assert len(dirs) == len(TURKEY_GEOGRAPHY_PACKAGES)
    names = {p.name for p in dirs}
    assert names == set(TURKEY_GEOGRAPHY_PACKAGES)
    for pkg_dir in dirs:
        manifest = json.loads((pkg_dir / "manifest.json").read_text(encoding="utf-8"))
        svg = (pkg_dir / "asset.svg").read_text(encoding="utf-8")
        dto = validate_asset_manifest(manifest)
        assert dto.domain == "geography"
        assert "<svg" in svg
        assert sum(len(layer.nodes) for layer in dto.layers) >= 1


def test_provinces_visible_at_default_scale():
    """Provinces layer min_lod must be <= 1.0 so they appear without zooming."""
    packages = build_all_package_specs()
    admin = next(p for p in packages if p["uri_name"] == "turkey_admin")
    province_layer = next(
        (lay for lay in admin["manifest"]["layers"] if lay["id"] == "provinces"),
        None,
    )
    assert province_layer is not None, "provinces layer missing"
    assert province_layer["min_lod"] <= 1.0, (
        f"provinces min_lod={province_layer['min_lod']} > 1.0: provinces hidden at default zoom"
    )


def test_province_paths_are_real_polygons():
    """Province SVG paths should have >5 vertices (real polygons, not rectangles)."""
    import re

    packages = build_all_package_specs()
    admin = next(p for p in packages if p["uri_name"] == "turkey_admin")
    svg = admin["svg"]

    # Extract province path `d` attributes
    province_matches = re.findall(
        r'<path id="turkey_admin_v1::province::[^"]+" d="([^"]+)"', svg
    )
    assert len(province_matches) == 81, f"Expected 81 province paths, got {len(province_matches)}"

    polygon_count = 0
    for path_d in province_matches:
        point_tokens = re.findall(r"[ML][-\d.]+\s+[-\d.]+", path_d)
        if len(point_tokens) > 5:
            polygon_count += 1

    # At least 75 of 81 provinces should have real polygon shapes (>5 vertices)
    assert polygon_count >= 75, (
        f"Only {polygon_count}/81 provinces have polygon paths (>5 vertices). "
        "GeoJSON data may not be loaded correctly."
    )
