"""
StudyOS — Topic catalog seed (Sprint-3.2.A)

Long-term domain model under Subject Catalog.
Identity = topic_code (`{subject_code}__{slug}`).
name = display only.
"""

from __future__ import annotations

from typing import Any


def _topics(subject_code: str, items: list[tuple[str, str, int, int | None]]) -> list[dict[str, Any]]:
    """items: (slug, name, sort_order, difficulty)."""
    out: list[dict[str, Any]] = []
    for slug, name, sort_order, difficulty in items:
        out.append(
            {
                "code": f"{subject_code}__{slug}",
                "name": name,
                "subject_code": subject_code,
                "sort_order": sort_order,
                "difficulty": difficulty,
                "is_active": True,
            }
        )
    return out


TOPIC_CATALOG_SEED: list[dict[str, Any]] = []

# ── TYT Matematik ─────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_matematik",
    [
        ("temel_kavramlar", "Temel Kavramlar", 10, 1),
        ("sayi_basamaklari", "Sayı Basamakları", 20, 1),
        ("bolme_bolunebilme", "Bölme Bölünebilme", 30, 2),
        ("obeb_okek", "OBEB OKEK", 40, 2),
        ("rasyonel_sayilar", "Rasyonel Sayılar", 50, 2),
        ("mutlak_deger", "Mutlak Değer", 60, 2),
        ("uslu_sayilar", "Üslü Sayılar", 70, 2),
        ("koklu_sayilar", "Köklü Sayılar", 80, 2),
        ("carpanlara_ayirma", "Çarpanlara Ayırma", 90, 3),
        ("oran_oranti", "Oran Orantı", 100, 2),
        ("problemler", "Problemler", 110, 3),
        ("kumeler", "Kümeler", 120, 2),
        ("fonksiyonlar", "Fonksiyonlar", 130, 3),
        ("polinomlar", "Polinomlar", 140, 3),
        ("ikinci_derece", "İkinci Dereceden Denklemler", 150, 3),
        ("permutasyon_kombinasyon", "Permütasyon Kombinasyon", 160, 3),
        ("olasilik", "Olasılık", 170, 3),
    ],
)

# ── TYT Geometri ──────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_geometri",
    [
        ("temel_geometri", "Temel Geometri", 10, 1),
        ("ucgenler", "Üçgenler", 20, 2),
        ("dik_ucgen", "Dik Üçgen", 30, 2),
        ("cokgenler", "Çokgenler", 40, 2),
        ("cember", "Çember", 50, 3),
        ("katı_cisimler", "Katı Cisimler", 60, 3),
        ("analitik", "Analitik Geometri", 70, 3),
    ],
)

# ── TYT Fizik ─────────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_fizik",
    [
        ("vektorler", "Vektörler", 10, 1),
        ("kuvvet", "Kuvvet", 20, 2),
        ("hareket", "Hareket", 30, 2),
        ("enerji", "Enerji", 40, 2),
        ("isitma", "Isı ve Sıcaklık", 50, 2),
        ("elektrostatik", "Elektrostatik", 60, 3),
        ("akim", "Elektrik Akımı", 70, 3),
        ("manyetizma", "Manyetizma", 80, 3),
        ("dalgalar", "Dalgalar", 90, 3),
        ("optik", "Optik", 100, 3),
    ],
)

# ── TYT Kimya ─────────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_kimya",
    [
        ("atom", "Atom ve Periyodik Sistem", 10, 1),
        ("kimyasal_turler", "Kimyasal Türler Arası Etkileşim", 20, 2),
        ("mol", "Mol Kavramı", 30, 2),
        ("kimyasal_tepkimeler", "Kimyasal Tepkimeler", 40, 2),
        ("asitler_bazlar", "Asitler Bazlar", 50, 3),
        ("karisimlar", "Karışımlar", 60, 2),
        ("kimya_her_yerde", "Kimya Her Yerde", 70, 2),
    ],
)

# ── TYT Biyoloji ──────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_biyoloji",
    [
        ("canlilarin_ortak", "Canlıların Ortak Özellikleri", 10, 1),
        ("hucre", "Hücre", 20, 2),
        ("canlilarin_siniflandirilmasi", "Canlıların Sınıflandırılması", 30, 2),
        ("hucresel_solunum", "Hücresel Solunum", 40, 3),
        ("fotosentez", "Fotosentez", 50, 3),
        ("kalitim", "Kalıtım", 60, 3),
        ("ekoloji", "Ekoloji", 70, 2),
    ],
)

# ── TYT Türkçe ────────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_turkce",
    [
        ("sozcukte_anlam", "Sözcükte Anlam", 10, 1),
        ("cumlede_anlam", "Cümlede Anlam", 20, 2),
        ("paragraf", "Paragraf", 30, 2),
        ("anlatim_bozukluklari", "Anlatım Bozuklukları", 40, 3),
        ("yazim", "Yazım Kuralları", 50, 2),
        ("noktalama", "Noktalama", 60, 2),
        ("ses_bilgisi", "Ses Bilgisi", 70, 2),
        ("dil_bilgisi", "Dil Bilgisi", 80, 3),
    ],
)

# ── TYT Tarih / Coğrafya / Felsefe / Din ──────────────────────
TOPIC_CATALOG_SEED += _topics(
    "tyt_tarih",
    [
        ("tarih_bilimi", "Tarih Bilimi", 10, 1),
        ("ilk_cag", "İlk Çağ", 20, 2),
        ("orta_cag", "Orta Çağ", 30, 2),
        ("osmanli", "Osmanlı", 40, 2),
        ("yakin_cag", "Yakın Çağ", 50, 3),
        ("inkilap", "İnkılap Tarihi", 60, 2),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "tyt_cografya",
    [
        ("harita", "Harita Bilgisi", 10, 1),
        ("iklim", "İklim", 20, 2),
        ("nufus", "Nüfus", 30, 2),
        ("turkiye_cografyasi", "Türkiye Coğrafyası", 40, 2),
        ("ekonomik_cografya", "Ekonomik Coğrafya", 50, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "tyt_felsefe",
    [
        ("felsefeye_giris", "Felsefeye Giriş", 10, 1),
        ("bilgi_felsefesi", "Bilgi Felsefesi", 20, 2),
        ("varlik", "Varlık Felsefesi", 30, 2),
        ("ahlak", "Ahlak Felsefesi", 40, 2),
        ("siyaset", "Siyaset Felsefesi", 50, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "tyt_din",
    [
        ("inanc", "İnanç", 10, 1),
        ("ibadet", "İbadet", 20, 1),
        ("ahlak_din", "Ahlak", 30, 2),
        ("din_ve_hayat", "Din ve Hayat", 40, 2),
    ],
)

# ── AYT Matematik / Fizik (örnek) ─────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "ayt_matematik",
    [
        ("fonksiyonlar", "Fonksiyonlar", 10, 2),
        ("trigonometri", "Trigonometri", 20, 3),
        ("limit", "Limit", 30, 3),
        ("turev", "Türev", 40, 4),
        ("integral", "İntegral", 50, 4),
        ("logaritma", "Logaritma", 60, 3),
        ("diziler", "Diziler", 70, 3),
        ("kompleks", "Kompleks Sayılar", 80, 4),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "ayt_fizik",
    [
        ("kuvvet_hareket", "Kuvvet ve Hareket", 10, 2),
        ("enerji_momentum", "Enerji ve Momentum", 20, 3),
        ("elektrik", "Elektrik", 30, 3),
        ("manyetizma", "Manyetizma", 40, 3),
        ("modern_fizik", "Modern Fizik", 50, 4),
        ("dalgalar", "Dalgalar", 60, 3),
    ],
)

# ── KPSS Türkçe (+ diğer KPSS dersleri) ───────────────────────
TOPIC_CATALOG_SEED += _topics(
    "kpss_turkce",
    [
        ("sozcukte_anlam", "Sözcükte Anlam", 10, 1),
        ("cumlede_anlam", "Cümlede Anlam", 20, 2),
        ("paragraf", "Paragraf", 30, 2),
        ("yazim", "Yazım", 40, 2),
        ("noktalama", "Noktalama", 50, 2),
        ("anlatim_bozukluklari", "Anlatım Bozuklukları", 60, 3),
        ("dil_bilgisi", "Dil Bilgisi", 70, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "kpss_matematik",
    [
        ("temel_matematik", "Temel Matematik", 10, 1),
        ("problemler", "Problemler", 20, 2),
        ("geometri", "Geometri", 30, 2),
        ("yorum", "Sayısal Mantık", 40, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "kpss_tarih",
    [
        ("osmanli", "Osmanlı Tarihi", 10, 2),
        ("inkilap", "İnkılap Tarihi", 20, 2),
        ("cumhuriyet", "Cumhuriyet Dönemi", 30, 2),
        ("kultur", "Kültür ve Medeniyet", 40, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "kpss_cografya",
    [
        ("turkiye", "Türkiye Coğrafyası", 10, 2),
        ("iklim", "İklim", 20, 2),
        ("nufus", "Nüfus ve Yerleşme", 30, 2),
        ("ekonomi", "Ekonomik Coğrafya", 40, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "kpss_vatandaslik",
    [
        ("anayasa", "Anayasa", 10, 2),
        ("temel_haklar", "Temel Haklar", 20, 2),
        ("devlet_yapisi", "Devlet Yapısı", 30, 2),
        ("idare", "İdare Hukuku Temelleri", 40, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "kpss_guncel",
    [
        ("guncel_olaylar", "Güncel Olaylar", 10, 1),
        ("kultur_sanat", "Kültür Sanat", 20, 2),
        ("bilim_teknoloji", "Bilim Teknoloji", 30, 2),
    ],
)

# ── YDS ───────────────────────────────────────────────────────
TOPIC_CATALOG_SEED += _topics(
    "yds_reading",
    [
        ("inference", "Inference", 10, 3),
        ("vocabulary_in_context", "Vocabulary in Context", 20, 2),
        ("paragraph_completion", "Paragraph Completion", 30, 3),
        ("main_idea", "Main Idea", 40, 2),
        ("detail", "Detail Questions", 50, 2),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "yds_vocabulary",
    [
        ("synonyms", "Synonyms", 10, 2),
        ("collocations", "Collocations", 20, 2),
        ("academic_words", "Academic Words", 30, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "yds_grammar",
    [
        ("tenses", "Tenses", 10, 2),
        ("conditionals", "Conditionals", 20, 3),
        ("relative_clauses", "Relative Clauses", 30, 3),
        ("passive", "Passive Voice", 40, 2),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "yds_cloze",
    [
        ("cloze_practice", "Cloze Practice", 10, 3),
    ],
)
TOPIC_CATALOG_SEED += _topics(
    "yds_translation",
    [
        ("tr_en", "TR → EN", 10, 3),
        ("en_tr", "EN → TR", 20, 3),
    ],
)
