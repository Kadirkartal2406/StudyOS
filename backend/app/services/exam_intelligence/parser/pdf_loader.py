"""Load PDF pages via pypdf — text extracted only in memory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class LoadedPdf:
    path: Path
    page_count: int
    pages: list[str]  # raw text per page (transient; never persisted as stems)


def load_pdf(path: Path | str) -> LoadedPdf:
    p = Path(path)
    reader = PdfReader(str(p))
    pages: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text)
    return LoadedPdf(path=p, page_count=len(pages), pages=pages)
