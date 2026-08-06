"""
StudyOS Educational Asset Engine (EAE) — ReportLab Native Vector Renderer
Converts EAE SVG paths directly into ReportLab native Drawing/Path objects for crisp 1200 DPI printing.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from reportlab.graphics.shapes import Drawing, Group, Path, String
from reportlab.lib import colors


class BookletPdfEaeRenderer:
    """
    Parses SVG path elements into native ReportLab vector Drawing objects without rasterization.
    """

    def create_vector_drawing(
        self,
        svg_content: str,
        target_width: float = 300.0,
        target_height: float = 180.0,
        *,
        highlight_node_ids: list[str] | None = None,
    ) -> Drawing:
        drawing = Drawing(target_width, target_height)
        if not svg_content or not svg_content.strip():
            return drawing

        try:
            root = ET.fromstring(svg_content.strip())
        except ET.ParseError:
            return drawing

        viewbox_str = root.attrib.get("viewBox", "0 0 1000 500")
        vb_parts = [float(p) for p in viewbox_str.replace(",", " ").split() if p]
        vb_w = vb_parts[2] if len(vb_parts) >= 4 else 1000.0
        vb_h = vb_parts[3] if len(vb_parts) >= 4 else 500.0

        scale_x = target_width / vb_w if vb_w > 0 else 1.0
        scale_y = target_height / vb_h if vb_h > 0 else 1.0

        group = Group()
        group.scale(scale_x, scale_y)
        highlights = set(highlight_node_ids or [])

        for elem in root.iter():
            tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_local != "path":
                continue
            path_d = elem.attrib.get("d", "")
            if not path_d:
                continue
            node_id = elem.attrib.get("id", "")
            highlighted = node_id in highlights
            rl_path = self._convert_svg_d_to_reportlab_path(
                path_d,
                fill="#FBBF24" if highlighted else "#E2E8F0",
                stroke="#B45309" if highlighted else "#334155",
                stroke_width=2.4 if highlighted else 1.5,
            )
            group.add(rl_path)

        drawing.add(group)
        return drawing

    def create_vector_drawing_from_bundle(
        self,
        bundle_payload: bytes,
        *,
        highlight_node_ids: list[str] | None = None,
        target_width: float = 300.0,
        target_height: float = 180.0,
    ) -> Drawing:
        from app.services.asset_compiler.packager import BundlePackager

        unpacked = BundlePackager().unpack(bundle_payload)
        svg = unpacked.get("svg_content") or ""
        return self.create_vector_drawing(
            svg,
            target_width=target_width,
            target_height=target_height,
            highlight_node_ids=highlight_node_ids,
        )

    def _convert_svg_d_to_reportlab_path(
        self,
        d_str: str,
        *,
        fill: str = "#E2E8F0",
        stroke: str = "#334155",
        stroke_width: float = 1.5,
    ) -> Path:
        rl_path = Path(
            fillColor=colors.HexColor(fill),
            strokeColor=colors.HexColor(stroke),
            strokeWidth=stroke_width,
        )

        tokens = re.findall(r"([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)", d_str)
        cmd = ""
        params: list[float] = []

        for token_tup in tokens:
            t_cmd, t_val = token_tup
            if t_cmd:
                if cmd:
                    self._apply_cmd(rl_path, cmd, params)
                    params = []
                cmd = t_cmd
            elif t_val:
                try:
                    params.append(float(t_val))
                except ValueError:
                    pass

        if cmd:
            self._apply_cmd(rl_path, cmd, params)

        return rl_path

    @staticmethod
    def _apply_cmd(rl_path: Path, cmd: str, p: list[float]) -> None:
        if cmd in ("M", "m"):
            for i in range(0, len(p) - 1, 2):
                if i == 0:
                    rl_path.moveTo(p[i], p[i + 1])
                else:
                    rl_path.lineTo(p[i], p[i + 1])
        elif cmd in ("L", "l"):
            for i in range(0, len(p) - 1, 2):
                rl_path.lineTo(p[i], p[i + 1])
        elif cmd in ("C", "c"):
            for i in range(0, len(p) - 5, 6):
                rl_path.curveTo(p[i], p[i + 1], p[i + 2], p[i + 3], p[i + 4], p[i + 5])
        elif cmd in ("Q", "q"):
            for i in range(0, len(p) - 3, 4):
                # Approximate quadratic as cubic
                rl_path.curveTo(p[i], p[i + 1], p[i], p[i + 1], p[i + 2], p[i + 3])
        elif cmd in ("Z", "z"):
            rl_path.closePath()
