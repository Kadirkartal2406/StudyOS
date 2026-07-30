"""
StudyOS — ÖSYM Tahmini Puan Hesaplama Motoru (Sınav & Ders bazlı ÖSYM ve hesaplama.net standartları)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SubjectNetInput(BaseModel):
    subject_code: str
    correct_count: int = Field(default=0, ge=0)
    wrong_count: int = Field(default=0, ge=0)


class CalculateScoreRequest(BaseModel):
    exam_type: str = "kpss"
    inputs: list[SubjectNetInput]


class CalculatedScoreRead(BaseModel):
    exam_type: str
    total_correct: int
    total_wrong: int
    total_net: float
    estimated_score: float
    badge: str
    disclaimer: str = (
        "Hesaplanan değer ÖSYM katsayıları temel alınarak hesaplanmış Tahmini Puan'dır. Kesin ÖSYM sınav sonucu değildir."
    )


EXAM_SUBJECT_LIMITS: dict[str, dict[str, int]] = {
    "kpss": {
        "kpss_turkce": 30,
        "kpss_matematik": 30,
        "kpss_tarih": 27,
        "kpss_cografya": 18,
        "kpss_vatandaslik": 15,
    },
    "tyt": {
        "tyt_turkce": 40,
        "tyt_matematik": 40,
        "tyt_sosyal": 20,
        "tyt_fen": 20,
    },
    "ayt": {
        "ayt_matematik": 40,
        "ayt_fen": 40,
        "ayt_edebiyat_sos1": 40,
        "ayt_sos2": 40,
    },
    "lgs": {
        "lgs_turkce": 20,
        "lgs_matematik": 20,
        "lgs_fen": 20,
        "lgs_inkilap": 10,
        "lgs_din": 10,
        "lgs_ingilizce": 10,
    },
}


def compute_net(correct: int, wrong: int, penalty: float = 4.0) -> float:
    net = correct - (wrong / penalty)
    return max(0.0, net)


def calculate_osym_score(
    exam_type: str, inputs: list[SubjectNetInput]
) -> CalculatedScoreRead:
    exam = exam_type.lower()
    penalty = 3.0 if exam == "lgs" else 4.0

    total_correct = 0
    total_wrong = 0
    total_net = 0.0

    for inp in inputs:
        total_correct += inp.correct_count
        total_wrong += inp.wrong_count
        net = compute_net(inp.correct_count, inp.wrong_count, penalty)
        total_net += net

    estimated_score = 0.0

    if exam == "kpss":
        # KPSS P3 Standard Base 40.0 + (Net * 0.50)
        estimated_score = round(min(100.0, max(40.0, 40.0 + (total_net * 0.50))), 2)
    elif exam == "tyt":
        # TYT Base 100.0 + (Net * 3.33)
        estimated_score = round(min(500.0, max(100.0, 100.0 + (total_net * 3.33))), 2)
    elif exam == "ayt":
        # AYT Base 100.0 + (Net * 2.50)
        estimated_score = round(min(500.0, max(100.0, 100.0 + (total_net * 2.50))), 2)
    else:  # LGS
        # LGS Base 100.0 + (Net * 4.44)
        estimated_score = round(min(500.0, max(100.0, 100.0 + (total_net * 4.44))), 2)

    max_score = 100.0 if exam == "kpss" else 500.0
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
        total_correct=total_correct,
        total_wrong=total_wrong,
        total_net=round(total_net, 2),
        estimated_score=estimated_score,
        badge=badge,
    )
