"""Reading load / profile analyzer."""

from __future__ import annotations

from typing import Any


def analyze_reading_load(
    *,
    paragraph_avg: float = 0.0,
    sentence_avg: float = 0.0,
    reading_avg_sec: float = 0.0,
    visual_ratio: float = 0.0,
    option_length: float = 0.0,
    layout: dict[str, Any] | None = None,
    exam_dna: dict[str, Any] | None = None,
) -> dict[str, Any]:
    layout = layout or {}
    dna = exam_dna or {}
    para = float(paragraph_avg or dna.get("paragraph_length_avg") or 0.0)
    sent = float(sentence_avg or layout.get("sentence_count_avg") or 0.0)
    read = float(reading_avg_sec or dna.get("reading_time_sec_avg") or 0.0)
    visual = float(visual_ratio or layout.get("visual_usage_ratio") or 0.0)
    opt = float(option_length or dna.get("option_length_avg") or 0.0)

    # Information density proxy
    info_density = round(min(1.0, (para / 160.0) * 0.6 + (sent / 8.0) * 0.4), 3)
    text_complexity = (
        "high" if para >= 120 or sent >= 6 else ("medium" if para >= 50 else "low")
    )
    load_band = (
        "very_high"
        if para >= 140 or read >= 45
        else ("high" if para >= 90 or read >= 30 else ("medium" if para >= 40 else "low"))
    )

    return {
        "paragraph_length": round(para, 1),
        "sentence_count": round(sent, 2),
        "average_reading_time_sec": round(read, 1),
        "visual_density": round(visual, 3),
        "information_density": info_density,
        "text_complexity": text_complexity,
        "load_band": load_band,
        "option_length_avg": round(opt, 2),
        "page_layout": layout.get("page_layout") or "unknown",
    }
