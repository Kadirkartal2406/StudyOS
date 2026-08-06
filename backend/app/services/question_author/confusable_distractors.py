"""Confusable-node distractor selection for EAE visual questions."""

from __future__ import annotations

from typing import Any


def pick_confusable_distractors(
    correct_node_id: str,
    *,
    node_attributes: dict[str, Any] | None = None,
    taxonomy: list[dict[str, Any]] | None = None,
    limit: int = 3,
) -> list[str]:
    """
    Prefer attributes.confusable_with; fall back to same layer_type peers from taxonomy.
    """
    attrs = node_attributes or {}
    confusable = [
        str(x) for x in (attrs.get("confusable_with") or []) if str(x) != correct_node_id
    ]
    if len(confusable) >= limit:
        return confusable[:limit]

    layer = attrs.get("layer_type")
    peers: list[str] = []
    for item in taxonomy or []:
        nid = str(item.get("node_id") or "")
        if not nid or nid == correct_node_id:
            continue
        item_attrs = item.get("attributes") or {}
        if layer and item_attrs.get("layer_type") == layer:
            peers.append(nid)
        elif nid in confusable:
            continue

    ordered = confusable + [p for p in peers if p not in confusable]
    return ordered[:limit]
