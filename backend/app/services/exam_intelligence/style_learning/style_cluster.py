"""Cluster topics into thinking-style families."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _cluster_label(
    *,
    topic_slug: str,
    skill_type: str | None,
    reading_band: str,
    reasoning_intensity: float,
) -> str:
    topic = (topic_slug or "").lower()
    skill = (skill_type or "").lower()

    if topic in ("paragraf", "reading") or skill in (
        "inference",
        "reading_comprehension",
    ):
        return "reading_heavy"
    if topic in ("problemler", "hareket", "mol", "fonksiyonlar") or skill == "problem_solving":
        if reasoning_intensity >= 0.45:
            return "reasoning_heavy"
        return "calculation_heavy"
    if topic in ("ucgenler",) or "geometri" in topic:
        return "spatial_geometry"
    if skill == "language_rules" or topic in ("dil_bilgisi", "yazim", "noktalama"):
        return "language_rules"
    if skill == "recall" or topic in ("osmanli", "anayasa", "hucre"):
        return "knowledge_recall"
    if reading_band in ("high", "very_high"):
        return "reading_heavy"
    if reasoning_intensity >= 0.5:
        return "reasoning_heavy"
    return "mixed_general"


def cluster_topics(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group style contracts into named clusters."""
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for c in contracts:
        reading = c.get("reading_load") or {}
        reasoning = c.get("reasoning") or {}
        intent = c.get("intent") or {}
        label = _cluster_label(
            topic_slug=str(intent.get("topic_slug") or c.get("topic_slug") or ""),
            skill_type=(c.get("language_style") or {}).get("skill_type"),
            reading_band=str(reading.get("load_band") or "medium"),
            reasoning_intensity=float(reasoning.get("reasoning_intensity") or 0.0),
        )
        buckets[label].append(
            {
                "exam_code": str(c.get("exam_code") or ""),
                "topic_code": str(c.get("topic_code") or ""),
                "subject_code": str(c.get("subject_code") or ""),
            }
        )

    out: list[dict[str, Any]] = []
    for label, members in sorted(buckets.items(), key=lambda x: -len(x[1])):
        out.append(
            {
                "cluster": label,
                "size": len(members),
                "members": members,
                "description": {
                    "reading_heavy": "Paragraph / reading comprehension dominant",
                    "reasoning_heavy": "Multi-step reasoning / logic dominant",
                    "calculation_heavy": "Procedure and calculation dominant",
                    "spatial_geometry": "Figure / spatial geometry dominant",
                    "language_rules": "Grammar / mechanics dominant",
                    "knowledge_recall": "Factual recall dominant",
                    "mixed_general": "Mixed thinking profile",
                }.get(label, label),
            }
        )
    return out


def assign_cluster_for_contract(contract: dict[str, Any]) -> str:
    reading = contract.get("reading_load") or {}
    reasoning = contract.get("reasoning") or {}
    intent = contract.get("intent") or {}
    return _cluster_label(
        topic_slug=str(intent.get("topic_slug") or contract.get("topic_slug") or ""),
        skill_type=(contract.get("language_style") or {}).get("skill_type"),
        reading_band=str(reading.get("load_band") or "medium"),
        reasoning_intensity=float(reasoning.get("reasoning_intensity") or 0.0),
    )
