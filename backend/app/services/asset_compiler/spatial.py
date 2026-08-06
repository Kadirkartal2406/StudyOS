"""
StudyOS Educational Asset Engine (EAE) — Spatial Index & Bounding Box Builder
"""

from __future__ import annotations

import re
from typing import Any


class SpatialIndexBuilder:
    """
    Computes bounding boxes and a hierarchical 2D R-tree for client hit testing.
    """

    def compute_bounding_box(self, points: list[tuple[float, float]]) -> list[float]:
        if not points:
            return [0.0, 0.0, 0.0, 0.0]

        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)

        return [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)]

    def bbox_from_svg_path(self, path_d: str) -> list[float]:
        """Extract approximate bbox from SVG path `d` numeric tokens."""
        nums = [float(n) for n in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", path_d or "")]
        if len(nums) < 2:
            return [0.0, 0.0, 0.0, 0.0]
        xs = nums[0::2]
        ys = nums[1::2]
        if not xs or not ys:
            return [0.0, 0.0, 0.0, 0.0]
        return self.compute_bounding_box(list(zip(xs, ys, strict=False)))

    def build_spatial_tree(self, nodes: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Builds a hierarchical R-tree (sort-tile-recursive style) for O(log N) hit testing.
        """
        entries: list[dict[str, Any]] = []
        for n in nodes:
            node_id = str(n.get("id", ""))
            bbox = list(n.get("bounding_box") or [0.0, 0.0, 0.0, 0.0])
            if len(bbox) < 4:
                bbox = [0.0, 0.0, 0.0, 0.0]
            entries.append(
                {
                    "type": "leaf",
                    "node_id": node_id,
                    "bbox": bbox,
                    "area": self._calc_area(bbox),
                }
            )

        root = self._build_rtree(entries, max_children=8)
        return {
            "root": root,
            "count": len(entries),
            "algorithm": "str_rtree_v1",
        }

    def query_bbox(
        self, tree: dict[str, Any], point: tuple[float, float]
    ) -> list[str]:
        """Return candidate node_ids whose bbox contains the point."""
        root = tree.get("root") or tree
        hits: list[str] = []
        self._query_node(root, point[0], point[1], hits)
        return hits

    def _query_node(
        self, node: dict[str, Any], x: float, y: float, hits: list[str]
    ) -> None:
        bbox = node.get("bbox") or [0, 0, 0, 0]
        if not self._contains(bbox, x, y):
            return
        if node.get("type") == "leaf":
            hits.append(str(node.get("node_id", "")))
            return
        for child in node.get("children") or []:
            self._query_node(child, x, y, hits)

    def _build_rtree(
        self, entries: list[dict[str, Any]], max_children: int = 8, depth: int = 0
    ) -> dict[str, Any]:
        if not entries:
            return {
                "type": "node",
                "bbox": [0.0, 0.0, 0.0, 0.0],
                "children": [],
                "count": 0,
            }
        if len(entries) <= max_children:
            bbox = self._union_bboxes([e["bbox"] for e in entries])
            return {
                "type": "node",
                "bbox": bbox,
                "children": entries,
                "count": len(entries),
            }

        # Sort-Tile-Recursive: alternate axis, split into tiles
        axis = depth % 2
        entries_sorted = sorted(
            entries,
            key=lambda e: (e["bbox"][axis] + e["bbox"][axis + 2]) / 2.0,
        )
        tile_count = max(2, int(len(entries_sorted) ** 0.5))
        tile_size = max(max_children, (len(entries_sorted) + tile_count - 1) // tile_count)
        children: list[dict[str, Any]] = []
        for i in range(0, len(entries_sorted), tile_size):
            chunk = entries_sorted[i : i + tile_size]
            children.append(self._build_rtree(chunk, max_children=max_children, depth=depth + 1))

        bbox = self._union_bboxes([c["bbox"] for c in children])
        return {
            "type": "node",
            "bbox": bbox,
            "children": children,
            "count": sum(int(c.get("count") or 1) for c in children),
        }

    @staticmethod
    def _contains(bbox: list[float], x: float, y: float) -> bool:
        if len(bbox) < 4:
            return False
        return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]

    @staticmethod
    def _union_bboxes(bboxes: list[list[float]]) -> list[float]:
        if not bboxes:
            return [0.0, 0.0, 0.0, 0.0]
        return [
            min(b[0] for b in bboxes),
            min(b[1] for b in bboxes),
            max(b[2] for b in bboxes),
            max(b[3] for b in bboxes),
        ]

    @staticmethod
    def _calc_area(bbox: list[float]) -> float:
        if len(bbox) < 4:
            return 0.0
        width = max(0.0, bbox[2] - bbox[0])
        height = max(0.0, bbox[3] - bbox[1])
        return width * height
