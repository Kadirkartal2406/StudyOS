"""Exam Intelligence seed — resmi sınav ağacı + konu metadata.

source=official: ÖSYM/MEB/YÖK dağılımına dayalı.
source=estimated: yayın istatistikleri / ortak dağılım tahmini.
"""

from __future__ import annotations

from typing import Any


def _meta(
    *,
    importance: float,
    avg_q: float,
    qmin: int,
    qmax: int,
    difficulty: float,
    minutes: int,
    source: str = "estimated",
    tags: list[str] | None = None,
    aliases: list[str] | None = None,
    revision_cost: float = 1.0,
    assessment_weight: float | None = None,
) -> dict[str, Any]:
    return {
        "importance_score": importance,
        "average_question_count": avg_q,
        "question_range_min": qmin,
        "question_range_max": qmax,
        "difficulty_score": difficulty,
        "estimated_study_minutes": minutes,
        "revision_cost": revision_cost,
        "assessment_weight": assessment_weight if assessment_weight is not None else importance,
        "knowledge_tags": tags or [],
        "aliases": aliases or [],
        "source": source,
    }


def _topics(
    subject_code: str,
    items: list[tuple[str, str, dict[str, Any]]],
    *,
    legacy_prefix: str | None = None,
) -> list[dict[str, Any]]:
    """items: (slug, name, meta)."""
    out: list[dict[str, Any]] = []
    for i, (slug, name, meta) in enumerate(items, start=1):
        legacy = f"{legacy_prefix or subject_code}__{slug}"
        out.append(
            {
                "code": f"{subject_code}__{slug}",
                "name": name,
                "display_order": i * 10,
                "legacy_topic_code": legacy,
                **meta,
            }
        )
    return out


# ── Shared topic lists ────────────────────────────────────────

def _tyt_turkce(sc: str) -> list[dict[str, Any]]:
    return _topics(
        sc,
        [
            ("sozcukte_anlam", "Sözcükte Anlam", _meta(importance=0.85, avg_q=4, qmin=2, qmax=6, difficulty=0.35, minutes=40, source="estimated", tags=["anlam"])),
            ("cumlede_anlam", "Cümlede Anlam", _meta(importance=0.9, avg_q=5, qmin=3, qmax=7, difficulty=0.45, minutes=45, source="estimated")),
            ("paragraf", "Paragraf", _meta(importance=1.0, avg_q=10, qmin=8, qmax=14, difficulty=0.55, minutes=90, source="estimated", tags=["paragraf"])),
            ("anlatim_bozukluklari", "Anlatım Bozuklukları", _meta(importance=0.7, avg_q=3, qmin=1, qmax=4, difficulty=0.5, minutes=35, source="estimated")),
            ("yazim", "Yazım Kuralları", _meta(importance=0.65, avg_q=2, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
            ("noktalama", "Noktalama", _meta(importance=0.65, avg_q=2, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
            ("ses_bilgisi", "Ses Bilgisi", _meta(importance=0.5, avg_q=1, qmin=0, qmax=2, difficulty=0.45, minutes=20, source="estimated")),
            ("dil_bilgisi", "Dil Bilgisi", _meta(importance=0.75, avg_q=4, qmin=2, qmax=6, difficulty=0.55, minutes=50, source="estimated")),
        ],
        legacy_prefix="tyt_turkce",
    )


def _tyt_matematik(sc: str) -> list[dict[str, Any]]:
    return _topics(
        sc,
        [
            ("temel_kavramlar", "Temel Kavramlar", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.3, minutes=40, source="estimated")),
            ("sayi_basamaklari", "Sayı Basamakları", _meta(importance=0.6, avg_q=1, qmin=0, qmax=2, difficulty=0.35, minutes=25, source="estimated")),
            ("bolme_bolunebilme", "Bölme Bölünebilme", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.4, minutes=30, source="estimated")),
            ("obeb_okek", "OBEB OKEK", _meta(importance=0.65, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=30, source="estimated")),
            ("rasyonel_sayilar", "Rasyonel Sayılar", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.4, minutes=30, source="estimated")),
            ("mutlak_deger", "Mutlak Değer", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.45, minutes=30, source="estimated")),
            ("uslu_sayilar", "Üslü Sayılar", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.45, minutes=35, source="estimated")),
            ("koklu_sayilar", "Köklü Sayılar", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.5, minutes=35, source="estimated")),
            ("carpanlara_ayirma", "Çarpanlara Ayırma", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("oran_oranti", "Oran Orantı", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.4, minutes=30, source="estimated")),
            ("problemler", "Problemler", _meta(importance=1.0, avg_q=6, qmin=4, qmax=8, difficulty=0.65, minutes=80, source="estimated", tags=["problem"])),
            ("kumeler", "Kümeler", _meta(importance=0.55, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=25, source="estimated")),
            ("fonksiyonlar", "Fonksiyonlar", _meta(importance=0.8, avg_q=2, qmin=1, qmax=4, difficulty=0.6, minutes=45, source="estimated")),
            ("polinomlar", "Polinomlar", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("ikinci_derece", "İkinci Dereceden Denklemler", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
            ("permutasyon_kombinasyon", "Permütasyon Kombinasyon", _meta(importance=0.65, avg_q=1.5, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
            ("olasilik", "Olasılık", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=35, source="estimated")),
        ],
        legacy_prefix="tyt_matematik",
    )


def _tyt_geometri(sc: str) -> list[dict[str, Any]]:
    return _topics(
        sc,
        [
            ("temel_geometri", "Temel Geometri", _meta(importance=0.75, avg_q=1.5, qmin=1, qmax=3, difficulty=0.4, minutes=35, source="estimated")),
            ("ucgenler", "Üçgenler", _meta(importance=0.95, avg_q=3, qmin=2, qmax=5, difficulty=0.55, minutes=50, source="estimated")),
            ("dik_ucgen", "Dik Üçgen", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
            ("cokgenler", "Çokgenler", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=35, source="estimated")),
            ("cember", "Çember", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.6, minutes=45, source="estimated")),
            ("kati_cisimler", "Katı Cisimler", _meta(importance=0.65, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("analitik", "Analitik Geometri", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
        ],
        legacy_prefix="tyt_geometri",
    )


def _tyt_fizik(sc: str) -> list[dict[str, Any]]:
    return _topics(
        sc,
        [
            ("vektorler", "Vektörler", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=30, source="estimated")),
            ("kuvvet", "Kuvvet", _meta(importance=0.85, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
            ("hareket", "Hareket", _meta(importance=0.9, avg_q=2, qmin=1, qmax=3, difficulty=0.55, minutes=45, source="estimated")),
            ("enerji", "Enerji", _meta(importance=0.85, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("isitma", "Isı ve Sıcaklık", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.45, minutes=30, source="estimated")),
            ("elektrostatik", "Elektrostatik", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.55, minutes=35, source="estimated")),
            ("akim", "Elektrik Akımı", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("manyetizma", "Manyetizma", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.6, minutes=35, source="estimated")),
            ("dalgalar", "Dalgalar", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.55, minutes=35, source="estimated")),
            ("optik", "Optik", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.55, minutes=35, source="estimated")),
        ],
        legacy_prefix="tyt_fizik",
    )


def _tyt_kimya(sc: str) -> list[dict[str, Any]]:
    return _topics(
        sc,
        [
            ("atom", "Atom ve Periyodik Sistem", _meta(importance=0.85, avg_q=1.5, qmin=1, qmax=3, difficulty=0.45, minutes=40, source="estimated")),
            ("kimyasal_turler", "Kimyasal Türler Arası Etkileşim", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
            ("mol", "Mol Kavramı", _meta(importance=0.85, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
            ("kimyasal_tepkimeler", "Kimyasal Tepkimeler", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("asitler_bazlar", "Asitler Bazlar", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.55, minutes=35, source="estimated")),
            ("karisimlar", "Karışımlar", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.45, minutes=30, source="estimated")),
            ("kimya_her_yerde", "Kimya Her Yerde", _meta(importance=0.6, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=25, source="estimated")),
        ],
        legacy_prefix="tyt_kimya",
    )


def _tyt_biyoloji(sc: str) -> list[dict[str, Any]]:
    return _topics(
        sc,
        [
            ("canlilarin_ortak", "Canlıların Ortak Özellikleri", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.35, minutes=30, source="estimated")),
            ("hucre", "Hücre", _meta(importance=0.9, avg_q=2, qmin=1, qmax=3, difficulty=0.5, minutes=45, source="estimated")),
            ("canlilarin_siniflandirilmasi", "Canlıların Sınıflandırılması", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.45, minutes=30, source="estimated")),
            ("hucresel_solunum", "Hücresel Solunum", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
            ("fotosentez", "Fotosentez", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
            ("kalitim", "Kalıtım", _meta(importance=0.85, avg_q=1.5, qmin=1, qmax=3, difficulty=0.6, minutes=45, source="estimated")),
            ("ekoloji", "Ekoloji", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.45, minutes=30, source="estimated")),
        ],
        legacy_prefix="tyt_biyoloji",
    )


def _tyt_sosyal(kind: str, sc: str) -> list[dict[str, Any]]:
    if kind == "tarih":
        return _topics(
            sc,
            [
                ("tarih_bilimi", "Tarih Bilimi", _meta(importance=0.5, avg_q=0.5, qmin=0, qmax=1, difficulty=0.3, minutes=20, source="estimated")),
                ("ilk_cag", "İlk Çağ", _meta(importance=0.65, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=30, source="estimated")),
                ("orta_cag", "Orta Çağ", _meta(importance=0.65, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=30, source="estimated")),
                ("osmanli", "Osmanlı", _meta(importance=0.85, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
                ("yakin_cag", "Yakın Çağ", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.5, minutes=35, source="estimated")),
                ("inkilap", "İnkılap Tarihi", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.45, minutes=40, source="estimated")),
            ],
            legacy_prefix="tyt_tarih",
        )
    if kind == "cografya":
        return _topics(
            sc,
            [
                ("harita", "Harita Bilgisi", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.35, minutes=25, source="estimated")),
                ("iklim", "İklim", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.45, minutes=35, source="estimated")),
                ("nufus", "Nüfus", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=30, source="estimated")),
                ("turkiye_cografyasi", "Türkiye Coğrafyası", _meta(importance=0.9, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
                ("ekonomik_cografya", "Ekonomik Coğrafya", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.5, minutes=30, source="estimated")),
            ],
            legacy_prefix="tyt_cografya",
        )
    if kind == "felsefe":
        return _topics(
            sc,
            [
                ("felsefeye_giris", "Felsefeye Giriş", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=25, source="estimated")),
                ("bilgi_felsefesi", "Bilgi Felsefesi", _meta(importance=0.75, avg_q=1, qmin=0, qmax=2, difficulty=0.5, minutes=30, source="estimated")),
                ("varlik", "Varlık Felsefesi", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.5, minutes=30, source="estimated")),
                ("ahlak", "Ahlak Felsefesi", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.45, minutes=25, source="estimated")),
                ("siyaset", "Siyaset Felsefesi", _meta(importance=0.65, avg_q=0.5, qmin=0, qmax=1, difficulty=0.5, minutes=25, source="estimated")),
            ],
            legacy_prefix="tyt_felsefe",
        )
    return _topics(
        sc,
        [
            ("inanc", "İnanç", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.35, minutes=20, source="estimated")),
            ("ibadet", "İbadet", _meta(importance=0.7, avg_q=1, qmin=0, qmax=2, difficulty=0.35, minutes=20, source="estimated")),
            ("ahlak_din", "Ahlak", _meta(importance=0.65, avg_q=0.5, qmin=0, qmax=1, difficulty=0.4, minutes=20, source="estimated")),
            ("din_ve_hayat", "Din ve Hayat", _meta(importance=0.65, avg_q=0.5, qmin=0, qmax=1, difficulty=0.4, minutes=20, source="estimated")),
        ],
        legacy_prefix="tyt_din",
    )


def _yd_language_topics(sc: str) -> list[dict[str, Any]]:
    """YDT / YDS / YÖKDİL ortak soru türleri."""
    return _topics(
        sc,
        [
            ("vocabulary", "Vocabulary", _meta(importance=0.9, avg_q=8, qmin=5, qmax=12, difficulty=0.5, minutes=60, source="estimated", tags=["vocab"])),
            ("grammar", "Grammar", _meta(importance=0.85, avg_q=6, qmin=4, qmax=10, difficulty=0.55, minutes=55, source="estimated")),
            ("reading", "Reading", _meta(importance=1.0, avg_q=10, qmin=6, qmax=15, difficulty=0.65, minutes=90, source="estimated", tags=["reading"])),
            ("dialogue", "Dialogue", _meta(importance=0.7, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
            ("translation", "Translation", _meta(importance=0.75, avg_q=4, qmin=2, qmax=6, difficulty=0.6, minutes=40, source="estimated")),
            ("cloze_test", "Cloze Test", _meta(importance=0.85, avg_q=5, qmin=3, qmax=8, difficulty=0.6, minutes=45, source="estimated")),
            ("sentence_completion", "Sentence Completion", _meta(importance=0.8, avg_q=4, qmin=2, qmax=6, difficulty=0.55, minutes=40, source="estimated")),
            ("paragraf", "Paragraph", _meta(importance=0.85, avg_q=4, qmin=2, qmax=6, difficulty=0.6, minutes=45, source="estimated")),
            ("meaning", "Meaning / Restatement", _meta(importance=0.75, avg_q=3, qmin=2, qmax=5, difficulty=0.55, minutes=35, source="estimated")),
            ("error_detection", "Error Detection", _meta(importance=0.7, avg_q=3, qmin=1, qmax=5, difficulty=0.55, minutes=30, source="estimated")),
        ],
    )


def _subject(
    code: str,
    name: str,
    order: int,
    topics: list[dict[str, Any]],
    *,
    legacy: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "name": name,
        "display_order": order,
        "legacy_subject_code": legacy or code,
        "topics": topics,
    }


def build_exam_intelligence_seed() -> list[dict[str, Any]]:
    """Tüm sınav ağacı."""
    exams: list[dict[str, Any]] = []

    # ── YKS ───────────────────────────────────────────────────
    tyt_subjects = [
        _subject("tyt_turkce", "Türkçe", 10, _tyt_turkce("tyt_turkce")),
        _subject("tyt_matematik", "Matematik", 20, _tyt_matematik("tyt_matematik")),
        _subject("tyt_geometri", "Geometri", 30, _tyt_geometri("tyt_geometri")),
        _subject("tyt_fizik", "Fizik", 40, _tyt_fizik("tyt_fizik")),
        _subject("tyt_kimya", "Kimya", 50, _tyt_kimya("tyt_kimya")),
        _subject("tyt_biyoloji", "Biyoloji", 60, _tyt_biyoloji("tyt_biyoloji")),
        _subject("tyt_tarih", "Tarih", 70, _tyt_sosyal("tarih", "tyt_tarih")),
        _subject("tyt_cografya", "Coğrafya", 80, _tyt_sosyal("cografya", "tyt_cografya")),
        _subject("tyt_felsefe", "Felsefe", 90, _tyt_sosyal("felsefe", "tyt_felsefe")),
        _subject("tyt_din", "Din Kültürü", 100, _tyt_sosyal("din", "tyt_din")),
    ]

    ayt_sayisal = [
        _subject(
            "ayt_matematik",
            "Matematik",
            10,
            _topics(
                "ayt_matematik",
                [
                    ("fonksiyonlar", "Fonksiyonlar", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.6, minutes=50, source="estimated")),
                    ("trigonometri", "Trigonometri", _meta(importance=0.85, avg_q=3, qmin=2, qmax=5, difficulty=0.65, minutes=50, source="estimated")),
                    ("limit", "Limit", _meta(importance=0.9, avg_q=3, qmin=2, qmax=4, difficulty=0.7, minutes=55, source="estimated")),
                    ("turev", "Türev", _meta(importance=1.0, avg_q=4, qmin=3, qmax=6, difficulty=0.75, minutes=70, source="estimated")),
                    ("integral", "İntegral", _meta(importance=1.0, avg_q=4, qmin=3, qmax=6, difficulty=0.8, minutes=70, source="estimated")),
                    ("logaritma", "Logaritma", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
                    ("diziler", "Diziler", _meta(importance=0.8, avg_q=2, qmin=1, qmax=4, difficulty=0.65, minutes=45, source="estimated")),
                    ("kompleks", "Kompleks Sayılar", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.7, minutes=40, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_geometri",
            "Geometri",
            20,
            _topics(
                "ayt_geometri",
                [
                    ("ucgen", "Üçgen", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.6, minutes=50, source="estimated")),
                    ("cember", "Çember", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.65, minutes=45, source="estimated")),
                    ("analitik", "Analitik Geometri", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.7, minutes=55, source="estimated")),
                    ("katilar", "Katı Cisimler", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_fizik",
            "Fizik",
            30,
            _topics(
                "ayt_fizik",
                [
                    ("kuvvet_hareket", "Kuvvet ve Hareket", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.65, minutes=55, source="estimated")),
                    ("enerji_momentum", "Enerji ve Momentum", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.65, minutes=50, source="estimated")),
                    ("elektrik", "Elektrik", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.7, minutes=55, source="estimated")),
                    ("manyetizma", "Manyetizma", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.7, minutes=45, source="estimated")),
                    ("modern_fizik", "Modern Fizik", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.75, minutes=45, source="estimated")),
                    ("dalgalar", "Dalgalar", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.65, minutes=40, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_kimya",
            "Kimya",
            40,
            _topics(
                "ayt_kimya",
                [
                    ("kimyasal_hesaplamalar", "Kimyasal Hesaplamalar", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.6, minutes=45, source="estimated")),
                    ("gazlar", "Gazlar", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.6, minutes=40, source="estimated")),
                    ("sivi_cozeltiler", "Sıvı Çözeltiler", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.65, minutes=45, source="estimated")),
                    ("kimyasal_denge", "Kimyasal Denge", _meta(importance=0.9, avg_q=2, qmin=1, qmax=4, difficulty=0.7, minutes=50, source="estimated")),
                    ("asit_baz", "Asit-Baz Dengesi", _meta(importance=0.85, avg_q=2, qmin=1, qmax=3, difficulty=0.7, minutes=45, source="estimated")),
                    ("elektrokimya", "Elektrokimya", _meta(importance=0.75, avg_q=1.5, qmin=1, qmax=3, difficulty=0.7, minutes=40, source="estimated")),
                    ("organik", "Organik Kimya", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.65, minutes=55, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_biyoloji",
            "Biyoloji",
            50,
            _topics(
                "ayt_biyoloji",
                [
                    ("hucre_bolunmesi", "Hücre Bölünmeleri", _meta(importance=0.85, avg_q=2, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
                    ("kalitim", "Kalıtım", _meta(importance=0.95, avg_q=3, qmin=2, qmax=5, difficulty=0.7, minutes=55, source="estimated")),
                    ("canli_sistemleri", "Canlılarda Enerji Dönüşümleri", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.65, minutes=45, source="estimated")),
                    ("bitki_biyolojisi", "Bitki Biyolojisi", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
                    ("insan_fizyolojisi", "İnsan Fizyolojisi", _meta(importance=0.95, avg_q=4, qmin=2, qmax=6, difficulty=0.65, minutes=70, source="estimated")),
                    ("ekoloji", "Komünite ve Popülasyon", _meta(importance=0.7, avg_q=1.5, qmin=1, qmax=3, difficulty=0.5, minutes=35, source="estimated")),
                ],
            ),
        ),
    ]

    ayt_ea = [
        _subject("ayt_matematik", "Matematik", 10, ayt_sayisal[0]["topics"], legacy="ayt_matematik"),
        _subject("ayt_geometri", "Geometri", 20, ayt_sayisal[1]["topics"], legacy="ayt_geometri"),
        _subject(
            "ayt_edebiyat",
            "Türk Dili ve Edebiyatı",
            30,
            _topics(
                "ayt_edebiyat",
                [
                    ("guzel_sanatlar", "Güzel Sanatlar ve Edebiyat", _meta(importance=0.6, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=25, source="estimated")),
                    ("siir", "Şiir Bilgisi", _meta(importance=0.85, avg_q=3, qmin=2, qmax=5, difficulty=0.55, minutes=50, source="estimated")),
                    ("nesir", "Anlatım Türleri / Nesir", _meta(importance=0.8, avg_q=2, qmin=1, qmax=4, difficulty=0.5, minutes=40, source="estimated")),
                    ("divan", "Divan Edebiyatı", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.6, minutes=55, source="estimated")),
                    ("halk", "Halk Edebiyatı", _meta(importance=0.8, avg_q=2, qmin=1, qmax=4, difficulty=0.5, minutes=40, source="estimated")),
                    ("tanzimat", "Tanzimat Edebiyatı", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.55, minutes=45, source="estimated")),
                    ("cumhuriyet", "Cumhuriyet Dönemi", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.55, minutes=50, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_tarih_1",
            "Tarih-1",
            40,
            _topics(
                "ayt_tarih_1",
                [
                    ("osmanli_kurulus", "Osmanlı Kuruluş", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.5, minutes=40, source="estimated")),
                    ("osmanli_yukselis", "Osmanlı Yükselme", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.5, minutes=45, source="estimated")),
                    ("osmanli_duraklama", "Duraklama / Gerileme", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
                    ("inkilap", "İnkılap Tarihi", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.5, minutes=50, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_cografya_1",
            "Coğrafya-1",
            50,
            _topics(
                "ayt_cografya_1",
                [
                    ("dogal_sistemler", "Doğal Sistemler", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.5, minutes=40, source="estimated")),
                    ("beseri_sistemler", "Beşeri Sistemler", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.5, minutes=40, source="estimated")),
                    ("turkiye", "Türkiye'nin Beşeri ve Ekonomik Coğrafyası", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.55, minutes=50, source="estimated")),
                ],
            ),
        ),
    ]

    ayt_sozel = [
        _subject("ayt_edebiyat", "Türk Dili ve Edebiyatı", 10, ayt_ea[2]["topics"], legacy="ayt_edebiyat"),
        _subject("ayt_tarih_1", "Tarih-1", 20, ayt_ea[3]["topics"], legacy="ayt_tarih_1"),
        _subject("ayt_cografya_1", "Coğrafya-1", 30, ayt_ea[4]["topics"], legacy="ayt_cografya_1"),
        _subject(
            "ayt_tarih_2",
            "Tarih-2",
            40,
            _topics(
                "ayt_tarih_2",
                [
                    ("xx_yuzyil", "20. Yüzyıl Başı", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.55, minutes=45, source="estimated")),
                    ("ii_dunya", "II. Dünya Savaşı ve Sonrası", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.55, minutes=45, source="estimated")),
                    ("turkiye_dis", "Türkiye'nin Dış Politikası", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.55, minutes=40, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_cografya_2",
            "Coğrafya-2",
            50,
            _topics(
                "ayt_cografya_2",
                [
                    ("bolgeler", "Bölgeler ve Ülkeler", _meta(importance=0.85, avg_q=2, qmin=1, qmax=4, difficulty=0.5, minutes=40, source="estimated")),
                    ("cevre", "Çevre ve Toplum", _meta(importance=0.8, avg_q=2, qmin=1, qmax=3, difficulty=0.5, minutes=35, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_felsefe",
            "Felsefe Grubu",
            60,
            _topics(
                "ayt_felsefe",
                [
                    ("felsefe", "Felsefe", _meta(importance=0.85, avg_q=4, qmin=2, qmax=6, difficulty=0.55, minutes=50, source="estimated")),
                    ("psikoloji", "Psikoloji", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.5, minutes=40, source="estimated")),
                    ("sosyoloji", "Sosyoloji", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.5, minutes=40, source="estimated")),
                    ("mantik", "Mantık", _meta(importance=0.85, avg_q=3, qmin=2, qmax=5, difficulty=0.6, minutes=45, source="estimated")),
                ],
            ),
        ),
        _subject(
            "ayt_din",
            "Din Kültürü",
            70,
            _topics(
                "ayt_din",
                [
                    ("inanc", "İnanç", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
                    ("ibadet", "İbadet", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
                    ("ahlak", "Ahlak ve Değerler", _meta(importance=0.65, avg_q=1, qmin=0, qmax=2, difficulty=0.4, minutes=20, source="estimated")),
                ],
            ),
        ),
    ]

    ydt_langs = [
        ("ydt_ingilizce", "İngilizce", "en", "ayt_yabanci_dil"),
        ("ydt_almanca", "Almanca", "de", None),
        ("ydt_fransizca", "Fransızca", "fr", None),
        ("ydt_arapca", "Arapça", "ar", None),
        ("ydt_rusca", "Rusça", "ru", None),
    ]

    exams.append(
        {
            "code": "yks",
            "name": "YKS",
            "display_order": 10,
            "source": "official",
            "packs": [
                {
                    "code": "tyt",
                    "name": "TYT",
                    "display_order": 10,
                    "branch_key": None,
                    "subjects": tyt_subjects,
                },
                {
                    "code": "ayt",
                    "name": "AYT",
                    "display_order": 20,
                    "branch_key": None,
                    "subjects": [],
                    "children": [
                        {
                            "code": "ayt_sayisal",
                            "name": "Sayısal",
                            "display_order": 10,
                            "branch_key": "sayisal",
                            "subjects": ayt_sayisal,
                        },
                        {
                            "code": "ayt_ea",
                            "name": "Eşit Ağırlık",
                            "display_order": 20,
                            "branch_key": "ea",
                            "subjects": ayt_ea,
                        },
                        {
                            "code": "ayt_sozel",
                            "name": "Sözel",
                            "display_order": 30,
                            "branch_key": "sozel",
                            "subjects": ayt_sozel,
                        },
                    ],
                },
                {
                    "code": "ydt",
                    "name": "YDT",
                    "display_order": 30,
                    "branch_key": "dil",
                    "subjects": [],
                    "children": [
                        {
                            "code": code,
                            "name": name,
                            "display_order": 10 + i * 10,
                            "branch_key": lang,
                            "subjects": [
                                _subject(
                                    code,
                                    name,
                                    10,
                                    _yd_language_topics(code),
                                    legacy=legacy,
                                )
                            ],
                        }
                        for i, (code, name, lang, legacy) in enumerate(ydt_langs)
                    ],
                },
            ],
        }
    )

    # ── KPSS ──────────────────────────────────────────────────
    kpss_subjects = [
        _subject(
            "kpss_turkce",
            "Türkçe",
            10,
            _topics(
                "kpss_turkce",
                [
                    ("sozcukte_anlam", "Sözcükte Anlam", _meta(importance=0.85, avg_q=4, qmin=2, qmax=6, difficulty=0.4, minutes=40, source="estimated")),
                    ("cumlede_anlam", "Cümlede Anlam", _meta(importance=0.9, avg_q=5, qmin=3, qmax=7, difficulty=0.45, minutes=45, source="estimated")),
                    ("paragraf", "Paragraf", _meta(importance=1.0, avg_q=8, qmin=5, qmax=12, difficulty=0.55, minutes=70, source="estimated")),
                    ("yazim", "Yazım", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
                    ("noktalama", "Noktalama", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
                    ("anlatim_bozukluklari", "Anlatım Bozuklukları", _meta(importance=0.75, avg_q=3, qmin=1, qmax=4, difficulty=0.5, minutes=35, source="estimated")),
                    ("dil_bilgisi", "Dil Bilgisi", _meta(importance=0.8, avg_q=4, qmin=2, qmax=6, difficulty=0.55, minutes=45, source="estimated")),
                ],
            ),
        ),
        _subject(
            "kpss_matematik",
            "Matematik",
            20,
            _topics(
                "kpss_matematik",
                [
                    ("temel_matematik", "Temel Matematik", _meta(importance=0.9, avg_q=8, qmin=5, qmax=12, difficulty=0.45, minutes=70, source="estimated")),
                    ("problemler", "Problemler", _meta(importance=1.0, avg_q=8, qmin=5, qmax=12, difficulty=0.6, minutes=80, source="estimated")),
                    ("geometri", "Geometri", _meta(importance=0.8, avg_q=5, qmin=3, qmax=8, difficulty=0.55, minutes=50, source="estimated")),
                    ("yorum", "Sayısal Mantık", _meta(importance=0.85, avg_q=6, qmin=3, qmax=9, difficulty=0.6, minutes=55, source="estimated")),
                ],
            ),
        ),
        _subject(
            "kpss_tarih",
            "Tarih",
            30,
            _topics(
                "kpss_tarih",
                [
                    ("osmanli", "Osmanlı Tarihi", _meta(importance=0.9, avg_q=6, qmin=4, qmax=9, difficulty=0.5, minutes=60, source="estimated")),
                    ("inkilap", "İnkılap Tarihi", _meta(importance=0.95, avg_q=7, qmin=4, qmax=10, difficulty=0.5, minutes=65, source="estimated")),
                    ("cumhuriyet", "Cumhuriyet Dönemi", _meta(importance=0.85, avg_q=5, qmin=3, qmax=8, difficulty=0.5, minutes=50, source="estimated")),
                    ("kultur", "Kültür ve Medeniyet", _meta(importance=0.7, avg_q=3, qmin=1, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
                ],
            ),
        ),
        _subject(
            "kpss_cografya",
            "Coğrafya",
            40,
            _topics(
                "kpss_cografya",
                [
                    ("turkiye", "Türkiye Coğrafyası", _meta(importance=0.95, avg_q=6, qmin=4, qmax=9, difficulty=0.5, minutes=55, source="estimated")),
                    ("iklim", "İklim", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
                    ("nufus", "Nüfus ve Yerleşme", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
                    ("ekonomi", "Ekonomik Coğrafya", _meta(importance=0.75, avg_q=3, qmin=1, qmax=5, difficulty=0.5, minutes=35, source="estimated")),
                ],
            ),
        ),
        _subject(
            "kpss_vatandaslik",
            "Vatandaşlık",
            50,
            _topics(
                "kpss_vatandaslik",
                [
                    ("anayasa", "Anayasa", _meta(importance=1.0, avg_q=8, qmin=5, qmax=12, difficulty=0.55, minutes=70, source="estimated")),
                    ("temel_haklar", "Temel Haklar", _meta(importance=0.85, avg_q=4, qmin=2, qmax=6, difficulty=0.5, minutes=40, source="estimated")),
                    ("devlet_yapisi", "Devlet Yapısı", _meta(importance=0.9, avg_q=5, qmin=3, qmax=8, difficulty=0.55, minutes=50, source="estimated")),
                    ("idare", "İdare Hukuku Temelleri", _meta(importance=0.8, avg_q=4, qmin=2, qmax=6, difficulty=0.6, minutes=45, source="estimated")),
                ],
            ),
        ),
        _subject(
            "kpss_guncel",
            "Güncel Bilgiler",
            60,
            _topics(
                "kpss_guncel",
                [
                    ("guncel_olaylar", "Güncel Olaylar", _meta(importance=0.9, avg_q=5, qmin=3, qmax=8, difficulty=0.4, minutes=40, source="estimated")),
                    ("kultur_sanat", "Kültür Sanat", _meta(importance=0.7, avg_q=2, qmin=1, qmax=4, difficulty=0.4, minutes=25, source="estimated")),
                    ("bilim_teknoloji", "Bilim Teknoloji", _meta(importance=0.7, avg_q=2, qmin=1, qmax=4, difficulty=0.4, minutes=25, source="estimated")),
                ],
            ),
        ),
    ]

    exams.append(
        {
            "code": "kpss",
            "name": "KPSS",
            "display_order": 20,
            "source": "official",
            "packs": [
                {
                    "code": "kpss_lisans",
                    "name": "KPSS Lisans",
                    "display_order": 10,
                    "branch_key": "lisans",
                    "subjects": kpss_subjects,
                },
                {
                    "code": "kpss_onlisans",
                    "name": "KPSS Ön lisans",
                    "display_order": 20,
                    "branch_key": "onlisans",
                    "subjects": kpss_subjects,
                },
                {
                    "code": "kpss_ortaogretim",
                    "name": "KPSS Ortaöğretim",
                    "display_order": 30,
                    "branch_key": "ortaogretim",
                    "subjects": kpss_subjects,
                },
            ],
        }
    )

    # ── LGS ───────────────────────────────────────────────────
    exams.append(
        {
            "code": "lgs",
            "name": "LGS",
            "display_order": 30,
            "source": "official",
            "packs": [
                {
                    "code": "lgs_genel",
                    "name": "LGS",
                    "display_order": 10,
                    "branch_key": None,
                    "subjects": [
                        _subject(
                            "lgs_turkce",
                            "Türkçe",
                            10,
                            _topics(
                                "lgs_turkce",
                                [
                                    ("sozcuk", "Sözcükte Anlam", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.35, minutes=30, source="estimated")),
                                    ("cumle", "Cümlede Anlam", _meta(importance=0.85, avg_q=3, qmin=2, qmax=5, difficulty=0.4, minutes=30, source="estimated")),
                                    ("paragraf", "Paragraf", _meta(importance=1.0, avg_q=6, qmin=4, qmax=9, difficulty=0.5, minutes=50, source="estimated")),
                                    ("dil_bilgisi", "Dil Bilgisi", _meta(importance=0.75, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
                                ],
                                legacy_prefix="lgs_turkce",
                            ),
                            legacy="lgs_turkce",
                        ),
                        _subject(
                            "lgs_matematik",
                            "Matematik",
                            20,
                            _topics(
                                "lgs_matematik",
                                [
                                    ("sayilar", "Sayılar", _meta(importance=0.85, avg_q=3, qmin=2, qmax=5, difficulty=0.4, minutes=35, source="estimated")),
                                    ("cebir", "Cebir", _meta(importance=0.9, avg_q=4, qmin=2, qmax=6, difficulty=0.55, minutes=45, source="estimated")),
                                    ("geometri", "Geometri", _meta(importance=0.9, avg_q=4, qmin=2, qmax=6, difficulty=0.55, minutes=45, source="estimated")),
                                    ("veri", "Veri / Olasılık", _meta(importance=0.7, avg_q=2, qmin=1, qmax=3, difficulty=0.45, minutes=30, source="estimated")),
                                ],
                                legacy_prefix="lgs_matematik",
                            ),
                            legacy="lgs_matematik",
                        ),
                        _subject(
                            "lgs_fen",
                            "Fen",
                            30,
                            _topics(
                                "lgs_fen",
                                [
                                    ("fizik", "Fizik", _meta(importance=0.85, avg_q=4, qmin=2, qmax=6, difficulty=0.5, minutes=40, source="estimated")),
                                    ("kimya", "Kimya", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.5, minutes=35, source="estimated")),
                                    ("biyoloji", "Biyoloji", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
                                ],
                                legacy_prefix="lgs_fen",
                            ),
                            legacy="lgs_fen",
                        ),
                        _subject(
                            "lgs_inkilap",
                            "İnkılap Tarihi",
                            40,
                            _topics(
                                "lgs_inkilap",
                                [
                                    ("milli_mucadele", "Milli Mücadele", _meta(importance=0.95, avg_q=4, qmin=2, qmax=6, difficulty=0.45, minutes=40, source="estimated")),
                                    ("inkilaplar", "Atatürk İlke ve İnkılapları", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=35, source="estimated")),
                                ],
                                legacy_prefix="lgs_inkilap",
                            ),
                            legacy="lgs_inkilap",
                        ),
                        _subject(
                            "lgs_din",
                            "Din",
                            50,
                            _topics(
                                "lgs_din",
                                [
                                    ("inanc", "İnanç", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.35, minutes=20, source="estimated")),
                                    ("ibadet", "İbadet", _meta(importance=0.75, avg_q=2, qmin=1, qmax=3, difficulty=0.35, minutes=20, source="estimated")),
                                ],
                                legacy_prefix="lgs_din",
                            ),
                            legacy="lgs_din",
                        ),
                        _subject(
                            "lgs_ingilizce",
                            "İngilizce",
                            60,
                            _topics(
                                "lgs_ingilizce",
                                [
                                    ("vocabulary", "Vocabulary", _meta(importance=0.8, avg_q=3, qmin=2, qmax=5, difficulty=0.4, minutes=25, source="estimated")),
                                    ("grammar", "Grammar", _meta(importance=0.85, avg_q=3, qmin=2, qmax=5, difficulty=0.45, minutes=30, source="estimated")),
                                    ("reading", "Reading", _meta(importance=0.9, avg_q=3, qmin=2, qmax=5, difficulty=0.5, minutes=30, source="estimated")),
                                ],
                                legacy_prefix="lgs_ingilizce",
                            ),
                            legacy="lgs_ingilizce",
                        ),
                    ],
                }
            ],
        }
    )

    # ── DGS / ALES ────────────────────────────────────────────
    for code, name, order in (("dgs", "DGS", 40), ("ales", "ALES", 50)):
        exams.append(
            {
                "code": code,
                "name": name,
                "display_order": order,
                "source": "official",
                "packs": [
                    {
                        "code": f"{code}_sayisal",
                        "name": "Sayısal",
                        "display_order": 10,
                        "branch_key": "sayisal",
                        "subjects": [
                            _subject(
                                f"{code}_sayisal",
                                "Sayısal",
                                10,
                                _topics(
                                    f"{code}_sayisal",
                                    [
                                        ("temel_matematik", "Temel Matematik", _meta(importance=0.9, avg_q=10, qmin=6, qmax=15, difficulty=0.5, minutes=70, source="estimated")),
                                        ("problemler", "Problemler", _meta(importance=1.0, avg_q=12, qmin=8, qmax=18, difficulty=0.6, minutes=80, source="estimated")),
                                        ("geometri", "Geometri", _meta(importance=0.8, avg_q=6, qmin=3, qmax=10, difficulty=0.55, minutes=50, source="estimated")),
                                        ("yorum", "Sayısal Mantık", _meta(importance=0.85, avg_q=8, qmin=4, qmax=12, difficulty=0.6, minutes=55, source="estimated")),
                                    ],
                                ),
                            )
                        ],
                    },
                    {
                        "code": f"{code}_sozel",
                        "name": "Sözel",
                        "display_order": 20,
                        "branch_key": "sozel",
                        "subjects": [
                            _subject(
                                f"{code}_sozel",
                                "Sözel",
                                10,
                                _topics(
                                    f"{code}_sozel",
                                    [
                                        ("sozcuk", "Sözcükte Anlam", _meta(importance=0.85, avg_q=8, qmin=5, qmax=12, difficulty=0.4, minutes=45, source="estimated")),
                                        ("cumle", "Cümlede Anlam", _meta(importance=0.9, avg_q=8, qmin=5, qmax=12, difficulty=0.45, minutes=45, source="estimated")),
                                        ("paragraf", "Paragraf", _meta(importance=1.0, avg_q=12, qmin=8, qmax=18, difficulty=0.55, minutes=70, source="estimated")),
                                        ("anlatim", "Anlatım Bozuklukları", _meta(importance=0.7, avg_q=4, qmin=2, qmax=6, difficulty=0.5, minutes=30, source="estimated")),
                                    ],
                                ),
                            )
                        ],
                    },
                ],
            }
        )

    # ── YDS / YÖKDİL ──────────────────────────────────────────
    for code, name, order in (("yds", "YDS", 60), ("yokdil", "YÖKDİL", 70)):
        exams.append(
            {
                "code": code,
                "name": name,
                "display_order": order,
                "source": "official",
                "packs": [
                    {
                        "code": f"{code}_ingilizce",
                        "name": "İngilizce",
                        "display_order": 10,
                        "branch_key": "en",
                        "subjects": [
                            _subject(
                                f"{code}_ingilizce",
                                "İngilizce",
                                10,
                                _yd_language_topics(f"{code}_ingilizce"),
                                legacy="yds_reading" if code == "yds" else None,
                            )
                        ],
                    }
                ],
            }
        )

    # ── AGS (MEB Akademi Giriş) ───────────────────────────────
    exams.append(
        {
            "code": "ags",
            "name": "AGS",
            "display_order": 80,
            "source": "official",
            "packs": [
                {
                    "code": "ags_genel",
                    "name": "AGS Genel",
                    "display_order": 10,
                    "branch_key": None,
                    "subjects": [
                        _subject(
                            "ags_egitim_bilimleri",
                            "Eğitim Bilimleri",
                            10,
                            _topics(
                                "ags_egitim_bilimleri",
                                [
                                    ("gelisim", "Gelişim Psikolojisi", _meta(importance=0.9, avg_q=8, qmin=5, qmax=12, difficulty=0.5, minutes=60, source="estimated")),
                                    ("ogrenme", "Öğrenme Psikolojisi", _meta(importance=0.95, avg_q=10, qmin=6, qmax=14, difficulty=0.55, minutes=70, source="estimated")),
                                    ("program", "Öğretim İlke ve Yöntemleri", _meta(importance=0.9, avg_q=8, qmin=5, qmax=12, difficulty=0.55, minutes=60, source="estimated")),
                                    ("olcme", "Ölçme ve Değerlendirme", _meta(importance=0.85, avg_q=6, qmin=4, qmax=10, difficulty=0.6, minutes=50, source="estimated")),
                                    ("rehberlik", "Rehberlik", _meta(importance=0.8, avg_q=5, qmin=3, qmax=8, difficulty=0.45, minutes=40, source="estimated")),
                                    ("sinif", "Sınıf Yönetimi", _meta(importance=0.75, avg_q=4, qmin=2, qmax=6, difficulty=0.45, minutes=35, source="estimated")),
                                ],
                            ),
                        ),
                        _subject(
                            "ags_genel_kultur",
                            "Genel Kültür",
                            20,
                            _topics(
                                "ags_genel_kultur",
                                [
                                    ("tarih", "Tarih", _meta(importance=0.8, avg_q=5, qmin=3, qmax=8, difficulty=0.45, minutes=40, source="estimated")),
                                    ("cografya", "Coğrafya", _meta(importance=0.75, avg_q=4, qmin=2, qmax=6, difficulty=0.45, minutes=35, source="estimated")),
                                    ("vatandaslik", "Vatandaşlık", _meta(importance=0.8, avg_q=5, qmin=3, qmax=8, difficulty=0.5, minutes=40, source="estimated")),
                                    ("guncel", "Güncel", _meta(importance=0.7, avg_q=3, qmin=1, qmax=5, difficulty=0.4, minutes=25, source="estimated")),
                                ],
                            ),
                        ),
                    ],
                }
            ],
        }
    )

    return exams
