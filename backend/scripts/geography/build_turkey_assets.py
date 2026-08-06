"""Build all 12 Turkey geography EAE packages into data/geography/turkey/built/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.asset_contracts.validator import validate_asset_manifest  # noqa: E402
from app.services.geography.turkey_catalog import (  # noqa: E402
    DATA_ROOT,
    build_all_package_specs,
    write_ontology_files,
)


def main() -> int:
    write_ontology_files(DATA_ROOT)
    built = DATA_ROOT / "built"
    built.mkdir(parents=True, exist_ok=True)

    packages = build_all_package_specs()
    for pkg in packages:
        name = pkg["uri_name"]
        out = built / name
        out.mkdir(parents=True, exist_ok=True)
        manifest = pkg["manifest"]
        validate_asset_manifest(manifest)
        (out / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out / "asset.svg").write_text(pkg["svg"], encoding="utf-8")
        node_count = sum(len(layer["nodes"]) for layer in manifest["layers"])
        print(f"OK {name}: {node_count} nodes -> {out}")

    print(f"Built {len(packages)} packages under {built}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
