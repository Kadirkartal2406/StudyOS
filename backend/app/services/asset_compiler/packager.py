"""
StudyOS Educational Asset Engine (EAE) — Bundle Packager
Serializes manifest + spatial index + sanitized SVG into compressed binary payload.
"""

from __future__ import annotations

import hashlib
import json
import zlib
from dataclasses import dataclass
from typing import Any


@dataclass
class CompiledBundle:
    binary_payload: bytes
    hash_sha256: str
    size_bytes: int
    compressed_size_bytes: int


class BundlePackager:
    """
    Packages EAE Asset Manifest and SVG geometry into an optimized compressed binary stream.
    """

    def package(
        self,
        manifest_dto: Any,
        sanitized_svg: str,
        spatial_tree: dict[str, Any],
    ) -> CompiledBundle:
        payload_dict = {
            "manifest": manifest_dto.model_dump()
            if hasattr(manifest_dto, "model_dump")
            else manifest_dto,
            "svg_content": sanitized_svg,
            "spatial_tree": spatial_tree,
        }

        # 1. Serialize to UTF-8 JSON bytes
        json_bytes = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
        uncompressed_size = len(json_bytes)

        # 2. Compress using zlib/deflate level 9 (standard lossless compression across Python & Flutter)
        compressed = zlib.compress(json_bytes, level=9)
        compressed_size = len(compressed)

        # 3. Compute SHA-256 Hash
        hash_sha256 = hashlib.sha256(compressed).hexdigest()

        return CompiledBundle(
            binary_payload=compressed,
            hash_sha256=hash_sha256,
            size_bytes=uncompressed_size,
            compressed_size_bytes=compressed_size,
        )

    def unpack(self, compressed_payload: bytes) -> dict[str, Any]:
        """Decompresses and deserializes binary bundle back into dictionary representation."""
        decompressed = zlib.decompress(compressed_payload)
        return json.loads(decompressed.decode("utf-8"))
