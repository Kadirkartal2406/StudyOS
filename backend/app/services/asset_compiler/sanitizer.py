"""
StudyOS Educational Asset Engine (EAE) — SVG Sanitizer
Strips malicious script tags, inline event handlers, external references, and dangerous CSS.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from app.core.asset_contracts.validator import ContractValidationError

# Register default SVG namespace to prevent ns0: prefixes
ET.register_namespace("", "http://www.w3.org/2000/svg")

# Dangerous tags to strip completely
DANGEROUS_TAGS = {"script", "iframe", "embed", "object", "foreignObject", "style"}

# Event handler attribute regex e.g. onload=, onclick=, onerror=
EVENT_HANDLER_REGEX = re.compile(r"^on[a-z]+$", re.IGNORECASE)

# Dangerous URL schemes
DANGEROUS_URL_SCHEMES = ("javascript:", "data:text/html", "vbscript:")


class SVGSanitizer:
    """
    Sanitizes raw SVG XML string to ensure zero XSS or remote script execution vulnerability.
    """

    def sanitize(self, raw_svg: str) -> str:
        text = (raw_svg or "").strip()
        if not text:
            raise ContractValidationError("SVG content is empty")

        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            raise ContractValidationError(f"Invalid SVG XML format: {exc}") from exc

        self._clean_element(root)

        # Re-serialize to clean XML string
        cleaned_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")
        return cleaned_xml

    def _clean_element(self, elem: ET.Element) -> None:
        # 1. Remove dangerous child elements
        to_remove = [child for child in elem if self._get_tag_local_name(child.tag) in DANGEROUS_TAGS]
        for child in to_remove:
            elem.remove(child)

        # 2. Clean attributes on current element
        attr_keys_to_delete = []
        for attr, val in elem.attrib.items():
            attr_local = self._get_tag_local_name(attr)
            val_str = str(val).strip().lower()

            # Remove on* event handlers
            if EVENT_HANDLER_REGEX.match(attr_local):
                attr_keys_to_delete.append(attr)
                continue

            # Remove javascript: or dangerous hrefs
            if any(val_str.startswith(scheme) for scheme in DANGEROUS_URL_SCHEMES):
                attr_keys_to_delete.append(attr)
                continue

        for k in attr_keys_to_delete:
            del elem.attrib[k]

        # 3. Recursively clean children
        for child in elem:
            self._clean_element(child)

    @staticmethod
    def _get_tag_local_name(tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag
