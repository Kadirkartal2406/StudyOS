"""Shared helpers for EAE geography attribute fixtures."""

from __future__ import annotations

from typing import Any


def geo_node_attrs(
    layer_type: str = "province",
    *,
    confusable: list[str] | None = None,
    aliases: list[str] | None = None,
    hints: list[str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    attrs: dict[str, Any] = {
        "layer_type": layer_type,
        "feature_class": layer_type,
        "confusable_with": confusable or [],
        "qie_aliases": aliases or [],
        "evidence_topic_hints": hints or [],
    }
    attrs.update(extra)
    return attrs
