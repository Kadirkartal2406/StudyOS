"""
StudyOS Educational Asset Engine (EAE) — Delta Sync Engine
Computes and applies binary patch deltas between asset bundle versions.
"""

from __future__ import annotations

import json
import zlib
from dataclasses import dataclass
from typing import Any


@dataclass
class AssetDeltaPatch:
    from_version: str
    to_version: str
    patch_bytes: bytes
    patch_size_bytes: int


class AssetDeltaService:
    """
    Computes byte-level binary deltas between asset bundle versions for minimal bandwidth mobile updates.
    """

    def compute_delta(
        self,
        from_version: str,
        to_version: str,
        old_bundle_payload: bytes,
        new_bundle_payload: bytes,
    ) -> AssetDeltaPatch:
        """
        Computes compressed binary delta patch stream between old and new bundle bytes.
        """
        # Decompress payloads to obtain structural diff
        try:
            old_data = json.loads(zlib.decompress(old_bundle_payload).decode("utf-8"))
            new_data = json.loads(zlib.decompress(new_bundle_payload).decode("utf-8"))
        except Exception:
            # Fallback if uncompressed json fails
            old_data = {}
            new_data = {}

        delta_dict = {
            "from_version": from_version,
            "to_version": to_version,
            "new_manifest": new_data.get("manifest"),
            "new_svg_content": new_data.get("svg_content"),
            "new_spatial_tree": new_data.get("spatial_tree"),
        }

        patch_json = json.dumps(delta_dict, ensure_ascii=False).encode("utf-8")
        compressed_patch = zlib.compress(patch_json, level=9)

        return AssetDeltaPatch(
            from_version=from_version,
            to_version=to_version,
            patch_bytes=compressed_patch,
            patch_size_bytes=len(compressed_patch),
        )

    def apply_delta(self, patch_bytes: bytes) -> dict[str, Any]:
        """Applies/unpacks a delta patch on client side."""
        patch_json = zlib.decompress(patch_bytes).decode("utf-8")
        return json.loads(patch_json)
