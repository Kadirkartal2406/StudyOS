"""Prompt Builder v3 — style contract from QuestionPlan + Exam DNA.

LLM is a writer only: it must follow the plan and must not invent skill/difficulty/bloom.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.services.qie.distractor_model import distractor_contract
from app.services.qie.planner import band_for_difficulty_score, difficulty_contract_for_band
from app.services.qie.types import PROMPT_VERSION, QuestionPlan


def build_qie_messages(
    plans: list[QuestionPlan],
    *,
    style_dna: dict[str, Any],
) -> tuple[list[dict[str, str]], str]:
    """Return (messages, fingerprint) for one batch."""
    if not plans:
        raise ValueError("plans required")

    choice_count = plans[0].choice_count
    keys = ["A", "B", "C", "D", "E"][:choice_count]
    keys_json = ", ".join(keys)

    plan_payload = [p.to_dict() for p in plans]
    dna_compact = {
        k: style_dna.get(k)
        for k in (
            "exam_code",
            "paragraph_length_avg",
            "paragraph_length_range",
            "sentence_count",
            "option_length",
            "option_similarity",
            "distractor_patterns",
            "vocabulary_level",
            "reading_time",
            "bloom_distribution",
            "reasoning_distribution",
            "option_style",
            "wording_style",
            "abstraction_level",
            "inference_ratio",
            "elimination_ratio",
            "choice_count",
        )
        if k in style_dna or style_dna.get(k) is not None
    }

    bands = {band_for_difficulty_score(int(p.difficulty)) for p in plans}
    band_lines = "\n".join(
        f"- {b.upper()}: {difficulty_contract_for_band(b)}" for b in sorted(bands)
    )

    system = f"""Sen StudyOS Question Intelligence Engine yazıcısısın.
Rolün: verilen Question Plan ve Exam Style DNA'ya birebir uyan çoktan seçmeli sorular YAZMAK.
KARAR VERMEYECEKSİN. skill, bloom, difficulty, distractor_pattern, stem_type alanlarını DEĞİŞTİRMEYECEKSİN.
Prompt version: {PROMPT_VERSION}

KURALLAR:
1) Her soru için plan[i] alanları zorunlu sözleşmedir.
2) Telifli gerçek ÖSYM sorusu kopyalama / hatırlama YASAK. Orijinal üret.
3) Şıklar {keys_json} — tam {choice_count} şık, tek doğru.
4) Distractor'lar plan.distractor_pattern sözleşmesine göre üretilecek.
5) Paragraf/stem uzunluğu plan.paragraph_length (kelime) hedefine yakın olsun.
6) Seçenek uzunlukları dengeli (option_balance={plans[0].option_balance}).
7) Zorluk bilişsel yük ile sağlanır; soruyu yalnızca uzatarak zorlaştırma YASAK.
8) Bu batch için zorluk sözleşmesi:
{band_lines}
9) Çıktı SADECE JSON:
{{"questions":[{{"stem":"...","choices":{{{", ".join(f'"{k}":"..."' for k in keys)}}},"correct_key":"{keys[0]}","explanation":"...","plan_index":0}}]}}
10) plan_index, plans dizisindeki index ile eşleşmeli.
11) Kullanıcıya veya meta olarak skill/bloom yazma; sadece soru metni.
"""

    has_eae = any(p.target_asset_id for p in plans)
    if has_eae:
        system += """12) EAE MAP BAĞLANTISI: Eğer planda `target_asset_id` ve `available_nodes` verilmişse, bu soru interaktif bir harita (EAE) sorusudur. 
`available_nodes` listesinden bir node'u seçip, o node ile ilgili ("Haritada işaretli il hangisidir?", "Hangi nehir..." vb.) bir soru yaz.
Seçtiğin node'u JSON içerisinde `eae_interaction` objesi olarak belirt.
Örnek JSON eklemesi: 
"eae_interaction": {"target_asset_id": "studyos://...", "correct_node_id": "turkey_admin_v1::province::konya"}
"""

    plan_lines = []
    for p in plans:
        band = band_for_difficulty_score(int(p.difficulty))
        line = (
            f"- index={p.index} skill={p.skill} bloom={p.bloom} "
            f"difficulty={p.difficulty} band={band} stem_type={p.stem_type} "
            f"paragraph_words≈{p.paragraph_length} reading_sec={p.reading_time_sec} "
            f"distractor={p.distractor_pattern} "
            f"({distractor_contract(p.distractor_pattern)}) "
            f"forbidden={p.forbidden_recent_patterns}"
        )
        if p.target_asset_id:
            line += f" TARGET_MAP={p.target_asset_id} ALLOWED_NODES={p.available_nodes}"
        plan_lines.append(line)

    user = f"""EXAM STYLE DNA (istatistik — soru metni yok):
{json.dumps(dna_compact, ensure_ascii=False, indent=2)}

QUESTION PLANS (değiştirilemez):
{json.dumps(plan_payload, ensure_ascii=False, indent=2)}

Özet:
{chr(10).join(plan_lines)}

Exam={plans[0].exam} Subject={plans[0].subject_name} Topic={plans[0].topic_name}
Tam {len(plans)} soru üret. Hiçbir planı atlama veya birleştirme.
"""
    soft_block = style_dna.get("measurement_soft_block")
    if soft_block:
        user = f"{user}\n{soft_block}\n"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    fp = hashlib.sha256(
        (system + user + PROMPT_VERSION).encode("utf-8")
    ).hexdigest()[:32]
    return messages, fp
