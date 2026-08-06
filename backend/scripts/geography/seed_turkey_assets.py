"""Compile and register all Turkey geography packages into the database."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.base import AsyncSessionLocal  # noqa: E402
from app.services.asset_registry_service import AssetRegistryService  # noqa: E402
from app.services.geography.turkey_catalog import DATA_ROOT  # noqa: E402


async def _bump_version(version: str) -> str:
    """Bump patch number: 1.0.0 -> 1.0.1, 1.0.1 -> 1.0.2, etc."""
    parts = version.split(".")
    if len(parts) == 3:
        try:
            parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)
        except ValueError:
            pass
    return version + ".1"


async def seed() -> None:
    built = DATA_ROOT / "built"
    if not built.exists():
        raise SystemExit("Run build_turkey_assets.py first")

    async with AsyncSessionLocal() as db:
        svc = AssetRegistryService(db)
        for pkg_dir in sorted(built.iterdir()):
            if not pkg_dir.is_dir():
                continue
            manifest = json.loads((pkg_dir / "manifest.json").read_text(encoding="utf-8"))
            svg = (pkg_dir / "asset.svg").read_text(encoding="utf-8")

            # If asset already exists, bump patch version to pass the SemVer conflict check
            existing = None
            try:
                existing = await svc.get_asset_by_uri(manifest["asset_id"])
            except Exception:
                pass
            if existing is not None:
                manifest["version"] = await _bump_version(existing.version)

            asset, _bundle = await svc.compile_and_register_asset(
                raw_svg=svg,
                raw_manifest=manifest,
                change_log="Sprint 8 Turkey geography production seed — real GeoJSON polygons, LOD fix",
                is_breaking=False,
            )
            await db.commit()
            print(f"Registered {asset.asset_id} v{asset.version} id={asset.id}")


def main() -> int:
    asyncio.run(seed())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
