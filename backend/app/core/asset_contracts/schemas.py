"""
StudyOS Educational Asset Engine (EAE) — Pydantic Validation Schemas
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.asset_contracts.constants import (
    ALLOWED_DOMAINS,
    ASSET_URI_PATTERN,
    NODE_ID_PATTERN,
    SEMVER_PATTERN,
    SUPPORTED_ASSET_FORMATS,
)


class ViewportSchemaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width: float = Field(..., gt=0, description="Canvas viewport width in points")
    height: float = Field(..., gt=0, description="Canvas viewport height in points")
    default_scale: float = Field(1.0, gt=0, le=20.0, description="Default rendering scale")
    max_scale: float = Field(8.0, gt=1.0, le=50.0, description="Maximum zoom scale")


class AssetNodeSchemaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique node ID matching pattern <asset>::<type>::<name>")
    name: dict[str, str] = Field(..., description="Localized display names e.g. {'tr': 'Konya', 'en': 'Konya'}")
    bounding_box: list[float] = Field(..., min_length=4, max_length=4, description="[min_x, min_y, max_x, max_y]")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Domain-specific pedagogical metadata")

    @field_validator("id")
    @classmethod
    def _validate_node_id(cls, v: str) -> str:
        if not NODE_ID_PATTERN.match(v):
            raise ValueError(
                f"Invalid Node ID format '{v}'. Must match pattern '<asset>::<layer_type>::<component_identifier>'"
            )
        return v

    @field_validator("bounding_box")
    @classmethod
    def _validate_bbox(cls, v: list[float]) -> list[float]:
        min_x, min_y, max_x, max_y = v
        if max_x < min_x or max_y < min_y:
            raise ValueError(f"Invalid bounding box {v}: max values must be >= min values")
        return v


class AssetLayerSchemaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=100, description="Unique layer identifier")
    z_index: int = Field(0, ge=0, le=1000, description="Render Z-index order")
    min_lod: float = Field(1.0, ge=0.1, le=50.0, description="Minimum LOD scale factor for layer rendering")
    nodes: list[AssetNodeSchemaDTO] = Field(default_factory=list, description="Child nodes in layer")


class AssetManifestSchemaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field("1.0", description="EAE Manifest schema spec version")
    asset_id: str = Field(..., description="Asset URI e.g. studyos://assets/geography/turkey_admin/v1")
    version: str = Field(..., description="SemVer string e.g. 1.2.0")
    domain: str = Field(..., description="Educational domain namespace")
    format: str = Field("svg", description="Source visual vector/mesh format")
    title: dict[str, str] = Field(..., description="Localized asset title")
    viewport: ViewportSchemaDTO = Field(..., description="Viewport bounds and scale settings")
    layers: list[AssetLayerSchemaDTO] = Field(..., min_length=1, description="Layer hierarchy")
    tags: list[str] = Field(default_factory=list, description="Search and catalog indexing tags")
    license_type: str = Field("studyos_core", description="Licensing tier")
    tenant_id: str | None = Field(None, description="Optional tenant UUID for institutional isolation")

    @field_validator("asset_id")
    @classmethod
    def _validate_asset_uri(cls, v: str) -> str:
        if not ASSET_URI_PATTERN.match(v):
            raise ValueError(f"Invalid asset URI '{v}'. Must match 'studyos://assets/<domain>/<name>/v<major>'")
        return v

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        if not SEMVER_PATTERN.match(v):
            raise ValueError(f"Invalid SemVer string '{v}'. Must match 'vX.Y.Z'")
        return v

    @field_validator("domain")
    @classmethod
    def _validate_domain(cls, v: str) -> str:
        d = v.lower().strip()
        if d not in ALLOWED_DOMAINS:
            raise ValueError(f"Domain '{v}' is not in allowed domains: {ALLOWED_DOMAINS}")
        return d

    @field_validator("format")
    @classmethod
    def _validate_format(cls, v: str) -> str:
        fmt = v.lower().strip()
        if fmt not in SUPPORTED_ASSET_FORMATS:
            raise ValueError(f"Format '{v}' is not in supported formats: {SUPPORTED_ASSET_FORMATS}")
        return fmt


class AssetGroundingSchemaDTO(BaseModel):
    """Schema representation passed to AI Prompters (LLM Context Builder)."""
    model_config = ConfigDict(extra="forbid")

    asset_id: str
    version: str
    domain: str
    available_node_ids: list[str]
    taxonomy_summary: list[dict[str, Any]]
