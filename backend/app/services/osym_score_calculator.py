"""
StudyOS — ÖSYM Estimated Score Calculator Service (Sprint 33)
Hesaplama.net katsayı ve formülleri temel alınarak tahmini ÖSYM puanı hesaplar.
Desteklenen sınavlar: KPSS, TYT, AYT, LGS.
"""

from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel, Field


class SubjectNetInput(BaseModel):
    subject_code: str
    correct_count: int = Field(default=0, ge=0)
    wrong_count: int = Field(default=0, ge=0)


class CalculateScoreRequest(BaseModel):
    exam_type: str  # kpss | tyt | ayt | lgs
    inputs: list[SubjectNetInput]


class CalculatedScoreRead(BaseModel):
    exam_type: str
    total_correct: int
    total_wrong: int
    total_net: float
    estimated_score: float
    max_score: float
    badge: str
    disclaimer: str = (
        "Hesaplanan değer ÖSYM katsayıları temel alınarak hesaplanmış Tahmini Puan'dır. "
        "Resmi ÖSYM sonuç belgesi niteliği taşımaz."
    )


def compute_net(correct: int, wrong: int, wrong_penalty: float = 4.0) -> float:
    return max(0.0, float(correct) - (float(wrong) / wrong_penalty))


def calculate_osym_score(exam_type: str, inputs: list[SubjectNetInput]) -> CalculatedScoreRead:
    exam = (exam_type or "kpss").lower()
    penalty = 3.0 if exam == "lgs" else 4.0

    net_map: dict[str, float] = {}
    tot_correct = 0
    tot_wrong = 0

    for item in inputs:
        tot_correct += item.correct_count
        tot_wrong += item.wrong_count
        net = compute_net(item.correct_count, item.wrong_count, penalty)
        net_map[item.subject_code.lower()] = net

    total_net = sum(net_map.values())
    estimated_score = 0.0
    max_score = 100.0

    if exam == "kpss":
        # KPSS P3: 50 Base + 0.55 * GA_net + 0.55 * GK_net
        ga = net_map.get("kpss_matematik", 0) + net_map.get("kpss_turkce", 0) + net_map.get("genel_yetenek", 0)
        gk = net_map.get("kpss_tarih", 0) + net_map.get("kpss_cografya", 0) + net_map.get("kpss_vatandasalik", 0) + net_map.get("genel_kultur", 0)
        if not (ga or gk):
            ga = total_net * 0.5
            gk = total_net * 0.5
        estimated_score = min(100.0, 40.0 + (ga * 0.5) + (gk * 0.5))
        max_score = 100.0

    elif exam == "tyt":
        # TYT: 100 Base + Turkce*3.3 + Mat*3.3 + Sosyal*3.4 + Fen*3.4 (max 500)
        turkce = net_map.get("tyt_turkce", 0)
        mat = net_map.get("tyt_matematik", 0)
        sos = net_map.get("tyt_sosyal", 0)
        fen = net_map.get("tyt_fen", 0)
        if not (turkce or mat or sos or fen):
            turkce = total_net * 0.33
            mat = total_net * 0.33
            sos = total_net * 0.17
            fen = total_net * 0.17
        estimated_score = min(500.0, 100.0 + (turkce * 3.3) + (mat * 3.3) + (sos * 3.4) + (fen * 3.4))
        max_score = 500.0

    elif exam == "lgs":
        # LGS: 100 Base + Turkce*4 + Mat*4 + Fen*4 + Ink*2 + Din*2 + Ing*2 (max 500, 3 y 1 d)
        turkce = net_map.get("lgs_turkce", 0)
        mat = net_map.get("lgs_matematik", 0)
        fen = net_map.get("lgs_fen", 0)
        others = sum(v for k, v in net_map.items() if k not in {"lgs_turkce", "lgs_matematik", "lgs_fen"})
        if not (turkce or mat or fen):
            turkce = total_net * 0.25
            mat = total_net * 0.25
            fen = total_net * 0.25
            others = total_net * 0.25
        estimated_score = min(500.0, 100.0 + (turkce * 4.4) + (mat * 4.4) + (fen * 4.4) + (others * 2.2))
        max_score = 500.0

    else:  # AYT / General
        estimated_score = min(500.0, 100.0 + (total_net * 2.5))
        max_score = 500.0

    estimated_score = round(estimated_score, 2)
    pct = (estimated_score / max_score) * 100.0

    if pct >= 90:
        badge = "🥇 Derece Adayı (Şampiyon)"
    elif pct >= 75:
        badge = "🥈 Altın Hedef"
    elif pct >= 50:
        badge = "🥉 Gümüş İlerleme"
    else:
        badge = "🌱 Başlangıç Seviyesi"

    return CalculatedScoreRead(
        exam_type=exam,
        total_correct=tot_correct,
        total_wrong=tot_wrong,
        total_net=round(total_net, 2),
        estimated_score=estimated_score,
        max_score=max_score,
        badge=badge,
    )
