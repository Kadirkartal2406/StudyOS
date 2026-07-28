"""Infer exam identity from path / filename — no AI."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExamIdentity:
    exam_code: str
    pack: str | None
    year: str | None
    session_id: str | None
    booklet_type: str | None
    language: str
    duration_minutes: int | None
    relative_source: str


_YEAR_RE = re.compile(r"(20\d{2})")
_DURATION: dict[str, int] = {
    "kpss": 130,
    "tyt": 165,
    "ayt": 180,
    "ales": 150,
    "yds": 180,
    "yokdil": 180,
    "lgs": 120,
    "ags": 130,
    "dgs": 145,
}


def _fold(s: str) -> str:
    """ASCII-ish fold for Turkish folder names (handles mojibake remnants)."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    return (
        s.replace("ı", "i")
        .replace("İ", "i")
        .replace("ş", "s")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ö", "o")
        .replace("ç", "c")
    )


def infer_identity(pdf_path: Path, *, repo_root: Path | None = None) -> ExamIdentity:
    parts = [_fold(x) for x in pdf_path.parts]
    name = _fold(pdf_path.stem)
    joined = "/".join(parts)

    exam = "unknown"
    pack: str | None = None
    booklet: str | None = None
    language = "tr"

    if "kpss" in parts or "kpss" in name:
        exam = "kpss"
        if any("onlisans" in p or p.endswith("nlisans") for p in parts) or "onlisans" in name:
            pack = "onlisans"
        elif any("ortaogretim" in p or "ortaog" in p for p in parts) or "ortaogretim" in name:
            pack = "ortaogretim"
        elif any(p == "lisans" or p.endswith("/lisans") for p in parts) or "lisans" in name:
            pack = "lisans"
        else:
            pack = "lisans"
    elif "tyt" in parts or "/tyt/" in joined or name.startswith("tyt"):
        exam = "tyt"
        pack = "tyt"
    elif "ayt" in parts or "/ayt/" in joined:
        exam = "ayt"
        pack = "ayt"
    elif "ydt" in parts or "ydt" in name:
        exam = "ydt"
        pack = "ydt"
        language = "en"
        for lang in ("ingilizce", "almanca", "fransizca", "arapca", "rusca"):
            if lang in name or any(lang in p for p in parts):
                booklet = lang
                break
    elif "ales" in parts or "ales" in name:
        exam = "ales"
        for p in parts:
            if p in ("1", "2", "3"):
                pack = p
                break
        pack = pack or "general"
    elif "yds" in parts or "yds" in name:
        exam = "yds"
        language = "en"
        pack = "yds"
    elif any("yokdil" in p or p.endswith("kdil") for p in parts) or "yokdil" in name or "kdil" in name:
        exam = "yokdil"
        language = "en"
        if "fen" in name or any("fen" in p for p in parts):
            pack = "fen"
        elif "saglik" in name or any("saglik" in p for p in parts):
            pack = "saglik"
        elif "sosyal" in name or any("sosyal" in p for p in parts):
            pack = "sosyal"
        else:
            pack = "general"
    elif "lgs" in parts or "lgs" in name:
        exam = "lgs"
        if any("sayisal" in p for p in parts) or "sayisal" in name:
            pack = "sayisal"
        elif any("sozel" in p for p in parts) or "sozel" in name:
            pack = "sozel"
        else:
            pack = "general"
    elif "ags" in parts or "ags" in name:
        exam = "ags"
        pack = "ags"
    elif "dgs" in parts or "dgs" in name:
        exam = "dgs"
        pack = "dgs"

    year_m = _YEAR_RE.search(name) or _YEAR_RE.search(joined)
    year = year_m.group(1) if year_m else None

    session = year
    if exam == "ales" and pack in ("1", "2", "3") and year:
        session = f"{year}_{pack}"
    elif booklet and year:
        session = f"{year}_{booklet}"
    elif exam == "yokdil" and pack:
        session = pack
    elif not session and pack:
        session = pack

    rel = str(pdf_path)
    if repo_root is not None:
        try:
            rel = str(pdf_path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
        except ValueError:
            rel = pdf_path.name

    return ExamIdentity(
        exam_code=exam,
        pack=pack,
        year=year,
        session_id=session,
        booklet_type=booklet or pack,
        language=language,
        duration_minutes=_DURATION.get(exam),
        relative_source=rel,
    )
