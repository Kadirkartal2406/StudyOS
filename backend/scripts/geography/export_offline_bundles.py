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

def export_offline_bundles():
    packager = BundlePackager()
    specs = build_all_package_specs()
    
    # Target directory in the mobile app
    mobile_assets_dir = backend_dir.parent / "mobile" / "assets" / "geography"
    mobile_assets_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting {len(specs)} geography packages to {mobile_assets_dir}...")
    
    for spec in specs:
        manifest_dict = spec["manifest"]
        svg_content = spec["svg"]
        uri_name = spec["uri_name"] # e.g. "turkey_admin"
        
        # Convert dictionary to DTO for the packager
        manifest_dto = AssetManifestSchemaDTO(**manifest_dict)
        
        # Empty spatial tree for now since the mobile app hit-tests the paths directly
        spatial_tree = {}
        
        bundle = packager.package(
            manifest_dto=manifest_dto,
            sanitized_svg=svg_content,
            spatial_tree=spatial_tree
        )
        
        file_path = mobile_assets_dir / f"{uri_name}.eae"
        file_path.write_bytes(bundle.binary_payload)
        
        print(f"  OK {uri_name}.eae ({bundle.compressed_size_bytes} bytes)")
        
    print("Done!")

if __name__ == "__main__":
    export_offline_bundles()
