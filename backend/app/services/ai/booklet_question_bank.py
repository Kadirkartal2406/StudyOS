"""Deterministic local question bank for shared daily booklets (AI kapalıyken).

Aynı (exam, date, ord) → aynı soru. Placeholder "Seçenek A" üretmez.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class BankQuestion:
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str


def _pick(seed: str, items: list) -> object:
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)
    return items[h % len(items)]


def _seed(exam: str, day: date, ord_index: int, topic_code: str) -> str:
    return f"{exam}|{day.isoformat()}|{ord_index}|{topic_code}"


# ── Subject-family templates ──────────────────────────────────

_TURKCE: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Aşağıdaki cümlelerin hangisinde altı çizili sözcük mecaz anlamda kullanılmıştır?",
        {
            "A": "Kapının kolunu kırık bulduk.",
            "B": "Bu işin kolunu henüz kavrayamadım.",
            "C": "Masasının kolu sallanıyordu.",
            "D": "Ceketimin kolu yırtılmış.",
            "E": "Sandalyenin koluna yaslandı.",
        },
        "B",
        "“İşin kolunu kavramak” mecaz kullanımdır.",
    ),
    (
        "“Anlamı bilinmeyen bir sözcüğün cümle içindeki işlevinden yola çıkılarak anlamının "
        "çıkarılması” hangi kavrama karşılık gelir?",
        {
            "A": "Bağlamdan anlam çıkarma",
            "B": "Eş anlamlılık",
            "C": "Zıt anlamlılık",
            "D": "Ses benzerliği",
            "E": "Yazım kuralı",
        },
        "A",
        "Bağlam, sözcüğün metin içindeki anlamını belirler.",
    ),
    (
        "Aşağıdaki cümlelerin hangisinde yazım yanlışı vardır?",
        {
            "A": "Herhangi bir sorun yok.",
            "B": "Hiç bir şey söylemedi.",
            "C": "Birkaç kişi bekliyordu.",
            "D": "Bugün okulda toplantı var.",
            "E": "Yarın sınava girecek.",
        },
        "B",
        "“Hiçbir” bitişik yazılır.",
    ),
    (
        "Paragrafta asıl anlatılmak istenen aşağıdakilerden hangisidir?",
        {
            "A": "Detaylar her zaman sonuçtan önemlidir.",
            "B": "Ana fikir, yardımcı düşüncelerle desteklenir.",
            "C": "Her paragraf bağımsız olmalıdır.",
            "D": "Başlık her zaman ana fikri verir.",
            "E": "Örnekler ana fikrin yerini tutar.",
        },
        "B",
        "Paragrafın omurgası ana fikirdir; örnekler onu destekler.",
    ),
    (
        "Aşağıdakilerin hangisinde “de/da” bağlacı yanlış yazılmıştır?",
        {
            "A": "O da gelecek.",
            "B": "Evde kimse yok.",
            "C": "Senide bekledik.",
            "D": "Kitap da masada.",
            "E": "Yarın da görüşürüz.",
        },
        "C",
        "Bağlaç olan “de/da” ayrı yazılır: “Seni de”.",
    ),
]

_MATEMATIK: list[tuple[str, dict[str, str], str, str]] = [
    (
        "3x − 7 = 11 ise x kaçtır?",
        {"A": "4", "B": "5", "C": "6", "D": "7", "E": "8"},
        "C",
        "3x = 18 → x = 6",
    ),
    (
        "Bir sayının %20’si 40 ise sayı kaçtır?",
        {"A": "160", "B": "180", "C": "200", "D": "220", "E": "240"},
        "C",
        "0,20 · x = 40 → x = 200",
    ),
    (
        "2/5 + 1/10 işleminin sonucu kaçtır?",
        {"A": "1/2", "B": "3/10", "C": "2/5", "D": "3/5", "E": "7/10"},
        "A",
        "4/10 + 1/10 = 5/10 = 1/2",
    ),
    (
        "Bir dik üçgende dik kenarlar 6 ve 8 ise hipotenüs kaçtır?",
        {"A": "8", "B": "9", "C": "10", "D": "12", "E": "14"},
        "C",
        "6²+8²=36+64=100 → √100=10",
    ),
    (
        "Ortalaması 12 olan 4 sayıya 18 eklenirse yeni ortalama kaç olur?",
        {"A": "12", "B": "13", "C": "13,2", "D": "14", "E": "15"},
        "C",
        "Toplam 48; +18 → 66; 66/5 = 13,2",
    ),
    (
        "f(x) = 2x + 3 ve f(a) = 11 ise a kaçtır?",
        {"A": "2", "B": "3", "C": "4", "D": "5", "E": "6"},
        "C",
        "2a + 3 = 11 → 2a = 8 → a = 4",
    ),
]

_TARIH: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Mustafa Kemal’in Samsun’a çıkış tarihi aşağıdakilerden hangisidir?",
        {
            "A": "19 Mayıs 1919",
            "B": "23 Nisan 1920",
            "C": "30 Ağustos 1922",
            "D": "29 Ekim 1923",
            "E": "10 Kasım 1938",
        },
        "A",
        "Milli Mücadele’nin fiilî başlangıcı 19 Mayıs 1919’dur.",
    ),
    (
        "TBMM’nin açılış tarihi hangisidir?",
        {
            "A": "19 Mayıs 1919",
            "B": "23 Nisan 1920",
            "C": "9 Eylül 1922",
            "D": "24 Temmuz 1923",
            "E": "29 Ekim 1923",
        },
        "B",
        "TBMM 23 Nisan 1920’de Ankara’da açılmıştır.",
    ),
    (
        "Lozan Antlaşması hangi yılda imzalanmıştır?",
        {"A": "1919", "B": "1920", "C": "1922", "D": "1923", "E": "1924"},
        "D",
        "Lozan 24 Temmuz 1923’te imzalanmıştır.",
    ),
    (
        "Osmanlı Devleti’nin kuruluşu geleneksel olarak hangi yıla dayandırılır?",
        {"A": "1071", "B": "1299", "C": "1453", "D": "1517", "E": "1683"},
        "B",
        "Kuruluş için yaygın kabul 1299’dur.",
    ),
]

_COGRAFYA: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Türkiye’nin en yüksek dağı hangisidir?",
        {
            "A": "Erciyes",
            "B": "Süphan",
            "C": "Ağrı",
            "D": "Kaçkar",
            "E": "Uludağ",
        },
        "C",
        "Ağrı Dağı ~5137 m ile en yüksektir.",
    ),
    (
        "Aşağıdakilerden hangisi iç kuvvetlere örnektir?",
        {
            "A": "Rüzgâr aşındırması",
            "B": "Akarsu aşındırması",
            "C": "Dalga aşındırması",
            "D": "Volkanizma",
            "E": "Buzul aşındırması",
        },
        "D",
        "Volkanizma yerin içinden kaynaklanan bir iç kuvvettir.",
    ),
    (
        "Türkiye’de nüfusun en yoğun olduğu bölge hangisidir?",
        {
            "A": "Doğu Anadolu",
            "B": "İç Anadolu",
            "C": "Marmara",
            "D": "Güneydoğu Anadolu",
            "E": "Karadeniz",
        },
        "C",
        "Marmara, sanayi ve göç nedeniyle en yoğundur.",
    ),
]

_VATANDASLIK: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Türkiye Cumhuriyeti Anayasası’na göre egemenlik kime aittir?",
        {
            "A": "Cumhurbaşkanına",
            "B": "TBMM’ye",
            "C": "Millete",
            "D": "Anayasa Mahkemesine",
            "E": "Bakanlar Kuruluna",
        },
        "C",
        "Egemenlik kayıtsız şartsız milletindir.",
    ),
    (
        "Yasama organı aşağıdakilerden hangisidir?",
        {
            "A": "Cumhurbaşkanı",
            "B": "TBMM",
            "C": "Anayasa Mahkemesi",
            "D": "Yargıtay",
            "E": "Danıştay",
        },
        "B",
        "Yasama yetkisi TBMM’nindir.",
    ),
    (
        "Aşağıdakilerden hangisi temel hak ve hürriyetlerdendir?",
        {
            "A": "Vergi koyma",
            "B": "Yasa çıkarma",
            "C": "Yerleşme ve seyahat hürriyeti",
            "D": "Bütçe yapma",
            "E": "Uluslararası antlaşma imzalama",
        },
        "C",
        "Yerleşme ve seyahat kişi hürriyetlerindendir.",
    ),
]

_GUNCEL: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Bir haber metninde “5N 1K” kuralı neyi ifade eder?",
        {
            "A": "Sadece başlık yazımını",
            "B": "Kim, ne, nerede, ne zaman, neden, nasıl",
            "C": "Sadece görsel seçimini",
            "D": "Reklam metnini",
            "E": "Kaynakça düzenini",
        },
        "B",
        "Haberin temel unsurları 5N1K ile özetlenir.",
    ),
    (
        "Aşağıdakilerden hangisi bir ülkenin yumuşak gücüne örnektir?",
        {
            "A": "Askerî müdahale",
            "B": "Ekonomik yaptırım",
            "C": "Kültürel diplomasi",
            "D": "Ambargo",
            "E": "Silahlanma yarışı",
        },
        "C",
        "Yumuşak güç kültür, diplomasi ve cazibe unsurlarını kapsar.",
    ),
]

_FEN: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Newton’un ikinci yasası hangi bağıntı ile ifade edilir?",
        {
            "A": "F = m · a",
            "B": "E = m · c²",
            "C": "V = I · R",
            "D": "p = m · v",
            "E": "W = F · x",
        },
        "A",
        "Net kuvvet, kütle ile ivmenin çarpımına eşittir.",
    ),
    (
        "Suyun kimyasal formülü nedir?",
        {"A": "CO₂", "B": "H₂O", "C": "O₂", "D": "NaCl", "E": "CH₄"},
        "B",
        "Su iki hidrojen ve bir oksijenden oluşur.",
    ),
    (
        "Fotosentezde bitkiler atmosferden hangi gazı alır?",
        {
            "A": "Azot",
            "B": "Oksijen",
            "C": "Karbondioksit",
            "D": "Hidrojen",
            "E": "Helyum",
        },
        "C",
        "Fotosentezde CO₂ kullanılır, O₂ açığa çıkar.",
    ),
]

_FELSEFE: list[tuple[str, dict[str, str], str, str]] = [
    (
        "“Bilgi nedir?” sorusu felsefenin hangi alanıyla doğrudan ilgilidir?",
        {
            "A": "Ontoloji",
            "B": "Epistemoloji",
            "C": "Estetik",
            "D": "Etik",
            "E": "Siyaset felsefesi",
        },
        "B",
        "Epistemoloji bilgi kuramıdır.",
    ),
    (
        "Ahlak felsefesinin temel sorularından biri hangisidir?",
        {
            "A": "Güzellik nedir?",
            "B": "Varlık nedir?",
            "C": "İyi eylem nedir?",
            "D": "Devlet nedir?",
            "E": "Uzay nedir?",
        },
        "C",
        "Etik, iyi-kötü / doğru-yanlış eylemleri inceler.",
    ),
]

_INGILIZCE: list[tuple[str, dict[str, str], str, str]] = [
    (
        "Which option correctly completes the sentence?\n"
        "She _____ to school every day.",
        {
            "A": "go",
            "B": "goes",
            "C": "going",
            "D": "gone",
            "E": "went",
        },
        "B",
        "3rd person singular present simple takes -s/-es.",
    ),
    (
        "Choose the synonym of “important”.",
        {
            "A": "trivial",
            "B": "significant",
            "C": "optional",
            "D": "rare",
            "E": "slow",
        },
        "B",
        "Significant ≈ important.",
    ),
]

_DEFAULT: list[tuple[str, dict[str, str], str, str]] = [
    (
        "{topic} konusunda aşağıdakilerden hangisi doğrudur?",
        {
            "A": "{topic} temel kavramları tutarlı biçimde uygulanır.",
            "B": "{topic} yalnızca ezbere dayanır.",
            "C": "{topic} hiçbir kurala bağlı değildir.",
            "D": "{topic} sadece tek bir örnekle sınırlıdır.",
            "E": "{topic} ölçülemez ve değerlendirilemez.",
        },
        "A",
        "{topic} konusunda kavramsal tutarlılık esastır.",
    ),
    (
        "{topic} ile ilgili bir soruda en güvenilir yaklaşım hangisidir?",
        {
            "A": "Tanımı hatırlayıp örneğe uygulamak",
            "B": "Şıkları rastgele elemek",
            "C": "Konuyu tamamen atlamak",
            "D": "Sadece ezber cümleleri yazmak",
            "E": "Zamanı boşa harcamak",
        },
        "A",
        "Tanım → uygulama, doğru çözüm yoludur.",
    ),
    (
        "{subject} / {topic}: Aşağıdaki yargılardan hangisi daha isabetlidir?",
        {
            "A": "Konu, örneklerle pekiştirildiğinde kalıcı öğrenilir.",
            "B": "Tekrar etmek öğrenmeyi engeller.",
            "C": "Hata yapmak öğrenmeyi imkânsız kılar.",
            "D": "Soru çözmek gereksizdir.",
            "E": "Plan yapmak zaman kaybıdır.",
        },
        "A",
        "Aktif tekrar ve örnekleme kalıcı öğrenmeyi destekler.",
    ),
]


def _family(subject_code: str) -> list[tuple[str, dict[str, str], str, str]]:
    s = (subject_code or "").lower()
    if any(x in s for x in ("turkce", "edebiyat", "dil_anlatim", "sozel")):
        return _TURKCE
    if any(x in s for x in ("matematik", "geometri", "sayisal")):
        return _MATEMATIK
    if "tarih" in s or "inkilap" in s:
        return _TARIH
    if "cografya" in s:
        return _COGRAFYA
    if "vatandas" in s:
        return _VATANDASLIK
    if "guncel" in s:
        return _GUNCEL
    if any(x in s for x in ("fizik", "kimya", "biyoloji", "fen")):
        return _FEN
    if "felsefe" in s or "din" in s:
        return _FELSEFE
    if any(x in s for x in ("ingilizce", "yabanci", "yds")):
        return _INGILIZCE
    return _DEFAULT


def looks_like_placeholder(stem: str | None, choices: dict | None) -> bool:
    """Eski sentetik pack’leri tespit et (yeniden üretim için)."""
    st = stem or ""
    if "Bu konuyla ilgili doğru seçeneği işaretleyiniz" in st:
        return True
    if "Seçenek A" in str((choices or {}).get("A", "")):
        return True
    return False


def make_booklet_question(
    *,
    exam_type: str,
    challenge_date: date,
    ord_index: int,
    subject_code: str,
    subject_name: str,
    topic_code: str,
    topic_name: str,
) -> BankQuestion:
    family = _family(subject_code)
    seed = _seed(exam_type, challenge_date, ord_index, topic_code or subject_code)
    stem_t, choices_t, correct, expl_t = _pick(seed, family)  # type: ignore[misc]

    topic = topic_name or topic_code or "Konu"
    subject = subject_name or subject_code or "Ders"

    def fmt(text: str) -> str:
        return (
            text.replace("{topic}", topic)
            .replace("{subject}", subject)
            .replace("{n}", str(ord_index + 1))
        )

    choices = {k: fmt(v) for k, v in choices_t.items()}
    # KPSS vb. 5 şıklı; 4 şıklı bankada E yoksa üret
    if "E" not in choices:
        choices["E"] = f"{topic} ile ilgili diğer seçeneklerin hiçbiri"

    return BankQuestion(
        stem=fmt(stem_t),
        choices=choices,
        correct_key=correct if correct in choices else "A",
        explanation=fmt(expl_t),
    )
