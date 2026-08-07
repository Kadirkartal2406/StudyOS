"""
StudyOS Educational Asset Engine (EAE) — Asset Registry Service
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.asset_contracts.validator import (
    ContractValidationError,
    validate_asset_manifest,
)
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.educational_asset import (
    EducationalAsset,
    EducationalAssetNode,
    EducationalAssetVersion,
)
from app.repositories.educational_asset_repository import EducationalAssetRepository
from app.services.asset_compiler.pipeline import AssetCompilerPipeline
from app.services.asset_version_service import AssetVersionService


class AssetRegistryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EducationalAssetRepository(db)
        self.version_service = AssetVersionService(db)
        self.compiler = AssetCompilerPipeline()

    async def compile_and_register_asset(
        self,
        raw_svg: str,
        raw_manifest: dict[str, Any],
        change_log: str | None = None,
        is_breaking: bool = False,
    ) -> tuple[EducationalAsset, bytes]:
        """
        Runs full 12-step compiler pipeline and registers asset + bundle hash.
        """
        pipeline_result = self.compiler.execute(raw_svg=raw_svg, raw_manifest=raw_manifest)
        manifest_dto = pipeline_result.manifest

        existing = await self.repo.get_by_asset_id(manifest_dto.asset_id)

        if existing is not None:
            updated = await self.version_service.upgrade_asset_version(
                existing_asset=existing,
                new_manifest=manifest_dto,
                change_log=change_log,
                is_breaking=is_breaking,
                bundle_payload=pipeline_result.bundle.binary_payload,
            )
            updated.bundle_hash_sha256 = pipeline_result.bundle.hash_sha256
            updated.bundle_size_bytes = pipeline_result.bundle.compressed_size_bytes
            await self.db.flush()
            return updated, pipeline_result.bundle.binary_payload

        # New Asset
        asset = EducationalAsset(
            asset_id=manifest_dto.asset_id,
            version=manifest_dto.version,
            domain=manifest_dto.domain,
            format=manifest_dto.format,
            title=manifest_dto.title,
            viewport=manifest_dto.viewport.model_dump(),
            tags=manifest_dto.tags,
            license_type=manifest_dto.license_type,
            tenant_id=uuid.UUID(manifest_dto.tenant_id) if manifest_dto.tenant_id else None,
            bundle_hash_sha256=pipeline_result.bundle.hash_sha256,
            bundle_size_bytes=pipeline_result.bundle.compressed_size_bytes,
        )

        nodes: list[EducationalAssetNode] = []
        for layer in manifest_dto.layers:
            for node_dto in layer.nodes:
                nodes.append(
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
                        educational_metadata=node_dto.educational_metadata.model_dump() if node_dto.educational_metadata else None,
                    )
                )

        version_entry = EducationalAssetVersion(
            version=manifest_dto.version,
            change_log=change_log or "Initial asset registration with compiled bundle",
            is_breaking=is_breaking,
            bundle_payload=pipeline_result.bundle.binary_payload,
        )

        created = await self.repo.create_asset(asset=asset, nodes=nodes, version_entry=version_entry)
        return created, pipeline_result.bundle.binary_payload

    async def register_asset_manifest(
        self,
        raw_manifest: dict[str, Any],
        change_log: str | None = None,
        is_breaking: bool = False,
    ) -> EducationalAsset:
        """
        Validates raw manifest and registers a new Asset or a new Version if asset exists.
        Enforces SemVer and Node ID contracts.
        """
        manifest_dto = validate_asset_manifest(raw_manifest)
        existing = await self.repo.get_by_asset_id(manifest_dto.asset_id)

        if existing is not None:
            # Updating an existing asset with a new version
            return await self.version_service.upgrade_asset_version(
                existing_asset=existing,
                new_manifest=manifest_dto,
                change_log=change_log,
                is_breaking=is_breaking,
            )

        # New Asset registration
        asset = EducationalAsset(
            asset_id=manifest_dto.asset_id,
            version=manifest_dto.version,
            domain=manifest_dto.domain,
            format=manifest_dto.format,
            title=manifest_dto.title,
            viewport=manifest_dto.viewport.model_dump(),
            tags=manifest_dto.tags,
            license_type=manifest_dto.license_type,
            tenant_id=uuid.UUID(manifest_dto.tenant_id)
            if manifest_dto.tenant_id
            else None,
        )

        nodes: list[EducationalAssetNode] = []
        for layer in manifest_dto.layers:
            for node_dto in layer.nodes:
                nodes.append(
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
                        educational_metadata=node_dto.educational_metadata.model_dump() if node_dto.educational_metadata else None,
                    )
                )

        version_entry = EducationalAssetVersion(
            version=manifest_dto.version,
            change_log=change_log or "Initial asset registration",
            is_breaking=is_breaking,
        )

        created = await self.repo.create_asset(
            asset=asset, nodes=nodes, version_entry=version_entry
        )
        return created

    async def get_asset_by_id(self, asset_db_id: uuid.UUID) -> EducationalAsset:
        asset = await self.repo.get_by_id(asset_db_id)
        if asset is None:
            raise NotFoundError(f"Asset with ID '{asset_db_id}' not found")
        return asset

    async def get_asset_by_uri(self, asset_uri: str) -> EducationalAsset:
        asset = await self.repo.get_by_asset_id(asset_uri.strip())
        if asset is None:
            raise NotFoundError(f"Asset with URI '{asset_uri}' not found")
        return asset

