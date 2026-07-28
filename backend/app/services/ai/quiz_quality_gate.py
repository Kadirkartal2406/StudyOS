"""
Sprint 14 — Quiz Quality Gate.

LLM çıktısı kullanıcıya gösterilmeden önce:
- JSON şema
- 4 şık (A–D)
- tek doğru cevap
- boş olmayan metinler
- konu soft-uyumu
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


_CHOICE_KEYS_4 = ("A", "B", "C", "D")
_CHOICE_KEYS_5 = ("A", "B", "C", "D", "E")
_MIN_STEM = 8
_MAX_STEM = 800
_MAX_STEM_BOOKLET = 2500
_MIN_CHOICE = 1
_MAX_CHOICE = 300
_MAX_CHOICE_BOOKLET = 500


@dataclass
class ValidatedQuizItem:
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None = None


@dataclass
class QualityGateResult:
    valid: list[ValidatedQuizItem]
    rejected_count: int
    errors: list[str]


def extract_json_payload(text: str) -> Any:
    """LLM metninden JSON çıkar (code fence toleranslı)."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Boş LLM yanıtı")
    # ```json ... ```
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if fence:
        raw = fence.group(1).strip()
    # İlk { veya [
    start_obj = raw.find("{")
    start_arr = raw.find("[")
    if start_obj == -1 and start_arr == -1:
        raise ValueError("JSON bulunamadı")
    if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
        raw = raw[start_arr:]
    else:
        raw = raw[start_obj:]
    return json.loads(raw)


def validate_quiz_payload(
    payload: Any,
    *,
    topic_name: str | None = None,
    expected_count: int = 5,
    choice_count: int = 4,
    max_stem: int | None = None,
) -> QualityGateResult:
    """
    Payload beklenen format:
      { "questions": [ { "stem", "choices": {A,B,C,D[,E]}, "correct_key", "explanation?" } ] }
    veya doğrudan liste.
    """
    errors: list[str] = []
    items_raw: list[Any]
    keys = _CHOICE_KEYS_5 if choice_count >= 5 else _CHOICE_KEYS_4
    stem_max = max_stem or (_MAX_STEM_BOOKLET if choice_count >= 5 else _MAX_STEM)
    choice_max = _MAX_CHOICE_BOOKLET if choice_count >= 5 else _MAX_CHOICE

    if isinstance(payload, dict):
        items_raw = payload.get("questions") or payload.get("items") or []
        if not isinstance(items_raw, list):
            return QualityGateResult([], 0, ["questions alanı liste değil"])
    elif isinstance(payload, list):
        items_raw = payload
    else:
        return QualityGateResult([], 0, ["Beklenen JSON obje veya liste"])

    valid: list[ValidatedQuizItem] = []
    rejected = 0
    topic_l = (topic_name or "").strip().lower()

    for idx, raw in enumerate(items_raw):
        ok, item, err = _validate_one(
            raw,
            topic_l=topic_l,
            choice_keys=keys,
            max_stem=stem_max,
            max_choice=choice_max,
        )
        if ok and item is not None:
            valid.append(item)
        else:
            rejected += 1
            errors.append(f"soru[{idx}]: {err}")

    if len(valid) > expected_count:
        valid = valid[:expected_count]

    if not valid:
        errors.append("Geçerli soru kalmadı — üretim reddedildi")

    return QualityGateResult(valid=valid, rejected_count=rejected, errors=errors)


def _validate_one(
    raw: Any,
    *,
    topic_l: str,
    choice_keys: tuple[str, ...] = _CHOICE_KEYS_4,
    max_stem: int = _MAX_STEM,
    max_choice: int = _MAX_CHOICE,
) -> tuple[bool, ValidatedQuizItem | None, str]:
    if not isinstance(raw, dict):
        return False, None, "obje değil"

    stem = str(raw.get("stem") or raw.get("question") or "").strip()
    if len(stem) < _MIN_STEM:
        return False, None, "stem çok kısa"
    if len(stem) > max_stem:
        return False, None, "stem çok uzun"

    # Eksik bağlama gönderme: kısa stem + gönderme kalıbı
    stem_l = stem.lower()
    dangling = (
        "yukarıdaki paragraf",
        "yukarıdaki metin",
        "aşağıdaki paragraf",
        "aşağıdaki metin",
        "verilen tabloya göre",
        "yukarıdaki tablo",
        "yukarıdaki şekil",
        "aşağıdaki şekil",
    )
    if any(p in stem_l for p in dangling) and len(stem) < 220:
        return False, None, "eksik bağlama gönderme (paragraf/metin stem içinde olmalı)"

    choices_in = raw.get("choices") or raw.get("options")
    choices: dict[str, str] = {}
    n = len(choice_keys)
    if isinstance(choices_in, dict):
        for k in choice_keys:
            val = choices_in.get(k) or choices_in.get(k.lower())
            if val is None and k == "E" and n == 5:
                # Gemini bazen 4 şık döner — E'yi tamamla
                choices[k] = "Yukarıdakilerin hiçbiri"
                continue
            if val is None:
                return False, None, f"şık {k} eksik"
            text = str(val).strip()
            if len(text) < _MIN_CHOICE or len(text) > max_choice:
                return False, None, f"şık {k} uzunluk geçersiz"
            choices[k] = text
    elif isinstance(choices_in, list) and len(choices_in) in {n, n - 1} and n == 5:
        # 4 veya 5 elemanlı liste
        for i, k in enumerate(choice_keys):
            if i < len(choices_in):
                text = str(choices_in[i]).strip()
            else:
                text = "Yukarıdakilerin hiçbiri"
            if len(text) < _MIN_CHOICE:
                return False, None, f"şık {k} boş"
            choices[k] = text
    elif isinstance(choices_in, list) and len(choices_in) == n:
        for i, k in enumerate(choice_keys):
            text = str(choices_in[i]).strip()
            if len(text) < _MIN_CHOICE:
                return False, None, f"şık {k} boş"
            choices[k] = text
    else:
        return False, None, f"{n} şık gerekli ({'-'.join(choice_keys)})"

    if len(set(choices.values())) < 2:
        return False, None, "şıklar birbirinin kopyası"

    correct = str(
        raw.get("correct_key") or raw.get("answer") or raw.get("correct") or ""
    ).strip().upper()
    if correct not in choice_keys:
        return False, None, f"correct_key {'|'.join(choice_keys)} olmalı"
    if correct not in choices:
        return False, None, "correct_key şıklarda yok"

    blob = stem.lower()
    if topic_l and len(topic_l) >= 4:
        if "lorem ipsum" in blob or blob.startswith("example question"):
            return False, None, "placeholder içerik"

    explanation = raw.get("explanation")
    expl = str(explanation).strip() if explanation else None
    if expl and len(expl) > 600:
        expl = expl[:600]

    return True, ValidatedQuizItem(
        stem=stem,
        choices=choices,
        correct_key=correct,
        explanation=expl,
    ), ""
