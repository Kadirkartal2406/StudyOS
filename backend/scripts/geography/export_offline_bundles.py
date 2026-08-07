"""
StudyOS Script — Export EAE offline bundles
Compiles the 12 geography packages and saves them directly to the Flutter assets directory.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.geography.turkey_catalog import build_all_package_specs
from app.services.asset_compiler.packager import BundlePackager
from app.core.asset_contracts.schemas import AssetManifestSchemaDTO

# Placeholder rect-only bundles were ~1–3 KB. Real province geometry is tens of KB.
MIN_REALISTIC_BYTES = 10_000


def export_offline_bundles() -> None:
    packager = BundlePackager()
    specs = build_all_package_specs()

    mobile_assets_dir = backend_dir.parent / "mobile" / "assets" / "geography"
    mobile_assets_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting {len(specs)} geography packages to {mobile_assets_dir}...")

    too_small: list[str] = []
    for spec in specs:
        manifest_dict = spec["manifest"]
        svg_content = spec["svg"]
        uri_name = spec["uri_name"]

        manifest_dto = AssetManifestSchemaDTO(**manifest_dict)
        spatial_tree: dict = {}

        bundle = packager.package(
            manifest_dto=manifest_dto,
            sanitized_svg=svg_content,
            spatial_tree=spatial_tree,
        )

        file_path = mobile_assets_dir / f"{uri_name}.eae"
        file_path.write_bytes(bundle.binary_payload)
        size = bundle.compressed_size_bytes
        flag = "OK" if size >= MIN_REALISTIC_BYTES else "TOO_SMALL"
        print(f"  {flag} {uri_name}.eae ({size} bytes, svg={len(svg_content)} chars)")
        if size < MIN_REALISTIC_BYTES:
            too_small.append(f"{uri_name}={size}")

    if too_small:
        raise SystemExit(
            "Export produced placeholder-sized bundles (expected >= "
            f"{MIN_REALISTIC_BYTES} bytes): {', '.join(too_small)}"
        )

    print("Done!")


if __name__ == "__main__":
    export_offline_bundles()
