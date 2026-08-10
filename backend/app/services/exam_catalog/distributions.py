"""
Single source of truth — official subject quotas + topic distribution metadata.

Subject totals come from official booklet headers / PDF section boundaries
(see data/analysis/*/verification.json and data/official_exams).

Topic avg_q / qmin / qmax / importance:
- source=\"official\" when derived from multi-year classification in
  data/analysis/*/aggregates.json (topic_distributions.stats).
- source=\"estimated\" when classification residual is high or no reliable
  per-topic evidence exists. Estimated values are study-structure weights only;
  booklet section sizes must use SUBJECT_QUOTAS / exam_question_blueprint —
  never sum(topic avg_q).

Do not store copyrighted stems here.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

# ── Official subject quotas (booklet) ─────────────────────────
# Values are questions per sitting for that exam/variant.

SUBJECT_QUOTAS: dict[str, dict[str, int]] = {
    "kpss_lisans": {
        "kpss_turkce": 30,
        "kpss_matematik": 30,
        "kpss_tarih": 27,
        "kpss_cografya": 18,
        "kpss_vatandaslik": 9,
        "kpss_guncel": 6,
    },
    "kpss_onlisans": {
        "kpss_turkce": 30,
        "kpss_matematik": 30,
        "kpss_tarih": 27,
        "kpss_cografya": 18,
        "kpss_vatandaslik": 9,
        "kpss_guncel": 6,
    },
    "kpss_ortaogretim": {
        "kpss_turkce": 30,
        "kpss_matematik": 30,
        "kpss_tarih": 27,
        "kpss_cografya": 18,
        "kpss_vatandaslik": 9,
        "kpss_guncel": 6,
    },
    # Measurement evidence: vatandaşlık block = 15 combined; product keeps
    # vatandaşlık/güncel split for study UX (9+6).
    "tyt": {
        "tyt_turkce": 40,
        "tyt_matematik": 30,
        "tyt_geometri": 10,
        "tyt_tarih": 5,
        "tyt_cografya": 5,
        "tyt_felsefe": 5,
        "tyt_din": 5,
        "tyt_fizik": 7,
        "tyt_kimya": 7,
        "tyt_biyoloji": 6,
    },
    "ayt_sayisal": {
        "ayt_matematik": 30,
        "ayt_geometri": 10,
        "ayt_fizik": 14,
        "ayt_kimya": 13,
        "ayt_biyoloji": 13,
    },
    "ayt_ea": {
        "ayt_matematik": 30,
        "ayt_geometri": 10,
        "ayt_edebiyat": 24,
        "ayt_tarih_1": 10,
        "ayt_cografya_1": 6,
    },
    "ayt_sozel": {
        "ayt_edebiyat": 24,
        "ayt_tarih_1": 10,
        "ayt_cografya_1": 6,
        "ayt_tarih_2": 11,
        "ayt_cografya_2": 11,
        "ayt_felsefe": 12,
        "ayt_din": 6,
    },
    "ydt_ingilizce": {"ydt_ingilizce": 80},
    "lgs_sayisal": {"lgs_matematik": 20, "lgs_fen": 20},
    "lgs_sozel": {
        "lgs_turkce": 20,
        "lgs_inkilap": 10,
        "lgs_din": 10,
        "lgs_ingilizce": 10,
    },
    # Combined product view (planner fallback when branch unset)
    "lgs": {
        "lgs_turkce": 20,
        "lgs_matematik": 20,
        "lgs_fen": 20,
        "lgs_inkilap": 10,
        "lgs_din": 10,
        "lgs_ingilizce": 10,
    },
    "ags": {"ags_turkce": 40, "ags_matematik": 40},
    "ales_sayisal": {"ales_sayisal": 50},
    "ales_sozel": {"ales_sozel": 50},
    "ales": {"ales_sayisal": 50, "ales_sozel": 50},
    "dgs_sayisal": {"dgs_sayisal": 60},
    "dgs_sozel": {"dgs_sozel": 60},
    "dgs": {"dgs_sayisal": 60, "dgs_sozel": 60},
    "yds_ingilizce": {"yds_ingilizce": 80},
    "yokdil_fen": {"yokdil_ingilizce": 80},
    "yokdil_saglik": {"yokdil_ingilizce": 80},
    "yokdil_sosyal": {"yokdil_ingilizce": 80},
    "yokdil_ingilizce": {"yokdil_ingilizce": 80},
}

EXAM_TOTALS: dict[str, int] = {
    k: sum(v.values()) for k, v in SUBJECT_QUOTAS.items()
}


def subject_quota(exam_key: str, subject_code: str) -> int | None:
    table = SUBJECT_QUOTAS.get(exam_key) or {}
    return table.get(subject_code)


def exam_total(exam_key: str) -> int | None:
    return EXAM_TOTALS.get(exam_key)


# ── Topic evidence (mean / min / max per exam sitting) ────────
# Keys: analysis topic slug OR product topic slug under subject.
# importance is relative within subject (0–1), derived from mean share.

TopicMeta = dict[str, Any]


def _t(
    avg: float,
    qmin: int,
    qmax: int,
    *,
    importance: float | None = None,
    source: str = "official",
    difficulty: float = 0.5,
    minutes: int | None = None,
) -> TopicMeta:
    imp = importance if importance is not None else min(1.0, max(0.35, avg / 10.0))
    mins = minutes if minutes is not None else max(15, int(round(avg * 8)))
    return {
        "importance_score": round(imp, 2),
        "average_question_count": float(avg),
        "question_range_min": int(qmin),
        "question_range_max": int(qmax),
        "difficulty_score": difficulty,
        "estimated_study_minutes": mins,
        "revision_cost": 1.0,
        "assessment_weight": round(imp, 2),
        "knowledge_tags": [],
        "aliases": [],
        "source": source,
    }


def _est(
    avg: float,
    qmin: int,
    qmax: int,
    *,
    importance: float = 0.7,
    difficulty: float = 0.5,
    minutes: int | None = None,
) -> TopicMeta:
    return _t(
        avg,
        qmin,
        qmax,
        importance=importance,
        source="estimated",
        difficulty=difficulty,
        minutes=minutes,
    )


# Evidence notes (n_exams / uncertain rates) live in TOPIC_EVIDENCE_NOTES.
TOPIC_EVIDENCE_NOTES: dict[str, str] = {
    "kpss": (
        "3 PDFs/variant; subject quotas stable 30/30/27/18/15. "
        "Türkçe/Matematik topic classifiers leave large uncertain residual — "
        "paragraf/geometri means are official; other fine topics estimated."
    ),
    "tyt": (
        "3 PDFs 2024–2026; booklet Türkçe 40, Temel Matematik 40, Sosyal 20, Fen 20. "
        "Product splits Mat/Geo and Sosyal/Fen subjects. High uncertain in math/turkce."
    ),
    "ayt": "3 AYT booklets; branch slices Mat+Fen / TDE+Mat / TDE+SB2.",
    "ydt_ingilizce": (
        "3 EN PDFs; 80Q. Classifier residual ~50% uncertain — keep coarse type weights "
        "with explicit uncertain topic."
    ),
    "lgs": "6 PDFs (3 sayısal + 3 sözel); quotas 20/20 and 20/10/10/10.",
    "dgs": "2 PDFs; 60+60. Large uncertain in both sections.",
    "ags": "2 PDFs; Türkçe 40 + Matematik 40 (parsed_metadata).",
    "ales": "Official 50+50; parsed subject tags noisy — section quotas only official.",
    "yds_yokdil": "80Q English booklets; subtype classifiers weak — coarse + uncertain.",
}


# Per-variant topic tables: subject_code → list[(slug, name, TopicMeta)]
# Only override topics we have evidence for; seed merges with estimated defaults.

def _kpss_topics(variant: str) -> dict[str, list[tuple[str, str, TopicMeta]]]:
    """Variant-specific KPSS topic evidence from aggregates.json."""
    # Means from data/analysis/kpss/aggregates.json topic_distributions.stats
    if variant == "lisans":
        turkce = [
            ("paragraf", "Paragraf", _t(17.33, 16, 18, importance=1.0, difficulty=0.55, minutes=90)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(11.67, 11, 13, importance=0.55, difficulty=0.5, minutes=50)),
            ("sozcukte_anlam", "Sözcükte Anlam", _est(1.0, 0, 2, importance=0.7)),
            ("cumlede_anlam", "Cümlede Anlam", _est(1.0, 0, 2, importance=0.75)),
            ("yazim", "Yazım", _est(0.5, 0, 1, importance=0.55)),
            ("noktalama", "Noktalama", _est(0.5, 0, 1, importance=0.55)),
            ("anlatim_bozukluklari", "Anlatım Bozuklukları", _est(0.5, 0, 2, importance=0.6)),
            ("dil_bilgisi", "Dil Bilgisi", _est(1.0, 0, 2, importance=0.65)),
        ]
        mat = [
            ("geometri", "Geometri", _t(17.67, 15, 20, importance=1.0, difficulty=0.55, minutes=80)),
            ("temel_matematik", "Temel Matematik / İşlem", _t(4.67, 4, 5, importance=0.85, difficulty=0.45, minutes=40)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(3.0, 2, 4, importance=0.5, difficulty=0.5, minutes=30)),
            ("problemler", "Problemler", _est(2.0, 1, 4, importance=0.9, difficulty=0.6)),
            ("yorum", "Sayısal Mantık / Tablo-Grafik", _est(1.5, 0, 3, importance=0.75)),
        ]
        tarih = [
            ("genel_tarih", "Genel Tarih", _t(16.67, 16, 17, importance=1.0, difficulty=0.5, minutes=70)),
            ("osmanli", "Osmanlı", _t(6.33, 5, 7, importance=0.85, difficulty=0.5, minutes=45)),
            ("inkilap", "İnkılap Tarihi", _t(3.33, 3, 4, importance=0.75, difficulty=0.45, minutes=30)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.7, 0, 2, importance=0.4)),
        ]
        cog = [
            ("genel_cografya", "Genel Coğrafya", _t(10.67, 10, 11, importance=1.0, difficulty=0.5, minutes=55)),
            ("harita", "Harita / Konum", _t(3.67, 3, 5, importance=0.85, difficulty=0.55, minutes=35)),
            ("iklim", "İklim", _est(1.5, 0, 3, importance=0.7)),
            ("nufus", "Nüfus ve Yerleşme", _est(1.0, 0, 2, importance=0.65)),
            ("ekonomi", "Ekonomik Coğrafya", _est(1.0, 0, 2, importance=0.65)),
        ]
        vat = [
            ("genel_vatandaslik", "Genel Vatandaşlık", _t(12.0, 11, 13, importance=1.0, difficulty=0.5, minutes=55)),
            ("anayasa", "Anayasa", _est(1.5, 1, 3, importance=0.85)),
            ("devlet_yapisi", "Devlet Yapısı", _est(1.0, 0, 2, importance=0.75)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.5, 0, 2, importance=0.4)),
        ]
        # Güncel is pedagogical split of vatandaşlık block (15−9≈6); no stable
        # independent classifier — keep estimated weights summing ~6.
        guncel = [
            ("guncel_olaylar", "Güncel Olaylar", _est(3.0, 2, 5, importance=0.9)),
            ("kultur_sanat", "Kültür Sanat", _est(1.5, 0, 3, importance=0.65)),
            ("bilim_teknoloji", "Bilim Teknoloji", _est(1.5, 0, 3, importance=0.65)),
        ]
    elif variant == "onlisans":
        turkce = [
            ("paragraf", "Paragraf", _t(15.33, 13, 18, importance=1.0, difficulty=0.55, minutes=85)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(14.33, 12, 16, importance=0.7, difficulty=0.5, minutes=60)),
            ("sozcukte_anlam", "Sözcükte Anlam", _est(0.5, 0, 2, importance=0.65)),
            ("cumlede_anlam", "Cümlede Anlam", _est(0.5, 0, 2, importance=0.7)),
            ("yazim", "Yazım", _est(0.3, 0, 1, importance=0.5)),
            ("noktalama", "Noktalama", _est(0.3, 0, 1, importance=0.5)),
            ("anlatim_bozukluklari", "Anlatım Bozuklukları", _est(0.3, 0, 1, importance=0.55)),
            ("dil_bilgisi", "Dil Bilgisi", _est(0.5, 0, 2, importance=0.6)),
        ]
        mat = [
            ("geometri", "Geometri", _t(19.67, 17, 23, importance=1.0, difficulty=0.55, minutes=85)),
            ("temel_matematik", "Temel Matematik / İşlem", _t(3.33, 3, 4, importance=0.8, difficulty=0.45, minutes=35)),
            ("problemler", "Problemler", _t(2.67, 1, 5, importance=0.9, difficulty=0.6, minutes=40)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(2.0, 0, 4, importance=0.45)),
            ("yorum", "Sayısal Mantık / Tablo-Grafik", _est(1.5, 0, 3, importance=0.7)),
        ]
        tarih = [
            ("genel_tarih", "Genel Tarih", _t(18.67, 18, 19, importance=1.0, difficulty=0.5, minutes=75)),
            ("osmanli", "Osmanlı", _t(6.33, 5, 7, importance=0.85, difficulty=0.5, minutes=45)),
            ("inkilap", "İnkılap Tarihi", _t(1.67, 1, 3, importance=0.65, difficulty=0.45, minutes=25)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.3, 0, 1, importance=0.35)),
        ]
        cog = [
            ("genel_cografya", "Genel Coğrafya", _t(11.33, 10, 12, importance=1.0, difficulty=0.5, minutes=55)),
            ("harita", "Harita / Konum", _t(3.33, 2, 5, importance=0.8, difficulty=0.55, minutes=35)),
            ("iklim", "İklim", _est(1.5, 0, 3, importance=0.7)),
            ("nufus", "Nüfus ve Yerleşme", _est(1.0, 0, 2, importance=0.65)),
            ("ekonomi", "Ekonomik Coğrafya", _est(1.0, 0, 2, importance=0.65)),
        ]
        vat = [
            ("genel_vatandaslik", "Genel Vatandaşlık", _t(12.33, 12, 13, importance=1.0, difficulty=0.5, minutes=55)),
            ("anayasa", "Anayasa", _t(2.0, 2, 2, importance=0.85, difficulty=0.55, minutes=30)),
            ("devlet_yapisi", "Devlet Yapısı", _est(0.5, 0, 2, importance=0.7)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.2, 0, 1, importance=0.35)),
        ]
        guncel = [
            ("guncel_olaylar", "Güncel Olaylar", _est(3.0, 2, 5, importance=0.9)),
            ("kultur_sanat", "Kültür Sanat", _est(1.5, 0, 3, importance=0.65)),
            ("bilim_teknoloji", "Bilim Teknoloji", _est(1.5, 0, 3, importance=0.65)),
        ]
    else:  # ortaogretim
        turkce = [
            ("uncertain", "Sınıflanamayan / Diğer", _t(15.0, 14, 17, importance=0.75, difficulty=0.5, minutes=60)),
            ("paragraf", "Paragraf", _t(14.67, 13, 16, importance=1.0, difficulty=0.55, minutes=80)),
            ("sozcukte_anlam", "Sözcükte Anlam", _est(0.3, 0, 1, importance=0.6)),
            ("cumlede_anlam", "Cümlede Anlam", _est(0.3, 0, 1, importance=0.65)),
            ("yazim", "Yazım", _est(0.2, 0, 1, importance=0.5)),
            ("noktalama", "Noktalama", _est(0.2, 0, 1, importance=0.5)),
            ("anlatim_bozukluklari", "Anlatım Bozuklukları", _est(0.2, 0, 1, importance=0.55)),
            ("dil_bilgisi", "Dil Bilgisi", _est(0.3, 0, 1, importance=0.6)),
        ]
        mat = [
            ("geometri", "Geometri", _t(20.67, 20, 22, importance=1.0, difficulty=0.55, minutes=90)),
            ("temel_matematik", "Temel Matematik / İşlem", _t(4.33, 3, 7, importance=0.85, difficulty=0.45, minutes=40)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(2.5, 1, 4, importance=0.45)),
            ("problemler", "Problemler", _est(1.5, 0, 3, importance=0.85)),
            ("yorum", "Sayısal Mantık / Tablo-Grafik", _est(1.0, 0, 2, importance=0.7)),
        ]
        tarih = [
            ("genel_tarih", "Genel Tarih", _t(18.67, 18, 19, importance=1.0, difficulty=0.5, minutes=75)),
            ("osmanli", "Osmanlı", _t(4.0, 3, 5, importance=0.8, difficulty=0.5, minutes=35)),
            ("inkilap", "İnkılap Tarihi", _t(3.67, 3, 4, importance=0.8, difficulty=0.45, minutes=30)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.7, 0, 2, importance=0.4)),
        ]
        cog = [
            ("genel_cografya", "Genel Coğrafya", _t(12.33, 12, 13, importance=1.0, difficulty=0.5, minutes=60)),
            ("iklim", "İklim", _t(2.33, 1, 3, importance=0.75, difficulty=0.45, minutes=25)),
            ("harita", "Harita / Konum", _t(2.0, 1, 3, importance=0.75, difficulty=0.55, minutes=25)),
            ("nufus", "Nüfus ve Yerleşme", _est(0.7, 0, 2, importance=0.6)),
            ("ekonomi", "Ekonomik Coğrafya", _est(0.7, 0, 2, importance=0.6)),
        ]
        vat = [
            ("genel_vatandaslik", "Genel Vatandaşlık", _t(12.33, 12, 13, importance=1.0, difficulty=0.5, minutes=55)),
            ("anayasa", "Anayasa", _est(1.5, 1, 3, importance=0.85)),
            ("devlet_yapisi", "Devlet Yapısı", _est(0.7, 0, 2, importance=0.7)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.5, 0, 2, importance=0.4)),
        ]
        guncel = [
            ("guncel_olaylar", "Güncel Olaylar", _est(3.0, 2, 5, importance=0.9)),
            ("kultur_sanat", "Kültür Sanat", _est(1.5, 0, 3, importance=0.65)),
            ("bilim_teknoloji", "Bilim Teknoloji", _est(1.5, 0, 3, importance=0.65)),
        ]

    return {
        "kpss_turkce": turkce,
        "kpss_matematik": mat,
        "kpss_tarih": tarih,
        "kpss_cografya": cog,
        "kpss_vatandaslik": vat,
        "kpss_guncel": guncel,
    }


def _lgs_sayisal_topics() -> dict[str, list[tuple[str, str, TopicMeta]]]:
    return {
        "lgs_matematik": [
            ("geometri", "Geometri", _t(8.67, 7, 11, importance=1.0, difficulty=0.55, minutes=50)),
            ("veri", "Veri / Grafik-Tablo", _t(4.0, 4, 4, importance=0.85, difficulty=0.5, minutes=30)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(3.0, 2, 5, importance=0.55, difficulty=0.5, minutes=25)),
            ("sayilar", "Sayılar / Temel Kavramlar", _t(2.33, 1, 4, importance=0.75, difficulty=0.4, minutes=25)),
            ("cebir", "Cebir", _t(0.67, 0, 2, importance=0.6, difficulty=0.55, minutes=20)),
            ("problemler", "Senaryo / Problem", _t(0.33, 0, 1, importance=0.55, difficulty=0.55, minutes=15)),
        ],
        "lgs_fen": [
            ("fizik", "Fizik", _t(9.67, 7, 12, importance=1.0, difficulty=0.55, minutes=50)),
            ("biyoloji", "Biyoloji", _t(4.67, 3, 8, importance=0.85, difficulty=0.5, minutes=35)),
            ("kimya", "Kimya", _t(2.0, 1, 3, importance=0.75, difficulty=0.5, minutes=25)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(2.0, 2, 2, importance=0.5, difficulty=0.5, minutes=20)),
            ("deney", "Deney / Veri Yorum", _t(1.67, 1, 2, importance=0.7, difficulty=0.55, minutes=20)),
        ],
    }


def _lgs_sozel_topics() -> dict[str, list[tuple[str, str, TopicMeta]]]:
    return {
        "lgs_turkce": [
            ("paragraf", "Paragraf", _t(9.33, 5, 12, importance=1.0, difficulty=0.5, minutes=50)),
            ("dil_bilgisi", "Dil Bilgisi", _t(8.0, 5, 12, importance=0.95, difficulty=0.5, minutes=45)),
            ("sozcuk", "Sözcükte Anlam", _t(2.0, 1, 3, importance=0.7, difficulty=0.35, minutes=20)),
            ("cumle", "Cümlede Anlam", _t(0.33, 0, 1, importance=0.5, difficulty=0.4, minutes=15)),
            ("uncertain", "Sınıflanamayan / Diğer", _est(0.3, 0, 1, importance=0.35)),
        ],
        "lgs_inkilap": [
            ("inkilaplar", "İnkılap / Atatürk İlkeleri", _t(7.0, 5, 9, importance=1.0, difficulty=0.45, minutes=40)),
            ("milli_mucadele", "Osmanlı Geçiş / Milli Mücadele", _t(1.67, 0, 3, importance=0.7, difficulty=0.45, minutes=20)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(0.67, 0, 1, importance=0.4, difficulty=0.4, minutes=15)),
        ],
        "lgs_din": [
            ("uncertain", "Sınıflanamayan / Diğer", _t(5.0, 4, 6, importance=0.7, difficulty=0.4, minutes=25)),
            ("inanc", "İnanç / Din ve Ahlak", _t(5.0, 4, 6, importance=0.9, difficulty=0.35, minutes=25)),
            ("ibadet", "İbadet", _est(0.0, 0, 1, importance=0.4)),
        ],
        "lgs_ingilizce": [
            ("reading", "Reading / Meaning", _t(7.67, 7, 8, importance=1.0, difficulty=0.5, minutes=35)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(2.0, 2, 2, importance=0.55, difficulty=0.45, minutes=20)),
            ("vocabulary", "Vocabulary", _est(0.3, 0, 1, importance=0.5)),
            ("grammar", "Grammar", _est(0.0, 0, 1, importance=0.45)),
        ],
    }


def _dgs_topics(section: str) -> dict[str, list[tuple[str, str, TopicMeta]]]:
    if section == "sayisal":
        return {
            "dgs_sayisal": [
                ("uncertain", "Sınıflanamayan / Diğer", _t(29.0, 26, 32, importance=0.7, difficulty=0.55, minutes=90)),
                ("geometri", "Geometri", _t(15.0, 14, 16, importance=1.0, difficulty=0.55, minutes=70)),
                ("temel_matematik", "Sayısal İşlem", _t(11.0, 10, 12, importance=0.95, difficulty=0.5, minutes=55)),
                ("yorum", "Analitik Mantık", _t(2.5, 2, 3, importance=0.75, difficulty=0.6, minutes=30)),
                ("veri", "Tablo / Grafik", _t(2.5, 1, 4, importance=0.7, difficulty=0.55, minutes=25)),
            ]
        }
    return {
        "dgs_sozel": [
            ("paragraf", "Paragraf", _t(25.5, 22, 29, importance=1.0, difficulty=0.55, minutes=90)),
            ("uncertain", "Sınıflanamayan / Diğer", _t(24.0, 22, 26, importance=0.75, difficulty=0.5, minutes=80)),
            ("cumle", "Cümlede Anlam", _t(6.0, 6, 6, importance=0.8, difficulty=0.45, minutes=35)),
            ("anlatim", "Analitik İfade", _t(4.5, 3, 6, importance=0.75, difficulty=0.55, minutes=30)),
        ]
    }


def _yd_language_topics(subject_code: str, *, uncertain_mean: float) -> list[tuple[str, str, TopicMeta]]:
    """Coarse English-test types. High uncertain → explicit residual."""
    # Remaining mass after uncertain for known types (YDT evidence)
    known = max(0.0, 80.0 - uncertain_mean)
    # YDT means: translation ~32, reading ~6.3, vocab ~1.3, dialogue ~0.3
    translation = min(32.0, known * 0.7)
    reading = min(6.5, known * 0.15)
    vocab = min(2.0, known * 0.05)
    dialogue = min(1.0, known * 0.02)
    rest = max(0.0, known - translation - reading - vocab - dialogue)
    return [
        ("uncertain", "Sınıflanamayan / Diğer", _t(uncertain_mean, int(uncertain_mean - 2), int(uncertain_mean + 2), importance=0.6, difficulty=0.55, minutes=70)),
        ("translation", "Translation", _t(translation, max(0, int(translation - 3)), int(translation + 3), importance=1.0, difficulty=0.6, minutes=70)),
        ("reading", "Reading", _t(reading, max(0, int(reading - 1)), int(reading + 2), importance=0.95, difficulty=0.65, minutes=50)),
        ("vocabulary", "Vocabulary", _t(vocab, 0, max(2, int(vocab + 1)), importance=0.75, difficulty=0.5, minutes=25)),
        ("dialogue", "Dialogue", _t(dialogue, 0, max(1, int(dialogue + 1)), importance=0.55, difficulty=0.45, minutes=20)),
        ("grammar", "Grammar / Cloze", _est(rest * 0.4, 0, max(2, int(rest * 0.5)), importance=0.7)),
        ("cloze_test", "Cloze Test", _est(rest * 0.3, 0, max(2, int(rest * 0.4)), importance=0.7)),
        ("sentence_completion", "Sentence Completion", _est(rest * 0.15, 0, max(1, int(rest * 0.25)), importance=0.65)),
        ("meaning", "Meaning / Restatement", _est(rest * 0.15, 0, max(1, int(rest * 0.25)), importance=0.65)),
    ]


def _ags_topics() -> dict[str, list[tuple[str, str, TopicMeta]]]:
    # Parsed metadata collapses topics to paragraf/problemler — treat as coarse
    # official weights with study subtopics estimated underneath.
    return {
        "ags_turkce": [
            ("paragraf", "Paragraf", _t(22.0, 18, 26, importance=1.0, difficulty=0.55, minutes=90)),
            ("sozcukte_anlam", "Sözcükte Anlam", _est(4.0, 2, 6, importance=0.75)),
            ("cumlede_anlam", "Cümlede Anlam", _est(4.0, 2, 6, importance=0.8)),
            ("dil_bilgisi", "Dil Bilgisi", _est(4.0, 2, 6, importance=0.7)),
            ("anlatim_bozukluklari", "Anlatım Bozuklukları", _est(3.0, 1, 5, importance=0.65)),
            ("yazim_noktalama", "Yazım ve Noktalama", _est(3.0, 1, 5, importance=0.6)),
        ],
        "ags_matematik": [
            ("problemler", "Problemler", _t(18.0, 14, 22, importance=1.0, difficulty=0.6, minutes=90)),
            ("temel_matematik", "Temel Matematik", _est(10.0, 6, 14, importance=0.9)),
            ("geometri", "Geometri", _est(6.0, 3, 10, importance=0.8)),
            ("yorum", "Sayısal Mantık", _est(6.0, 3, 10, importance=0.8)),
        ],
    }


def _ales_topics(section: str) -> dict[str, list[tuple[str, str, TopicMeta]]]:
    # Official section size 50; subtype mix estimated (parsed labels noisy).
    if section == "sayisal":
        return {
            "ales_sayisal": [
                ("temel_matematik", "Temel Matematik", _est(14.0, 10, 18, importance=0.9)),
                ("problemler", "Problemler", _est(16.0, 12, 20, importance=1.0, difficulty=0.6)),
                ("geometri", "Geometri", _est(10.0, 6, 14, importance=0.85)),
                ("yorum", "Sayısal Mantık", _est(10.0, 6, 14, importance=0.85)),
            ]
        }
    return {
        "ales_sozel": [
            ("paragraf", "Paragraf", _est(18.0, 14, 22, importance=1.0)),
            ("sozcuk", "Sözcükte Anlam", _est(10.0, 6, 14, importance=0.85)),
            ("cumle", "Cümlede Anlam", _est(12.0, 8, 16, importance=0.9)),
            ("anlatim", "Anlatım / Mantık", _est(10.0, 6, 14, importance=0.8)),
        ]
    }


def topic_table_for(exam_key: str) -> dict[str, list[tuple[str, str, TopicMeta]]]:
    """Return subject → topics for a canonical distribution key."""
    if exam_key.startswith("kpss_"):
        return _kpss_topics(exam_key.removeprefix("kpss_"))
    if exam_key == "lgs_sayisal":
        return _lgs_sayisal_topics()
    if exam_key == "lgs_sozel":
        return _lgs_sozel_topics()
    if exam_key == "dgs_sayisal":
        return _dgs_topics("sayisal")
    if exam_key == "dgs_sozel":
        return _dgs_topics("sozel")
    if exam_key == "ags":
        return _ags_topics()
    if exam_key == "ales_sayisal":
        return _ales_topics("sayisal")
    if exam_key == "ales_sozel":
        return _ales_topics("sozel")
    if exam_key == "ydt_ingilizce":
        return {"ydt_ingilizce": _yd_language_topics("ydt_ingilizce", uncertain_mean=40.0)}
    if exam_key == "yds_ingilizce":
        # No reliable multi-year subtype stats in analysis/; keep estimated mix + residual.
        return {
            "yds_ingilizce": [
                ("uncertain", "Sınıflanamayan / Diğer", _est(20.0, 10, 30, importance=0.55)),
                ("reading", "Reading", _est(18.0, 12, 25, importance=1.0, difficulty=0.65)),
                ("vocabulary", "Vocabulary", _est(10.0, 6, 14, importance=0.85)),
                ("grammar", "Grammar", _est(8.0, 5, 12, importance=0.8)),
                ("cloze_test", "Cloze Test", _est(8.0, 5, 12, importance=0.8)),
                ("translation", "Translation", _est(6.0, 3, 10, importance=0.75)),
                ("dialogue", "Dialogue", _est(4.0, 2, 6, importance=0.65)),
                ("sentence_completion", "Sentence Completion", _est(3.0, 1, 5, importance=0.65)),
                ("meaning", "Meaning / Restatement", _est(3.0, 1, 5, importance=0.65)),
            ]
        }
    if exam_key.startswith("yokdil"):
        return {
            "yokdil_ingilizce": [
                ("uncertain", "Sınıflanamayan / Diğer", _est(18.0, 10, 28, importance=0.55)),
                ("reading", "Reading / Academic Passage", _est(30.0, 22, 40, importance=1.0, difficulty=0.65)),
                ("vocabulary", "Vocabulary", _est(12.0, 8, 16, importance=0.85)),
                ("grammar", "Grammar / Cloze", _est(10.0, 6, 14, importance=0.8)),
                ("translation", "Translation", _est(5.0, 2, 8, importance=0.7)),
                ("meaning", "Meaning / Restatement", _est(5.0, 2, 8, importance=0.7)),
            ]
        }
    return {}


def blueprint_sections(exam_key: str) -> list[tuple[str, int]]:
    """Ordered (subject_code, count) for booklet blueprints."""
    quotas = SUBJECT_QUOTAS.get(exam_key)
    if not quotas:
        return []
    # Stable pedagogical order
    order_prefs = [
        "kpss_turkce",
        "kpss_matematik",
        "kpss_tarih",
        "kpss_cografya",
        "kpss_vatandaslik",
        "kpss_guncel",
        "tyt_turkce",
        "tyt_matematik",
        "tyt_geometri",
        "tyt_tarih",
        "tyt_cografya",
        "tyt_felsefe",
        "tyt_din",
        "tyt_fizik",
        "tyt_kimya",
        "tyt_biyoloji",
        "ayt_matematik",
        "ayt_geometri",
        "ayt_fizik",
        "ayt_kimya",
        "ayt_biyoloji",
        "ayt_edebiyat",
        "ayt_tarih_1",
        "ayt_cografya_1",
        "ayt_tarih_2",
        "ayt_cografya_2",
        "ayt_felsefe",
        "ayt_din",
        "ydt_ingilizce",
        "lgs_turkce",
        "lgs_matematik",
        "lgs_fen",
        "lgs_inkilap",
        "lgs_din",
        "lgs_ingilizce",
        "ags_turkce",
        "ags_matematik",
        "ales_sayisal",
        "ales_sozel",
        "dgs_sayisal",
        "dgs_sozel",
        "yds_ingilizce",
        "yokdil_ingilizce",
    ]
    out: list[tuple[str, int]] = []
    seen: set[str] = set()
    for code in order_prefs:
        if code in quotas:
            out.append((code, quotas[code]))
            seen.add(code)
    for code, n in quotas.items():
        if code not in seen:
            out.append((code, n))
    return out


def resolve_quota_key(exam: str, branch: str | None = None) -> str:
    """Map runtime exam+branch to SUBJECT_QUOTAS key."""
    from app.core.exam_identity import canonicalize_exam_type

    e = (exam or "").strip().lower()
    b = (branch or "").strip().lower() or None
    canonical = canonicalize_exam_type(e, b)

    # Branch-specific keys first (must not fall through to umbrella quotas)
    if (canonical == "lgs" or e == "lgs") and b in {"sayisal", "sozel"}:
        return f"lgs_{b}"
    if (canonical == "ales" or e == "ales") and b in {"sayisal", "sozel"}:
        return f"ales_{b}"
    if (canonical == "dgs" or e == "dgs") and b in {"sayisal", "sozel"}:
        return f"dgs_{b}"
    if e in {"yokdil", "yokdil_ingilizce"} and b in {"fen", "saglik", "sosyal"}:
        return f"yokdil_{b}"
    if e == "ayt" and b in {"sayisal", "ea", "sozel"}:
        return f"ayt_{b}"
    if e == "kpss" and b in {"lisans", "onlisans", "ortaogretim"}:
        return f"kpss_{b}"
    if e == "yks" and b in {"en", "dil"}:
        return "ydt_ingilizce"

    if canonical.startswith("kpss_"):
        return canonical
    if canonical.startswith("ayt_"):
        return canonical
    if canonical in SUBJECT_QUOTAS:
        return canonical
    return canonical


def deep_copy_topics(
    table: dict[str, list[tuple[str, str, TopicMeta]]],
) -> dict[str, list[tuple[str, str, TopicMeta]]]:
    return {k: [(a, b, deepcopy(c)) for a, b, c in rows] for k, rows in table.items()}
