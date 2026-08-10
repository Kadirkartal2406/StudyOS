"""Exam Intelligence seed — resmi sınav ağacı + konu metadata.

source=official: ÖSYM/MEB/YÖK dağılımına / çok yıllı analiz istatistiğine dayalı.
source=estimated: sınıflandırma artığı yüksek veya kanıt yok — ağırlık tahmini.
Subject booklet quotas: app.services.exam_catalog.distributions.SUBJECT_QUOTAS
(never derive totals by summing topic avg_q).
"""

from __future__ import annotations

from typing import Any

from app.services.exam_catalog.distributions import topic_table_for


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


def _topics_from_table(
    subject_code: str,
    rows: list[tuple[str, str, dict[str, Any]]],
    *,
    legacy_prefix: str | None = None,
) -> list[dict[str, Any]]:
    return _topics(subject_code, rows, legacy_prefix=legacy_prefix)


def _subjects_from_topic_table(
    table: dict[str, list[tuple[str, str, dict[str, Any]]]],
    order: list[tuple[str, str, int]],
) -> list[dict[str, Any]]:
    """order: (subject_code, display_name, display_order)."""
    out: list[dict[str, Any]] = []
    for code, name, disp in order:
        rows = table.get(code) or []
        out.append(
            _subject(
                code,
                name,
                disp,
                _topics_from_table(code, rows),
                legacy=code,
            )
        )
    return out


# ── Shared topic lists ────────────────────────────────────────

def _tyt_turkce(sc: str) -> list[dict[str, Any]]:
    # Evidence: aggregates yks/tyt — paragraf ~23.7, uncertain ~14.3 of 40
    return _topics(
        sc,
        [
            ("paragraf", "Paragraf", _meta(importance=1.0, avg_q=23.67, qmin=23, qmax=24, difficulty=0.55, minutes=100, source="official", tags=["paragraf"])),
            ("uncertain", "Sınıflanamayan / Diğer", _meta(importance=0.55, avg_q=14.33, qmin=13, qmax=16, difficulty=0.5, minutes=60, source="official")),
            ("sozcukte_anlam", "Sözcükte Anlam", _meta(importance=0.7, avg_q=0.5, qmin=0, qmax=2, difficulty=0.35, minutes=20, source="estimated", tags=["anlam"])),
            ("cumlede_anlam", "Cümlede Anlam", _meta(importance=0.7, avg_q=0.5, qmin=0, qmax=2, difficulty=0.45, minutes=20, source="estimated")),
            ("anlatim_bozukluklari", "Anlatım Bozuklukları", _meta(importance=0.55, avg_q=0.3, qmin=0, qmax=1, difficulty=0.5, minutes=15, source="estimated")),
            ("yazim", "Yazım Kuralları", _meta(importance=0.5, avg_q=0.2, qmin=0, qmax=1, difficulty=0.4, minutes=15, source="estimated")),
            ("noktalama", "Noktalama", _meta(importance=0.5, avg_q=0.2, qmin=0, qmax=1, difficulty=0.4, minutes=15, source="estimated")),
            ("dil_bilgisi", "Dil Bilgisi", _meta(importance=0.6, avg_q=0.3, qmin=0, qmax=1, difficulty=0.55, minutes=20, source="estimated")),
        ],
        legacy_prefix="tyt_turkce",
    )


def _tyt_matematik(sc: str) -> list[dict[str, Any]]:
    # Temel Matematik test = 40; product Mat 30 + Geo 10.
    # Evidence within math portion: uncertain ~18.3, geometri ~17.3 of full 40 —
    # Mat slice (~30) keeps non-geometry residual; Geo subject owns geometry.
    return _topics(
        sc,
        [
            ("uncertain", "Sınıflanamayan / Diğer", _meta(importance=0.7, avg_q=14.0, qmin=12, qmax=16, difficulty=0.55, minutes=70, source="official")),
            ("problemler", "Problemler", _meta(importance=1.0, avg_q=5.0, qmin=3, qmax=8, difficulty=0.65, minutes=60, source="estimated", tags=["problem"])),
            ("temel_kavramlar", "Temel Kavramlar", _meta(importance=0.8, avg_q=2.0, qmin=1, qmax=4, difficulty=0.35, minutes=30, source="estimated")),
            ("uslu_sayilar", "Üslü Sayılar", _meta(importance=0.7, avg_q=1.5, qmin=0, qmax=3, difficulty=0.45, minutes=25, source="estimated")),
            ("koklu_sayilar", "Köklü Sayılar", _meta(importance=0.7, avg_q=1.5, qmin=0, qmax=3, difficulty=0.5, minutes=25, source="estimated")),
            ("oran_oranti", "Oran Orantı", _meta(importance=0.65, avg_q=1.0, qmin=0, qmax=2, difficulty=0.4, minutes=20, source="estimated")),
            ("fonksiyonlar", "Fonksiyonlar", _meta(importance=0.75, avg_q=1.5, qmin=0, qmax=3, difficulty=0.6, minutes=30, source="estimated")),
            ("olasilik", "Olasılık", _meta(importance=0.65, avg_q=1.0, qmin=0, qmax=2, difficulty=0.55, minutes=25, source="estimated")),
            ("gorsel_veri", "Grafik / Tablo", _meta(importance=0.75, avg_q=2.5, qmin=1, qmax=4, difficulty=0.5, minutes=30, source="official")),
        ],
        legacy_prefix="tyt_matematik",
    )


def _tyt_geometri(sc: str) -> list[dict[str, Any]]:
    # Official Temel Matematik geometry share ~17.3/40; product Geo subject = 10Q.
    return _topics(
        sc,
        [
            ("ucgenler", "Üçgenler", _meta(importance=0.95, avg_q=3.5, qmin=2, qmax=5, difficulty=0.55, minutes=40, source="estimated")),
            ("temel_geometri", "Temel Geometri", _meta(importance=0.8, avg_q=2.0, qmin=1, qmax=3, difficulty=0.4, minutes=25, source="estimated")),
            ("cember", "Çember", _meta(importance=0.8, avg_q=1.5, qmin=1, qmax=3, difficulty=0.6, minutes=25, source="estimated")),
            ("cokgenler", "Çokgenler", _meta(importance=0.7, avg_q=1.0, qmin=0, qmax=2, difficulty=0.5, minutes=20, source="estimated")),
            ("analitik", "Analitik Geometri", _meta(importance=0.75, avg_q=1.0, qmin=0, qmax=2, difficulty=0.6, minutes=25, source="estimated")),
            ("kati_cisimler", "Katı Cisimler", _meta(importance=0.65, avg_q=1.0, qmin=0, qmax=2, difficulty=0.55, minutes=20, source="estimated")),
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
    """YDT / YDS / YÖKDİL — evidence table when available."""
    key = {
        "ydt_ingilizce": "ydt_ingilizce",
        "yds_ingilizce": "yds_ingilizce",
        "yokdil_ingilizce": "yokdil_ingilizce",
    }.get(sc, "yds_ingilizce")
    table = topic_table_for(key)
    rows = table.get(sc) or table.get("ydt_ingilizce") or table.get("yds_ingilizce") or []
    return _topics_from_table(sc, rows)


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
                    ("uncertain", "Sınıflanamayan / Diğer", _meta(importance=0.65, avg_q=15.0, qmin=12, qmax=18, difficulty=0.65, minutes=80, source="official")),
                    ("fonksiyonlar", "Fonksiyonlar", _meta(importance=0.9, avg_q=2.5, qmin=1, qmax=4, difficulty=0.6, minutes=45, source="estimated")),
                    ("trigonometri", "Trigonometri", _meta(importance=0.85, avg_q=2.0, qmin=1, qmax=4, difficulty=0.65, minutes=40, source="estimated")),
                    ("limit", "Limit", _meta(importance=0.9, avg_q=2.0, qmin=1, qmax=3, difficulty=0.7, minutes=40, source="estimated")),
                    ("turev", "Türev", _meta(importance=1.0, avg_q=3.0, qmin=2, qmax=5, difficulty=0.75, minutes=55, source="estimated")),
                    ("integral", "İntegral", _meta(importance=1.0, avg_q=3.0, qmin=2, qmax=5, difficulty=0.8, minutes=55, source="estimated")),
                    ("logaritma", "Logaritma", _meta(importance=0.75, avg_q=1.0, qmin=0, qmax=2, difficulty=0.6, minutes=25, source="estimated")),
                    ("diziler", "Diziler", _meta(importance=0.8, avg_q=1.0, qmin=0, qmax=2, difficulty=0.65, minutes=25, source="estimated")),
                    ("kompleks", "Kompleks Sayılar", _meta(importance=0.7, avg_q=0.5, qmin=0, qmax=2, difficulty=0.7, minutes=20, source="estimated")),
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
                    ("ucgen", "Üçgen", _meta(importance=0.9, avg_q=3.5, qmin=2, qmax=5, difficulty=0.6, minutes=45, source="estimated")),
                    ("cember", "Çember", _meta(importance=0.85, avg_q=2.5, qmin=1, qmax=4, difficulty=0.65, minutes=40, source="estimated")),
                    ("analitik", "Analitik Geometri", _meta(importance=0.9, avg_q=2.5, qmin=1, qmax=4, difficulty=0.7, minutes=45, source="estimated")),
                    ("katilar", "Katı Cisimler", _meta(importance=0.7, avg_q=1.5, qmin=0, qmax=3, difficulty=0.6, minutes=30, source="estimated")),
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
        # Keep subject_code === pool/blueprint code (do not alias to AYT dil).
        ("ydt_ingilizce", "İngilizce", "en", "ydt_ingilizce"),
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

    # ── KPSS (variant-specific topic evidence) ───────────────
    kpss_order = [
        ("kpss_turkce", "Türkçe", 10),
        ("kpss_matematik", "Matematik", 20),
        ("kpss_tarih", "Tarih", 30),
        ("kpss_cografya", "Coğrafya", 40),
        ("kpss_vatandaslik", "Vatandaşlık", 50),
        ("kpss_guncel", "Güncel Bilgiler", 60),
    ]
    exams.append(
        {
            "code": "kpss",
            "name": "KPSS",
            "display_order": 20,
            "source": "official",
            "packs": [
                {
                    "code": f"kpss_{variant}",
                    "name": name,
                    "display_order": order,
                    "branch_key": variant,
                    "subjects": _subjects_from_topic_table(
                        topic_table_for(f"kpss_{variant}"), kpss_order
                    ),
                }
                for variant, name, order in (
                    ("lisans", "KPSS Lisans", 10),
                    ("onlisans", "KPSS Ön lisans", 20),
                    ("ortaogretim", "KPSS Ortaöğretim", 30),
                )
            ],
        }
    )

    # ── LGS (Sayısal / Sözel packs) ────────────────────────────
    exams.append(
        {
            "code": "lgs",
            "name": "LGS",
            "display_order": 30,
            "source": "official",
            "packs": [
                {
                    "code": "lgs_sayisal",
                    "name": "Sayısal",
                    "display_order": 10,
                    "branch_key": "sayisal",
                    "subjects": _subjects_from_topic_table(
                        topic_table_for("lgs_sayisal"),
                        [
                            ("lgs_matematik", "Matematik", 10),
                            ("lgs_fen", "Fen Bilimleri", 20),
                        ],
                    ),
                },
                {
                    "code": "lgs_sozel",
                    "name": "Sözel",
                    "display_order": 20,
                    "branch_key": "sozel",
                    "subjects": _subjects_from_topic_table(
                        topic_table_for("lgs_sozel"),
                        [
                            ("lgs_turkce", "Türkçe", 10),
                            ("lgs_inkilap", "İnkılap Tarihi", 20),
                            ("lgs_din", "Din Kültürü", 30),
                            ("lgs_ingilizce", "İngilizce", 40),
                        ],
                    ),
                },
            ],
        }
    )

    # ── DGS / ALES ────────────────────────────────────────────
    for code, name, order in (("dgs", "DGS", 40), ("ales", "ALES", 50)):
        say_table = topic_table_for(f"{code}_sayisal")
        soz_table = topic_table_for(f"{code}_sozel")
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
                        "subjects": _subjects_from_topic_table(
                            say_table,
                            [(f"{code}_sayisal", "Sayısal", 10)],
                        ),
                    },
                    {
                        "code": f"{code}_sozel",
                        "name": "Sözel",
                        "display_order": 20,
                        "branch_key": "sozel",
                        "subjects": _subjects_from_topic_table(
                            soz_table,
                            [(f"{code}_sozel", "Sözel", 10)],
                        ),
                    },
                ],
            }
        )

    # ── YDS ───────────────────────────────────────────────────
    exams.append(
        {
            "code": "yds",
            "name": "YDS",
            "display_order": 60,
            "source": "official",
            "packs": [
                {
                    "code": "yds_ingilizce",
                    "name": "İngilizce",
                    "display_order": 10,
                    "branch_key": "en",
                    "subjects": [
                        _subject(
                            "yds_ingilizce",
                            "İngilizce",
                            10,
                            _yd_language_topics("yds_ingilizce"),
                            legacy="yds_ingilizce",
                        )
                    ],
                }
            ],
        }
    )

    # ── YÖKDİL (Fen / Sağlık / Sosyal) ────────────────────────
    yokdil_packs = []
    for i, (field, label) in enumerate(
        (
            ("fen", "Fen Bilimleri"),
            ("saglik", "Sağlık Bilimleri"),
            ("sosyal", "Sosyal Bilimler"),
        ),
        start=1,
    ):
        table = topic_table_for(f"yokdil_{field}")
        yokdil_packs.append(
            {
                "code": f"yokdil_{field}",
                "name": label,
                "display_order": i * 10,
                "branch_key": field,
                "subjects": _subjects_from_topic_table(
                    table,
                    [("yokdil_ingilizce", "İngilizce", 10)],
                ),
            }
        )
    exams.append(
        {
            "code": "yokdil",
            "name": "YÖKDİL",
            "display_order": 70,
            "source": "official",
            "packs": yokdil_packs,
        }
    )

    # ── AGS ───────────────────────────────────────────────────
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
                    "subjects": _subjects_from_topic_table(
                        topic_table_for("ags"),
                        [
                            ("ags_turkce", "Türkçe", 10),
                            ("ags_matematik", "Matematik", 20),
                        ],
                    ),
                }
            ],
        }
    )

    return exams
