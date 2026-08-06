"""M29.10 — Prompt Library (templates only; no frozen Prompt Builder edits)."""

from __future__ import annotations

import json
from typing import Any


def _compact_style(contract: dict[str, Any] | None) -> dict[str, Any]:
    if not contract:
        return {}
    keys = (
        "exam_code",
        "topic_code",
        "reading_load",
        "reasoning",
        "trap",
        "intent",
        "bloom",
        "thinking_pattern",
        "difficulty",
        "expected_time_sec",
        "option_balance",
        "language_style",
        "expected_thinking",
        "cluster",
    )
    return {k: contract.get(k) for k in keys if k in contract}


def plan_messages(plan: dict[str, Any], style: dict[str, Any]) -> list[dict[str, str]]:
    system = """Sen StudyOS Question Author Planner'sın.
Soru YAZMA. Sadece JSON Question Plan üret.
Alanlar: measured_outcome, reasoning_type, distractor_type, paragraph_length,
option_strategy, bloom_level, difficulty_target, reading_duration_sec, trap_type.
Telifli soru kopyalama yasak."""
    user = f"""STYLE CONTRACT (soru metni yok):
{json.dumps(_compact_style(style), ensure_ascii=False, indent=2)}

BLUEPRINT / QIE PLAN İPUÇLARI:
{json.dumps(plan, ensure_ascii=False, indent=2)}

Çıktı SADECE JSON object."""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def writer_messages(
    author_plan: dict[str, Any],
    *,
    style: dict[str, Any],
    correct_only: bool = False,
    eae_grounding_context: str | None = None,
) -> list[dict[str, str]]:
    keys = ["A", "B", "C", "D", "E"][: int(author_plan.get("choice_count") or 5)]
    if correct_only:
        system = """Sen StudyOS Question Writer'sın.
Author Plan + Style Contract'a uyarak TEK soru gövdesi ve DOĞRU CEVABI yaz.
Şıkları şimdilik yazma — sadece stem + correct_answer_text + brief_rationale.
JSON: {"stem":"...","correct_answer_text":"...","rationale":"..."}
ÖSYM dili, orijinal, telif yok."""
    else:
        system = f"""Sen StudyOS Question Writer'sın.
Author Plan + Style Contract + Difficulty Target'a uyarak TEK çoktan seçmeli soru yaz.
Şıklar: {", ".join(keys)}. Tek doğru.
JSON: {{"stem":"...","choices":{{{", ".join(f'"{k}":"..."' for k in keys)}}},"correct_key":"{keys[0]}","explanation":"...","target_node_id":"...","correct_node_id":"..."}}
ÖSYM dili. Telifli kopya yasak. Plan alanlarını değiştirme.
EAE görsel sorularda seçenekler ve doğru cevap Node ID kullanmalıdır."""
    if eae_grounding_context:
        system = f"{system}\n\n{eae_grounding_context}"
    user = f"""STYLE CONTRACT:
{json.dumps(_compact_style(style), ensure_ascii=False, indent=2)}

AUTHOR PLAN:
{json.dumps(author_plan, ensure_ascii=False, indent=2)}

Difficulty target={author_plan.get("difficulty_target")}
Reasoning={author_plan.get("reasoning_type")}
Reading time≈{author_plan.get("reading_duration_sec")} sn
Paragraph≈{author_plan.get("paragraph_length")} kelime
Trap={author_plan.get("trap_type")}
"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def critic_messages(question: dict[str, Any], author_plan: dict[str, Any]) -> list[dict[str, str]]:
    system = """Sen StudyOS Self Critic'sın.
Verilen soruyu puanla (0-100): style, difficulty, option_quality, distractors,
language, naturalness, exam_feeling, reasoning.
JSON: {"style":0,"difficulty":0,"option_quality":0,"distractors":0,"language":0,
"naturalness":0,"exam_feeling":0,"reasoning":0,"notes":"..."}"""
    user = f"""AUTHOR PLAN:
{json.dumps(author_plan, ensure_ascii=False)}

QUESTION:
{json.dumps(question, ensure_ascii=False)}"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def rewrite_messages(
    question: dict[str, Any],
    author_plan: dict[str, Any],
    critic: dict[str, Any],
) -> list[dict[str, str]]:
    system = """Sen StudyOS Rewrite Engine'sın.
Eleştiriye göre soruyu YENİDEN yaz. Aynı kazanım/plan korunacak.
Zayıf stil, difficulty veya distractor'ları güçlendir.
JSON soru formatı: stem, choices, correct_key, explanation."""
    user = f"""PLAN: {json.dumps(author_plan, ensure_ascii=False)}
CRITIC: {json.dumps(critic, ensure_ascii=False)}
OLD QUESTION: {json.dumps(question, ensure_ascii=False)}
Yeniden yaz."""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def distractor_messages(
    stem: str,
    correct_text: str,
    correct_key: str,
    trap_types: list[str],
    choice_count: int,
) -> list[dict[str, str]]:
    keys = [k for k in ["A", "B", "C", "D", "E"][:choice_count] if k != correct_key]
    system = """Sen StudyOS Distractor Author'sın.
Doğru cevap sabit. Her yanlış şık FARKLI hata tipinden gelsin.
JSON: {"distractors":[{"key":"B","text":"...","trap_type":"yanlis_cikarim"}, ...]}"""
    user = f"""STEM: {stem}
CORRECT_KEY: {correct_key}
CORRECT_TEXT: {correct_text}
NEED KEYS: {keys}
TRAP TYPES (assign uniquely): {trap_types}
Her key için bir distractor."""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def naturalizer_messages(question: dict[str, Any], exam: str) -> list[dict[str, str]]:
    system = f"""Sen StudyOS Question Naturalizer'sın.
AI kokusunu azalt. Tekrarlayan kalıpları temizle.
{exam.upper()} / ÖSYM resmi diline yaklaştır.
Anlamı ve doğru cevabı değiştirme.
JSON: stem, choices, correct_key, explanation."""
    user = json.dumps(question, ensure_ascii=False, indent=2)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def examiner_messages(question: dict[str, Any], exam: str) -> list[dict[str, str]]:
    system = f"""Sen ÖSYM soru hazırlama komisyonusun ({exam.upper()}).
0-100 puanla: exam_ready, paragraph_natural, options_balanced,
answer_not_guessable, distractors_strong, osym_feel.
JSON + "notes" alanı. 85 altı sınava girmez."""
    user = json.dumps(question, ensure_ascii=False, indent=2)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
