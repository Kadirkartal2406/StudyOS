"""
StudyOS Educational Asset Engine (EAE) — Contract Validator
"""

from __future__ import annotations

from typing import Any
from pydantic import ValidationError

from app.core.asset_contracts.constants import (
    ASSET_URI_PATTERN,
    GEOGRAPHY_LAYER_TYPES,
    GEOGRAPHY_REQUIRED_ATTRIBUTE_KEYS,
    NODE_ID_PATTERN,
    SEMVER_PATTERN,
)
from app.core.asset_contracts.schemas import AssetManifestSchemaDTO


class ContractValidationError(ValueError):
    """Raised when an asset manifest or node contract validation fails."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors or []


def validate_asset_uri(uri: str) -> bool:
    """Validates if a given URI matches the studyos://assets/ namespace pattern."""
    return bool(ASSET_URI_PATTERN.match((uri or "").strip()))


def validate_node_id(node_id: str) -> bool:
    """Validates if a node ID matches the <asset>::<type>::<name> pattern."""
    return bool(NODE_ID_PATTERN.match((node_id or "").strip()))


def validate_semver(version: str) -> bool:
    """Validates if a string is a valid SemVer format."""
    return bool(SEMVER_PATTERN.match((version or "").strip()))


def validate_asset_manifest(raw_manifest: dict[str, Any]) -> AssetManifestSchemaDTO:
    """
    Validates a raw dictionary against the EAE Asset Manifest Pydantic Schema.
    Also verifies uniqueness of all Node IDs across layers.
    """
    try:
        dto = AssetManifestSchemaDTO.model_validate(raw_manifest)
    except ValidationError as exc:
        raise ContractValidationError(
            f"Asset manifest schema validation failed with {exc.error_count()} errors",
            errors=exc.errors(include_url=False),
        ) from exc

    # Cross-layer Node ID uniqueness validation
    seen_nodes: set[str] = set()
    for layer in dto.layers:
        for node in layer.nodes:
            if node.id in seen_nodes:
                raise ContractValidationError(
                    f"Duplicate Node ID '{node.id}' found in layer '{layer.id}'. Node IDs must be unique across manifest."
                )
            seen_nodes.add(node.id)

    if dto.domain == "geography":
        _validate_geography_nodes(dto)

    return dto


def _validate_geography_nodes(dto: AssetManifestSchemaDTO) -> None:
    """Enforce geography-specific layer_type allowlist and required attributes."""
    for layer in dto.layers:
        for node in layer.nodes:
            parts = node.id.split("::")
            layer_type = parts[1] if len(parts) == 3 else ""
            if layer_type not in GEOGRAPHY_LAYER_TYPES:
                raise ContractValidationError(
                    f"Geography node '{node.id}' uses unknown layer_type '{layer_type}'. "
                    f"Allowed: {sorted(GEOGRAPHY_LAYER_TYPES)}"
                )

            attrs = node.attributes or {}
            missing = GEOGRAPHY_REQUIRED_ATTRIBUTE_KEYS - set(attrs.keys())
            if missing:
                raise ContractValidationError(
                    f"Geography node '{node.id}' missing required attributes: {sorted(missing)}"
                )

            if attrs.get("layer_type") != layer_type:
                raise ContractValidationError(
                    f"Geography node '{node.id}' attributes.layer_type must equal '{layer_type}'"
                )

            for key in ("confusable_with", "qie_aliases", "evidence_topic_hints"):
                val = attrs.get(key)
                if not isinstance(val, list):
                    raise ContractValidationError(
                        f"Geography node '{node.id}' attribute '{key}' must be a list"
                    )

            region_codes = attrs.get("region_codes")
            if region_codes is not None and not isinstance(region_codes, list):
                raise ContractValidationError(
                    f"Geography node '{node.id}' attribute 'region_codes' must be a list when present"
                )
            province_codes = attrs.get("province_codes")
            if province_codes is not None and not isinstance(province_codes, list):
                raise ContractValidationError(
                    f"Geography node '{node.id}' attribute 'province_codes' must be a list when present"
                )
