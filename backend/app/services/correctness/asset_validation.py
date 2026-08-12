"""Required asset / dangling-reference check — deictic patterns only."""

from __future__ import annotations

import re
from typing import Any

from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
)

# Determiner + asset type (not a bare "grafik" mention).
_DEICTIC_TR = re.compile(
    r"(yukar[ıi]daki|a[sş]a[gğ][ıi]daki|verilen)\s+"
    r"(şekil|grafik|tablo|paragraf|metin|pasaj|diyagram)|"
    r"(şekil|grafik|tablo|paragraf|metin|pasaj)\s+"
    r"(veriliyor|verilmiştir|verilmektedir|aşağıdadır)",
    re.IGNORECASE,
)
_LOCATIVE_TR = re.compile(
    r"\b(şekilde|grafikte|tabloda|diyagramda)\b",
    re.IGNORECASE,
)
_DEICTIC_EN = re.compile(
    r"\b(the|this|following)\s+(passage|text|graph|figure|table|diagram)\b|"
    r"\baccording to the passage\b|"
    r"\bthe passage\b",
    re.IGNORECASE,
)
_INLINE_GEO = re.compile(
    r"T\s*\(\s*-?\d+\s*,\s*-?\d+\s*\)|"
    r"\(\s*-?\d+\s*,\s*-?\d+\s*\)|"
    r"y\s*=\s*|f\s*\(\s*x\s*\)",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+")


def _word_count(text: str) -> int:
    return len(_WORD_RE.findall(text or ""))


def _asset_present(inp: CorrectnessInput) -> bool:
    if inp.eae_interaction:
        eae = inp.eae_interaction
        if eae.get("target_asset_id") or eae.get("asset_uri") or eae.get("correct_node_id"):
            return True
    plan = inp.plan
    if plan is not None and getattr(plan, "target_asset_id", None):
        return True
    return False


def check_required_asset(inp: CorrectnessInput) -> CorrectnessCheck:
    stem = inp.stem or ""
    evidence: dict[str, Any] = {
        "deictic": False,
        "asset_present": _asset_present(inp),
        "word_count": _word_count(stem),
        "pattern": None,
    }
    plan = inp.plan
    required = bool(
        (plan is not None and getattr(plan, "requires_asset", None) is True)
        or (plan is not None and getattr(plan, "requires_passage", None) is True)
    )

    deictic = bool(_DEICTIC_TR.search(stem) or _DEICTIC_EN.search(stem))
    locative = bool(_LOCATIVE_TR.search(stem))
    evidence["deictic"] = deictic or locative

    if evidence["asset_present"]:
        return CorrectnessCheck(name="asset", status="pass", evidence=evidence)

    if required and not evidence["asset_present"]:
        evidence["pattern"] = "plan_requires_asset"
        return CorrectnessCheck(
            name="asset",
            status="fail",
            error_code=CorrectnessErrorCode.MISSING_REQUIRED_ASSET.value,
            message="missing_required_asset",
            evidence=evidence,
        )

    if deictic:
        # Passage-like: long stem likely contains the passage.
        if _DEICTIC_EN.search(stem) and evidence["word_count"] >= 80:
            evidence["pattern"] = "inline_passage"
            return CorrectnessCheck(name="asset", status="pass", evidence=evidence)
        if evidence["word_count"] >= 80 and _INLINE_GEO.search(stem):
            evidence["pattern"] = "self_describing"
            return CorrectnessCheck(name="asset", status="pass", evidence=evidence)
        evidence["pattern"] = "deictic_missing_asset"
        return CorrectnessCheck(
            name="asset",
            status="fail",
            error_code=CorrectnessErrorCode.MISSING_REQUIRED_ASSET.value,
            message="missing_required_asset",
            evidence=evidence,
        )

    if locative:
        # "Şekilde y=f(x) ... T(2,4)" is often self-contained; do not FAIL.
        if _INLINE_GEO.search(stem) or evidence["word_count"] >= 60:
            evidence["pattern"] = "locative_self_describing"
            return CorrectnessCheck(
                name="asset",
                status="unsupported",
                error_code=CorrectnessErrorCode.MISSING_REQUIRED_ASSET.value,
                message="asset:locative_ambiguous",
                evidence=evidence,
            )
        evidence["pattern"] = "locative_short"
        return CorrectnessCheck(
            name="asset",
            status="fail",
            error_code=CorrectnessErrorCode.MISSING_REQUIRED_ASSET.value,
            message="missing_required_asset",
            evidence=evidence,
        )

    return CorrectnessCheck(name="asset", status="pass", evidence=evidence)
