"""Extract answer key letters only — never question text."""

from __future__ import annotations

import re

# Prefer dense key formats: 1-A, 1.A, 1)A, 1 A (same line clusters)
_KEY_PAIR = re.compile(
    r"(?i)(?:^|[\s\|])(\d{1,3})\s*[\-\.\)–:]\s*([A-E])(?=\s|$|\||\d)"
)
_KEY_PAIR_LOOSE = re.compile(
    r"(?i)(?:^|[^\d])(\d{1,3})\s+([A-E])(?=\s|$)"
)
_ANSWER_SECTION = re.compile(
    r"(?is)(?:cevap\s*anahtar|answer\s*key|doğru\s*cevaplar|dogru\s*cevaplar|"
    r"cevaplar)\s*[:\-]?",
)
# Option lines inside stems — reject as keys when preceded by long prose on same page
_OPTION_LINE = re.compile(r"(?m)^\s*[A-E]\s*[\.\)\-–:]\s+\S+")


def _parse_pairs(section: str, *, loose: bool = False) -> dict[str, str]:
    key: dict[str, str] = {}
    pattern = _KEY_PAIR_LOOSE if loose else _KEY_PAIR
    for mm in pattern.finditer(section):
        n = int(mm.group(1))
        if 1 <= n <= 200:
            key[str(n)] = mm.group(2).upper()
    return key


def extract_answer_key(pages: list[str]) -> dict[str, str]:
    full = "\n".join(pages or [])
    key: dict[str, str] = {}
    from_header = False

    m = _ANSWER_SECTION.search(full)
    if m:
        from_header = True
        section = full[m.end() : m.end() + 16000]
        key = _parse_pairs(section)
        if len(key) < 5:
            key = _parse_pairs(section, loose=True)

    # Last pages often hold the key even without a clear header
    if len(key) < 5 and pages:
        tail = "\n".join(pages[-4:])
        option_hits = len(_OPTION_LINE.findall(tail))
        pairs = _parse_pairs(tail)
        if len(pairs) < 5:
            pairs = _parse_pairs(tail, loose=True)
        if len(pairs) >= 10 and option_hits < len(pairs):
            key = pairs

    # Drop sparse accidental hits unless they came from an explicit answer section
    if not from_header and 0 < len(key) < 8:
        return {}

    return dict(sorted(key.items(), key=lambda kv: int(kv[0])))
