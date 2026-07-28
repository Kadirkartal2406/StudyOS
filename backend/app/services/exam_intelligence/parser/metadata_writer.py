"""Write telif-safe JSON artifacts under data/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.exam_intelligence.parser.types import ParseResult

# Forbidden keys that must never appear in written JSON
_FORBIDDEN = {
    "stem",
    "question_text",
    "choices",
    "options",
    "explanation",
    "answer_text",
    "passage",
    "transient_text",
    "_transient_text",
}


def _assert_safe(obj: Any, path: str = "$") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in _FORBIDDEN or "stem" in lk or lk.endswith("_text") and lk not in (
                "booklet_type",
            ):
                if lk in _FORBIDDEN or lk in ("stem", "question_text", "passage"):
                    raise ValueError(f"Forbidden field in output: {path}.{k}")
            _assert_safe(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_safe(v, f"{path}[{i}]")


def write_json(path: Path, data: dict[str, Any]) -> Path:
    _assert_safe(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def metadata_path(data_root: Path, result: ParseResult) -> Path:
    exam = result.exam_code or "unknown"
    parts = [data_root / "parsed_metadata" / exam]
    if result.pack and result.pack not in (exam, "general"):
        parts.append(Path(result.pack))
    base = parts[0]
    for p in parts[1:]:
        base = base / p
    session = result.session_id or result.year or "unknown"
    return base / f"{session}.json"


def write_metadata(data_root: Path, result: ParseResult) -> Path:
    return write_json(metadata_path(data_root, result), result.metadata_dict())


def write_style_stats(
    data_root: Path,
    exam_code: str,
    stats_map: dict[tuple[str, str], dict[str, Any]],
) -> list[Path]:
    written: list[Path] = []
    for (sub, topic), stats in stats_map.items():
        # topic like kpss_turkce__paragraf → folder paragraf under subject
        topic_slug = topic.split("__")[-1] if "__" in topic else "general"
        sub_slug = sub.split("_", 1)[-1] if "_" in sub else sub
        path = (
            data_root
            / "exam_style_stats"
            / exam_code
            / sub_slug
            / topic_slug
            / "stats.json"
        )
        written.append(write_json(path, stats))
    return written


def write_style_profile(data_root: Path, exam_code: str, dna: dict[str, Any]) -> Path:
    name = {
        "kpss": "KPSS.json",
        "tyt": "TYT.json",
        "ayt": "AYT.json",
        "ydt": "YDT.json",
        "ales": "ALES.json",
        "yds": "YDS.json",
        "yokdil": "YOKDIL.json",
        "lgs": "LGS.json",
        "ags": "AGS.json",
        "dgs": "DGS.json",
    }.get(exam_code, f"{exam_code.upper()}.json")
    return write_json(data_root / "exam_style_profiles" / name, dna)


def write_report(data_root: Path, result: ParseResult) -> Path:
    reports = data_root / "parsed_metadata" / "_reports"
    reports.mkdir(parents=True, exist_ok=True)
    session = result.session_id or result.year or "unknown"
    path = reports / f"{result.exam_code}_{session}_report.txt"
    path.write_text("\n".join(result.report_lines) + "\n", encoding="utf-8")
    return path
