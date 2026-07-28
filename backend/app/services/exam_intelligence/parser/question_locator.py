"""Locate question boundaries without persisting stem text."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Common ÖSYM-style numbering: "1.", "1)", "1 -", sometimes "SORU 1"
_Q_START = re.compile(
    r"(?m)(?:^|\n)\s*(?:SORU\s*)?(\d{1,3})\s*[\.\)\-–:]\s+",
    re.IGNORECASE,
)
_OPTION = re.compile(
    r"(?m)^\s*([A-EÁÀ])\s*[\.\)\-–:]\s*",
)


@dataclass
class LocatedQuestion:
    number: int
    page: int | None
    # Transient text for heuristics only — callers must not write this to disk.
    _transient_text: str
    word_count: int
    sentence_count: int
    option_lengths: list[int]
    symbol_count: int
    equation_count: int
    has_table: bool
    has_visual_hint: bool
    multi_step: bool


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", text or "", re.UNICODE))


def _sentence_count(text: str) -> int:
    parts = re.split(r"[.!?…]+", text or "")
    return max(0, sum(1 for p in parts if p.strip()))


def _option_lengths(text: str) -> list[int]:
    spans = list(_OPTION.finditer(text or ""))
    if not spans:
        return []
    lengths: list[int] = []
    for i, m in enumerate(spans):
        start = m.end()
        end = spans[i + 1].start() if i + 1 < len(spans) else len(text)
        chunk = text[start:end]
        lengths.append(_word_count(chunk))
    return lengths[:5]


_ANSWER_ONLY = re.compile(
    r"(?is)^\s*(?:SORU\s*)?\d{1,3}\s*[\.\)\-–:]?\s*[A-E]\s*(?:\n|$)",
)


def _looks_like_answer_key_row(blob: str) -> bool:
    """Skip rows that are only '12. A' style answer-key noise."""
    compact = (blob or "").strip()
    if len(compact) < 8:
        return True
    if _ANSWER_ONLY.match(compact):
        return True
    # Dense key tables: many "N X" pairs, almost no prose
    letters = len(re.findall(r"\b[A-E]\b", compact))
    words = _word_count(compact)
    if letters >= 3 and words <= letters + 2:
        return True
    return False


def locate_questions(pages: list[str]) -> list[LocatedQuestion]:
    """Scan pages; keep only stats + transient blob for estimators."""
    found: dict[int, LocatedQuestion] = {}
    for page_idx, page_text in enumerate(pages, start=1):
        matches = list(_Q_START.finditer(page_text or ""))
        for i, m in enumerate(matches):
            num = int(m.group(1))
            if num < 1 or num > 200:
                continue
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(page_text)
            blob = page_text[start:end]
            # Cap transient blob to reduce accidental leakage risk in logs
            blob = blob[:4000]
            if _looks_like_answer_key_row(blob):
                continue
            low = blob.lower()
            eq = len(re.findall(r"[=∑∫√≤≥≠]|\\frac|\\sqrt", blob))
            symbols = len(re.findall(r"[α-ωΑ-Ω°∞±×÷]", blob))
            has_table = any(k in low for k in ("tablo", "table", "|---"))
            has_visual = any(
                k in low
                for k in ("şekil", "sekil", "grafik", "diyagram", "figure", "görsel")
            )
            multi = (
                blob.count("?") >= 2
                or "öncelikle" in low
                or "ardından" in low
                or "adım" in low
            )
            opts = _option_lengths(blob)
            found[num] = LocatedQuestion(
                number=num,
                page=page_idx,
                _transient_text=blob,
                word_count=_word_count(blob),
                sentence_count=_sentence_count(blob),
                option_lengths=opts,
                symbol_count=symbols,
                equation_count=eq,
                has_table=has_table,
                has_visual_hint=has_visual,
                multi_step=multi,
            )
    return [found[k] for k in sorted(found)]


def synthesize_shell_questions(
    count: int,
    *,
    from_answer_key: dict[str, str] | None = None,
) -> list[LocatedQuestion]:
    """Create empty shells when PDF is image-only (stats only, no text)."""
    numbers: list[int]
    if from_answer_key:
        numbers = sorted(int(k) for k in from_answer_key if str(k).isdigit())
    else:
        numbers = list(range(1, max(count, 0) + 1))
    out: list[LocatedQuestion] = []
    for num in numbers:
        out.append(
            LocatedQuestion(
                number=num,
                page=None,
                _transient_text="",
                word_count=0,
                sentence_count=0,
                option_lengths=[],
                symbol_count=0,
                equation_count=0,
                has_table=False,
                has_visual_hint=False,
                multi_step=False,
            )
        )
    return out
