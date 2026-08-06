"""
StudyOS Educational Asset Engine (EAE) — Asset Version Service
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.asset_contracts.schemas import AssetManifestSchemaDTO
from app.core.exceptions import ConflictError, ValidationError
from app.models.educational_asset import (
    EducationalAsset,
    EducationalAssetNode,
    EducationalAssetVersion,
)
from app.repositories.educational_asset_repository import EducationalAssetRepository

if TYPE_CHECKING:
    pass


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parses 'vX.Y.Z' or 'X.Y.Z' into (major, minor, patch)."""
    clean = version.lstrip("v").split("-")[0]
    parts = clean.split(".")
    if len(parts) < 3:
        raise ValidationError(f"Invalid SemVer string '{version}'")
    return int(parts[0]), int(parts[1]), int(parts[2])


class AssetVersionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EducationalAssetRepository(db)

    async def upgrade_asset_version(
        self,
        existing_asset: EducationalAsset,
        new_manifest: AssetManifestSchemaDTO,
        change_log: str | None = None,
        is_breaking: bool = False,
        bundle_payload: bytes | None = None,
    ) -> EducationalAsset:
        """
        Upgrades an asset version enforcing SemVer rules and Node ID breaking change rules.
        """
        old_major, old_minor, old_patch = parse_semver(existing_asset.version)
        new_major, new_minor, new_patch = parse_semver(new_manifest.version)

        if (new_major, new_minor, new_patch) <= (old_major, old_minor, old_patch):
            raise ConflictError(
                f"New version '{new_manifest.version}' must be strictly higher than current version '{existing_asset.version}'"
            )

        # Node ID preservation check for non-breaking upgrades
        existing_node_ids = {n.node_id for n in existing_asset.nodes}
        new_node_ids = {
            node.id for layer in new_manifest.layers for node in layer.nodes
        }

        removed_node_ids = existing_node_ids - new_node_ids
        if removed_node_ids and not is_breaking and new_major == old_major:
            raise ValidationError(
                f"Version upgrade removes existing Node IDs {removed_node_ids} without a Major version bump or is_breaking=True flag."
            )

        # Update Asset Fields
        existing_asset.version = new_manifest.version
        existing_asset.domain = new_manifest.domain
        existing_asset.format = new_manifest.format
        existing_asset.title = new_manifest.title
        existing_asset.viewport = new_manifest.viewport.model_dump()
        existing_asset.tags = new_manifest.tags
        existing_asset.license_type = new_manifest.license_type

        new_nodes: list[EducationalAssetNode] = []
        for layer in new_manifest.layers:
            for node_dto in layer.nodes:
                new_nodes.append(
                    EducationalAssetNode(
                        node_id=node_dto.id,
                        name=node_dto.name,
                        bounding_box=node_dto.bounding_box,
                        attributes={
                            **(node_dto.attributes or {}),
                            "layer_id": layer.id,
                            "z_index": layer.z_index,
                            "min_lod": layer.min_lod,
                        },
                    )
                )

        version_entry = EducationalAssetVersion(
            version=new_manifest.version,
            change_log=change_log or f"Upgraded to version {new_manifest.version}",
            is_breaking=is_breaking or (new_major > old_major),
            bundle_payload=bundle_payload,
        )

        updated = await self.repo.add_version(
            asset=existing_asset,
            version_entry=version_entry,
            new_nodes=new_nodes,
        )
        return updated

    async def deprecate_asset(self, asset_uri: str) -> EducationalAsset:
        asset = await self.repo.get_by_asset_id(asset_uri.strip())
        if asset is None:
            raise ValidationError(f"Asset with URI '{asset_uri}' not found")
        asset.is_deprecated = True
        await self.db.flush()
        return asset
