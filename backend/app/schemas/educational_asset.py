"""
StudyOS Educational Asset Engine (EAE) — API Schemas & DTOs
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.asset_contracts.schemas import ViewportSchemaDTO


class AssetSearchQueryDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str | None = Field(default=None, description="Free text search query for title, tags, or nodes")
    domain: str | None = Field(default=None, description="Filter by domain namespace e.g. geography")
    tag: str | None = Field(default=None, description="Filter by tag")
    include_deprecated: bool = Field(default=False, description="Include deprecated asset versions")
    tenant_id: uuid.UUID | None = Field(default=None, description="Filter by institutional tenant ID")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AssetListItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: str
    version: str
    domain: str
    format: str
    title: dict[str, str]
    tags: list[str]
    license_type: str
    is_deprecated: bool
    created_at: datetime
    viewport: dict[str, Any] | None = None


class AssetNodeDetailDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = None
    node_id: str | None = None
    # Flutter contract uses `id` for node identity inside layers
    name: dict[str, str]
    bounding_box: list[float]
    attributes: dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        return None


class AssetLayerDetailDTO(BaseModel):
    id: str
    z_index: int = 0
    min_lod: float = 1.0
    nodes: list[dict[str, Any]] = Field(default_factory=list)


class AssetDetailDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: str
    version: str
    domain: str
    format: str
    title: dict[str, str]
    viewport: ViewportSchemaDTO | dict[str, Any]
    tags: list[str]
    license_type: str
    tenant_id: uuid.UUID | None
    is_deprecated: bool
    bundle_hash_sha256: str | None
    bundle_size_bytes: int | None
    created_at: datetime
    updated_at: datetime
    schema_version: str = "1.0"
    nodes: list[AssetNodeDetailDTO] = Field(default_factory=list)
    layers: list[AssetLayerDetailDTO] = Field(default_factory=list)


class AssetVersionItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: str
    change_log: str | None
    is_breaking: bool
    created_at: datetime


class AssetCreateRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest: dict[str, Any] = Field(..., description="Full EAE asset manifest payload")
    change_log: str | None = Field(default=None, description="Version change log description")
    is_breaking: bool = Field(default=False, description="Flag if major breaking changes exist")


class AssetNodeUpdateRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: dict[str, str] | None = None
    attributes: dict[str, Any] | None = None
    bounding_box: list[float] | None = None


def build_asset_detail_dto(asset: Any, *, svg_manifest: dict[str, Any] | None = None) -> AssetDetailDTO:
    """Serialize ORM asset into Flutter-compatible detail with layers[]."""
    flat_nodes = [
        AssetNodeDetailDTO(
            id=n.id,
            node_id=n.node_id,
            name=n.name,
            bounding_box=n.bounding_box,
            attributes=n.attributes or {},
        )
        for n in (asset.nodes or [])
    ]

    layers: list[AssetLayerDetailDTO] = []
    if svg_manifest and isinstance(svg_manifest.get("layers"), list):
        for layer in svg_manifest["layers"]:
            layer_nodes = []
            for node in layer.get("nodes") or []:
                layer_nodes.append(
                    {
                        "id": node.get("id") or node.get("node_id"),
                        "name": node.get("name") or {},
                        "bounding_box": node.get("bounding_box") or [0, 0, 0, 0],
                        "attributes": node.get("attributes") or {},
                    }
                )
            layers.append(
                AssetLayerDetailDTO(
                    id=str(layer.get("id") or "layer"),
                    z_index=int(layer.get("z_index") or 0),
                    min_lod=float(layer.get("min_lod") or 1.0),
                    nodes=layer_nodes,
                )
            )
    else:
        # Reconstruct from node attributes
        grouped: dict[str, AssetLayerDetailDTO] = {}
        for n in asset.nodes or []:
            attrs = n.attributes or {}
            layer_id = str(attrs.get("layer_id") or attrs.get("layer_type") or "default")
            if layer_id not in grouped:
                grouped[layer_id] = AssetLayerDetailDTO(
                    id=layer_id,
                    z_index=int(attrs.get("z_index") or 0),
                    min_lod=float(attrs.get("min_lod") or 1.0),
                    nodes=[],
                )
            grouped[layer_id].nodes.append(
                {
                    "id": n.node_id,
                    "name": n.name,
                    "bounding_box": n.bounding_box,
                    "attributes": attrs,
                }
            )
        layers = list(grouped.values())

    viewport = asset.viewport
    if svg_manifest and svg_manifest.get("viewport"):
        viewport = svg_manifest["viewport"]

    return AssetDetailDTO(
        id=asset.id,
        asset_id=asset.asset_id,
        version=asset.version,
        domain=asset.domain,
        format=asset.format,
        title=asset.title,
        viewport=viewport,
        tags=asset.tags or [],
        license_type=asset.license_type,
        tenant_id=asset.tenant_id,
        is_deprecated=asset.is_deprecated,
        bundle_hash_sha256=asset.bundle_hash_sha256,
        bundle_size_bytes=asset.bundle_size_bytes,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        schema_version=(svg_manifest or {}).get("schema_version", "1.0"),
        nodes=flat_nodes,
        layers=layers,
    )
