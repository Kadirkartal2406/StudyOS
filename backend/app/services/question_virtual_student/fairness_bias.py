"""Fairness / bias heuristics (wording only — no generation)."""

from __future__ import annotations

from typing import Any

_GENDER = ("erkekler", "kızlar", "kadınlar", "baylar", "bayanlar")
_SES = ("lüks", "fakir", "zengin mahalle", "gecekondu", "özel okul")
_REGION = ("istanbul'da yaşayan", "köylü", "doğulu", "batılı", "anadolulu")
_HARD_VOCAB = ("epistemolojik", "ontolojik", "hermeneutik", "metaforik düzlem")


def check_fairness_bias(question: dict[str, Any]) -> dict[str, Any]:
    text = (
        str(question.get("stem") or "")
        + " "
        + " ".join(str(v) for v in (question.get("choices") or {}).values())
    ).lower()
    flags: list[str] = []
    score = 100

    if any(g in text for g in _GENDER):
        flags.append("gender_bias_risk")
        score -= 15
    if any(s in text for s in _SES):
        flags.append("socioeconomic_bias_risk")
        score -= 15
    if any(r in text for r in _REGION):
        flags.append("regional_bias_risk")
        score -= 12
    hard = [v for v in _HARD_VOCAB if v in text]
    if hard:
        flags.append("vocabulary_unfairness")
        score -= 10 + 5 * len(hard)

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "unfair_wording": score < 85,
    }
