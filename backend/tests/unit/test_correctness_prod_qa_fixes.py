"""Production QA failure fixtures + MUST/SHOULD correctness extensions."""

from __future__ import annotations

from app.services.correctness import (
    CorrectnessErrorCode,
    CorrectnessInput,
    CorrectnessVerdict,
    run_correctness_gate,
    run_integrity_gate,
)
from app.services.correctness.area_template import try_poly_abs_area
from app.services.correctness.explanation_consistency import check_explanation_consistency
from app.services.correctness.relation_parse import (
    parse_linear_relation,
    parse_option_value,
    relations_equal,
)
from app.services.correctness.solution_consistency import check_solution_consistency
from app.services.correctness.solvability import check_solvability

# ── Real Track A ACCEPT failures (prod_qa_2026-08-12) ───────────────

PROD_DGS_0 = {
    "stem": (
        r"Pozitif tam sayılardan oluşan ve ardışık terimleri arasındaki farkın "
        r"sabit olmadığı bir sayı dizisinde, her n \geq 1 için n. terim "
        r"\(a_n = n^2 - \text{en küçük asal bölen}(n+1)\) kuralıyla tanımlanmıştır. "
        r"Bu dizinin ilk dört teriminin toplamı kaçtır?"
    ),
    "choices": {"A": "22", "B": "24", "C": "26", "D": "28", "E": "30"},
    "correct_key": "B",
    "explanation": (
        r"Adım 1: n = 1 için \(a_1 = 1^2 - \text{en küçük asal bölen}(2) = 1 - 2 = -1\). "
        r"Soru metnindeki ifadenin sonucu \(a_1 = -1\) olmakla birlikte, sorunun özgün "
        r"kurgusunda terimlerin toplamı şu şekilde hesaplanır:"
        "\n"
        r"n = 1 için: \(1^2 + \text{en küçük asal bölen}(2) = 1 + 2 = 3\)"
        "\n"
        r"n = 2 için: \(2^2 + \text{en küçük asal bölen}(3) = 4 + 3 = 7\)"
        "\n"
        r"n = 3 için: \(3^2 + \text{en küçük asal bölen}(4) = 9 + 2 = 11\)"
        "\n"
        r"n = 4 için: \(4^2 + \text{en küçük asal bölen}(5) = 16 + 5 = 21\) "
        "\n"
        "(Not: Soru metnindeki eksi işareti artı olarak değerlendirildiğinde veya "
        "standart soru kalibresinde) Toplam = 3 + 7 + 11 + 21"
    ),
}

PROD_AYT_2 = {
    "stem": (
        r"Gerçel sayılar kümesinde tanımlı ve sürekli bir f fonksiyonu için "
        r"\int_{0}^{4} f(x)\,dx = 12 olduğuna göre, "
        r"\int_{0}^{2} \left(x \cdot f'(x^2)\,dx\right) integralinin değeri kaçtır?"
    ),
    "choices": {"A": "3", "B": "6", "C": "12", "D": "18", "E": "24"},
    "correct_key": "B",
    "explanation": (
        r"Adım 1: u = x^2 dönüşümü. Adım 4: \int_{0}^{4} f'(u)\,du = f(4) - f(0). "
        r"Sonuç: 6"
    ),
}

PROD_AYT_3 = {
    "stem": (
        r"Dik koordinat düzleminde f(x) = 4 - x^2 parabolü ile g(x) = |x| "
        r"fonksiyonunun grafikleri arasında kalan sınırlı bölgenin alanı kaç birimkaredir?"
    ),
    "choices": {
        "A": "16/3",
        "B": "20/3",
        "C": "22/3",
        "D": "26/3",
        "E": "32/3",
    },
    "correct_key": "D",
    "explanation": (
        r"Adım 2: x_0 = \frac{\sqrt{17} - 1}{2}. "
        r"Adım 4: alan 26/3 birimkare olarak bulunur."
    ),
}

PROD_ALES_5 = {
    "stem": (
        "Bir depolama tesisinde bulunan A ve B tipi iki farklı konteyner grubunun "
        "doluluk oranları ve kapasiteleri incelenmiştir. A grubu konteynerlerin toplam "
        "sayısı B grubu konteynerlerin toplam sayısının 3 katıdır. Her bir A "
        "konteynerinin kapasitesi x birim, B konteynerinin kapasitesi ise y birimdir. "
        "A grubunun tamamının doluluk oranı %30, B grubunun tamamının doluluk oranı "
        "ise %80'tir. Bu iki grup birleştirildiğinde tüm sistemin genel doluluk oranı "
        "%45 olduğuna göre, x ile y arasındaki bağıntı aşağıdakilerden hangisidir?"
    ),
    "choices": {
        "A": "y = 2x",
        "B": "y = 3x",
        "C": "2y = 3x",
        "D": "3y = 4x",
        "E": "y = 4x",
    },
    "correct_key": "A",
    "explanation": (
        "Adım 6: Genel doluluk oranı: \\frac{0.8ky + 0.9kx}{ky + 3kx} = 0.45 = \\frac{9}{20}\n"
        "Adım 7: 20(0.8ky + 0.9kx) = 9(ky + 3kx) \\Rightarrow 16ky + 18kx = 9ky + 27kx "
        "\\Rightarrow 7ky = 9kx... Gerekli sadeleştirmelerle tam oran olan y = 2x bağıntısını"
    ),
}


def _p1(q: dict, *, subject: str, exam: str):
    return run_correctness_gate(
        CorrectnessInput.from_dict(q, subject_code=subject, exam=exam)
    )


def _p2(q: dict, *, subject: str, exam: str):
    return run_integrity_gate(
        CorrectnessInput.from_dict(q, subject_code=subject, exam=exam)
    )


# ── Relation parser ─────────────────────────────────────────────────


def test_relation_parser_basic_forms() -> None:
    assert parse_linear_relation("y=2x") is not None
    assert parse_linear_relation("y = 2x") is not None
    assert parse_linear_relation("y=(9/7)x") is not None
    assert parse_linear_relation(r"y=\frac{9}{7}x") is not None
    assert parse_linear_relation("2y=3x") is not None
    assert parse_linear_relation("7ky=9kx") is not None


def test_relation_parser_rejects_prose() -> None:
    assert parse_linear_relation("Bilgiye hızlı erişim okumayı zayıflatır.") is None
    assert parse_option_value("Trust needs explanation").ok is False


def test_relation_equivalence_and_contradiction() -> None:
    a = parse_linear_relation("7ky=9kx")
    b = parse_linear_relation("y=(9/7)x")
    c = parse_linear_relation("y=2x")
    assert a is not None and b is not None and c is not None
    assert relations_equal(a, b) is True
    assert relations_equal(a, c) is False


def test_relation_options_not_false_equivalent() -> None:
    from app.services.correctness.option_equivalence import find_equivalent_option_pairs

    pairs = find_equivalent_option_pairs(PROD_ALES_5["choices"])
    assert pairs == []


# ── Production QA regressions ───────────────────────────────────────


def test_prod_dgs_0_operator_rewrite_solution_stem_mismatch() -> None:
    inp = CorrectnessInput.from_dict(
        PROD_DGS_0, subject_code="dgs_sayisal", exam="dgs_sayisal"
    )
    sc = check_solution_consistency(inp)
    assert sc.status == "fail"
    assert sc.error_code == CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value
    assert sc.evidence.get("operator_rewrite")
    r = _p2(PROD_DGS_0, subject="dgs_sayisal", exam="dgs_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value


def test_prod_ales_5_explanation_self_consistency_fail() -> None:
    inp = CorrectnessInput.from_dict(
        PROD_ALES_5, subject_code="ales_sayisal", exam="ales_sayisal"
    )
    ec = check_explanation_consistency(inp)
    assert ec.status == "fail"
    assert ec.error_code == CorrectnessErrorCode.ANSWER_KEY_MISMATCH.value
    assert "7ky" in (ec.message or "")
    r = _p1(PROD_ALES_5, subject="ales_sayisal", exam="ales_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.ANSWER_KEY_MISMATCH.value
    assert r.verdict == CorrectnessVerdict.FAIL


def test_prod_ayt_2_unsolvable_insufficient_information() -> None:
    inp = CorrectnessInput.from_dict(
        PROD_AYT_2, subject_code="ayt_matematik", exam="ayt_sayisal"
    )
    sv = check_solvability(inp)
    assert sv.status == "fail"
    assert sv.error_code == CorrectnessErrorCode.UNSOLVABLE.value
    assert sv.evidence.get("pattern") == "integral_f_given_asks_fprime"
    r = _p2(PROD_AYT_2, subject="ayt_matematik", exam="ayt_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.UNSOLVABLE.value


def test_prod_ayt_3_area_template_no_correct_option() -> None:
    area = try_poly_abs_area(PROD_AYT_3["stem"])
    assert area.ok is True
    r = _p1(PROD_AYT_3, subject="ayt_matematik", exam="ayt_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value
    assert r.evidence.get("solved_value") is not None


# ── False-positive guards ───────────────────────────────────────────


def test_fp_consistent_minus_spf_not_rewrite() -> None:
    q = {
        "stem": (
            r"a_n = n^2 - \text{en küçük asal bölen}(n+1) için a_1 kaçtır?"
        ),
        "choices": {"A": "-1", "B": "1", "C": "2", "D": "3", "E": "0"},
        "correct_key": "A",
        "explanation": (
            r"n=1: \(1^2 - \text{en küçük asal bölen}(2) = 1 - 2 = -1\). Sonuç: -1"
        ),
    }
    sc = check_solution_consistency(
        CorrectnessInput.from_dict(q, subject_code="dgs_sayisal", exam="dgs_sayisal")
    )
    assert sc.status == "pass"
    assert sc.evidence.get("operator_rewrite") is None


def test_fp_consistent_relation_explanation_passes() -> None:
    q = {
        "stem": "x ve y arasında hangi bağıntı vardır?",
        "choices": {
            "A": "y = 2x",
            "B": "y = 3x",
            "C": "2y = 3x",
            "D": "3y = 4x",
            "E": "y = 4x",
        },
        "correct_key": "A",
        "explanation": "Adım: 2ky = 4kx \\Rightarrow y = 2x. Sonuç: y = 2x",
    }
    ec = check_explanation_consistency(
        CorrectnessInput.from_dict(q, subject_code="ales_sayisal", exam="ales_sayisal")
    )
    assert ec.status == "pass"


def test_fp_integral_with_f_values_not_unsolvable() -> None:
    q = {
        "stem": (
            r"f(0)=1, f(4)=5 ve \int_{0}^{4} f(x)\,dx = 12 olduğuna göre "
            r"\int_{0}^{2} x f'(x^2)\,dx kaçtır?"
        ),
        "choices": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        "correct_key": "B",
        "explanation": "Sonuç: 2",
    }
    sv = check_solvability(
        CorrectnessInput.from_dict(q, subject_code="ayt_matematik", exam="ayt_sayisal")
    )
    assert sv.status != "fail" or sv.evidence.get("pattern") != "integral_f_given_asks_fprime"


def test_fp_area_non_abs_g_unsupported() -> None:
    stem = (
        r"f(x) = -x^2 + 4x parabolü ile g(x) = x doğrusu arasında kalan "
        r"sınırlı bölgenin alanı kaçtır?"
    )
    assert try_poly_abs_area(stem).ok is False


def test_fp_valid_numeric_still_passes_phase1() -> None:
    q = {
        "stem": "2 + 2 işleminin sonucu kaçtır?",
        "choices": {"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
        "correct_key": "B",
        "explanation": "Adım 1: 2 + 2 = 4.\nSonuç: 4",
    }
    r = _p1(q, subject="lgs_matematik", exam="lgs_sayisal")
    assert r.passed is True
    assert r.verdict == CorrectnessVerdict.PASS


# ── ALES #11 confessed derived∉options ──────────────────────────────

ALES_11_CONFESSED_NO_OPTION = {
    "stem": (
        "Bir kütüphanedeki raflara kitaplar dizilirken her rafa ya 12 adet roman "
        "ya da 18 adet tarih kitabı tam olarak sığmaktadır. Kitapların konulduğu "
        "toplam raf sayısı 20'den fazla ve 35'ten azdır. Rafların tamamı tamamen "
        "doldurulduğunda, kütüphanedeki roman sayısı ile tarih kitabı sayısı "
        "arasındaki fark en çok kaç olabilir?"
    ),
    "choices": {"A": "72", "B": "96", "C": "108", "D": "120", "E": "144"},
    "correct_key": "C",
    "explanation": (
        "Adım 1: Toplam raf sayısı R olsun. 20 < R < 35.\n"
        "Adım 2: Fark = 18R - 12R = 6R.\n"
        "Adım 3: En büyük R = 34 için fark 6 × 34 = 204.\n"
        "Ancak seçeneklerde 6 × 34 = 204 yoktur. "
        "Sorunun klasik tipinde C seçeneği alınır."
    ),
}


def test_ales_11_confessed_derived_missing_from_options_fails() -> None:
    ec = check_explanation_consistency(
        CorrectnessInput.from_dict(
            ALES_11_CONFESSED_NO_OPTION,
            subject_code="ales_sayisal",
            exam="ales_sayisal",
        )
    )
    assert ec.status == "fail"
    assert ec.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value
    assert "204" in (ec.message or "")

    r = _p1(ALES_11_CONFESSED_NO_OPTION, subject="ales_sayisal", exam="ales_sayisal")
    assert r.passed is False
    assert r.verdict == CorrectnessVerdict.FAIL
    assert r.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value


def test_fp_derived_204_present_in_options_passes() -> None:
    q = {
        "stem": "Fark en çok kaçtır?",
        "choices": {"A": "72", "B": "96", "C": "108", "D": "144", "E": "204"},
        "correct_key": "E",
        "explanation": "Adım: 6 × 34 = 204 elde edilir.\nSonuç: 204",
    }
    ec = check_explanation_consistency(
        CorrectnessInput.from_dict(q, subject_code="ales_sayisal", exam="ales_sayisal")
    )
    assert ec.status == "pass"
    r = _p1(q, subject="ales_sayisal", exam="ales_sayisal")
    assert r.passed is True


def test_fp_confession_but_value_actually_in_options_no_fail() -> None:
    q = {
        "stem": "Fark en çok kaçtır?",
        "choices": {"A": "72", "B": "96", "C": "108", "D": "144", "E": "204"},
        "correct_key": "C",
        "explanation": (
            "Hesap: 6 × 34 = 204. Ancak 204 seçeneklerde yok denmiştir; "
            "yine de şıklarda 204 vardır."
        ),
    }
    ec = check_explanation_consistency(
        CorrectnessInput.from_dict(q, subject_code="ales_sayisal", exam="ales_sayisal")
    )
    assert ec.status == "pass"
    assert ec.error_code is None


def test_fp_absence_language_without_numeric_no_fail() -> None:
    q = {
        "stem": "Ana düşünce aşağıdakilerden hangisidir?",
        "choices": {
            "A": "Okumak önemlidir",
            "B": "Yazmak önemlidir",
            "C": "Dinlemek önemlidir",
            "D": "Konuşmak önemlidir",
            "E": "Hiçbiri",
        },
        "correct_key": "A",
        "explanation": (
            "Paragrafın vurgusu A seçeneğidir. "
            "Diğer yorumlar seçeneklerde yok sayılmamalıdır ama net sonuç A'dır."
        ),
    }
    # "seçeneklerde yok" substring appears inside "seçeneklerde yok sayılmamalıdır"
    # — if that triggers absence, there is still no reliable numeric derived value.
    ec = check_explanation_consistency(
        CorrectnessInput.from_dict(q, subject_code="ales_sayisal", exam="ales_sayisal")
    )
    assert ec.status == "pass"


def test_fp_normal_correct_math_still_passes() -> None:
    q = {
        "stem": "2 + 2 işleminin sonucu kaçtır?",
        "choices": {"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
        "correct_key": "B",
        "explanation": "Adım 1: 2 + 2 = 4.\nSonuç: 4",
    }
    ec = check_explanation_consistency(
        CorrectnessInput.from_dict(q, subject_code="lgs_matematik", exam="lgs_sayisal")
    )
    assert ec.status == "pass"
    r = _p1(q, subject="lgs_matematik", exam="lgs_sayisal")
    assert r.passed is True
    assert r.verdict == CorrectnessVerdict.PASS
