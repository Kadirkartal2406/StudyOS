"""Phase 1 correctness gate — real QA regressions + conservative parser tests."""

from __future__ import annotations

from app.services.ai.quiz_quality_gate import validate_quiz_payload
from app.services.correctness import (
    CORRECTNESS_CHECKS,
    CORRECTNESS_VERSION,
    CorrectnessErrorCode,
    CorrectnessInput,
    CorrectnessVerdict,
    is_correctness_current,
    run_correctness_gate,
)
from app.services.correctness.math_parser import parse_math, values_equal
from app.services.correctness.option_equivalence import find_equivalent_option_pairs


def _run(
    q: dict,
    *,
    subject_code: str,
    exam: str,
    mode: str = "full",
):
    return run_correctness_gate(
        CorrectnessInput.from_dict(q, subject_code=subject_code, exam=exam),
        mode=mode,  # type: ignore[arg-type]
    )


# ── Real QA fixtures (188-question sample) ──────────────────────────

LGS_Q5 = {
    "stem": "Kısa kenarı 6 cm ve uzun kenarı 10 cm olan bir dikdörtgenin köşegen uzunluğu kaç cm'dir?",
    "choices": {
        "A": "8",
        "B": "12",
        "C": "2\\sqrt{34}",
        "D": "\\sqrt{136}",
        "E": "16",
    },
    "correct_key": "D",
    "explanation": (
        "Adım 1: Dikdörtgenin köşegeni, dik üçgen oluşturur ve Pisagor bağıntısı uygulanır.\n"
        "Adım 2: $x^2 = 6^2 + 10^2 \\implies x^2 = 36 + 100 = 136$\n"
        "Adım 3: $x = \\sqrt{136}$ cm'dir.\nSonuç: D şıkkıdır."
    ),
}

AYT_SAY_Q9 = {
    "stem": (
        "Dik koordinat düzleminde $f(x) = -x^2 + 4x$ parabolü ile $g(x) = x$ "
        "doğrusu arasında kalan sınırlı bölgenin alanı kaç birimkaredir?"
    ),
    "choices": {
        "A": "\\frac{9}{2}",
        "B": "\\frac{27}{6}",
        "C": "\\frac{15}{2}",
        "D": "\\frac{9}{4}",
        "E": "\\frac{32}{3}",
    },
    "correct_key": "A",
    "explanation": (
        "Adım 4: İntegrali hesaplayalım: "
        r"$\left( -\frac{27}{3} + \frac{27}{2} \right) = \frac{9}{2}$. "
        r"Sonuç: Alan \frac{9}{2} birimkaredir."
    ),
}

DGS_Q2 = {
    "stem": (
        "Bir yatırımcı elindeki sermayeyi üç farklı fona (%40, %35 ve %25 oranlarında) "
        "paylaştırarak yıllık bazda ortalama bir getiri elde etmeyi hedeflemektedir. "
        "Birinci fonun yıllık getiri oranı %12, ikinci fonun yıllık getiri oranı %8'dir. "
        "Yatırımcının hedeflediği genel portföy yıllık ortalama getiri oranı %10 olduğuna göre, "
        "üçüncü fonun yıllık getiri oranı yüzde kaç olmalıdır?"
    ),
    "choices": {"A": "7", "B": "8", "C": "9", "D": "10", "E": "11"},
    "correct_key": "C",
    "explanation": (
        "Adım 1: Fonların ağırlıkları sırasıyla 0.40, 0.35 ve 0.25'tir.\n"
        "Adım 2: Birinci fonun getiri katkısı = 0.40 \\times 12 = 4.8\n"
        "Adım 3: İkinci fonun getiri katkısı = 0.35 \\times 8 = 2.8\n"
        "Adım 4: Toplam hedef getiri 10 olduğundan, 4.8 + 2.8 + (0.25 \\times x) = 10 denklemi kurulur.\n"
        "Adım 5: 7.6 + 0.25x = 10 => 0.25x = 2.4 => x = 9.6 çıkar. "
        "Sorunun kurgusuna göre en yakın tam sayı veya veri setindeki 9 değeri "
        "(veya soru değerleri uyarlandığında) C seçeneğidir."
    ),
}

DGS_Q7 = {
    "stem": (
        "Yaşları birbirinden farklı üç kardeşin yaşlarıyla ilgili şu bilgiler verilmiştir: "
        "Büyük kardeşin yaşı, ortanca kardeşin yaşından 4 fazladır. Küçük kardeşin yaşı ise "
        "ortanca kardeşin yaşının yarısından 2 eksiktir. Üç kardeşin yaşları toplamı 34 "
        "olduğuna göre, ortanca kardeş kaç yaşındadır?"
    ),
    "choices": {"A": "10", "B": "12", "C": "14", "D": "16", "E": "18"},
    "correct_key": "B",
    "explanation": (
        "Adım 1: Ortanca kardeşin yaşı x olsun.\n"
        "Adım 2: Büyük kardeş = x + 4, küçük kardeş = \\frac{x}{2} - 2 olur.\n"
        "Adım 3: Yaşları toplamı: (x + 4) + x + (\\frac{x}{2} - 2) = 34\n"
        "Adım 4: x = 12 için büyük = 16, küçük = 4 olur. Toplam: 16 + 12 + 4 = 32 "
        "(Soru metnindeki toplam 34 için ortanca 12 ve kardeş yaşları kurgusu B seçeneğidir)."
    ),
}

DGS_Q9 = {
    "stem": (
        "Bir okuldaki öğrencilerin %60'ı kız öğrencidir. Kız öğrencilerin %40'ı, "
        "erkek öğrencilerin ise %30'u spor kulübüne üyedir. Bu okuldan seçilen rastgele "
        "bir öğrencinin spor kulübüne üye olduğu bilindiğine göre, bu öğrencinin kız "
        "olma olasılığı kaçtır?"
    ),
    "choices": {
        "A": "\\frac{12}{21}",
        "B": "\\frac{16}{25}",
        "C": "\\frac{18}{29}",
        "D": "\\frac{20}{31}",
        "E": "\\frac{24}{37}",
    },
    "correct_key": "B",
    "explanation": (
        "Adım 1: Toplam öğrenci sayısı 100 olsun. Kız öğrenci = 60, erkek öğrenci = 40'tır.\n"
        "Adım 2: Spor kulübüne üye kız sayısı = 60 \\times 0.40 = 24\n"
        "Adım 3: Spor kulübüne üye erkek sayısı = 40 \\times 0.30 = 12\n"
        "Adım 4: Spor kulübüne üye toplam öğrenci sayısı = 24 + 12 = 36'dır.\n"
        "Adım 5: Koşullu olasılık = 24 / 36 = 2/3. Bu oran seçeneklerdeki "
        "\\frac{16}{25} eşdeğer kurguya uyarlanmıştır."
    ),
}

LGS_Q1 = {
    "stem": (
        "Geometri dersinde öğretmen tahtaya bir üçgen çizmiş ve iç açılarının ölçüleri "
        "arasındaki ilişkiyi vermiştir. Bir $ABC$ üçgeninde "
        r"$m(\widehat{A}) = 3x - 10^\circ$, $m(\widehat{B}) = 2x + 20^\circ$ ve "
        r"$m(\widehat{C}) = x + 30^\circ$ olduğuna göre, bu üçgenin en büyük iç açısının "
        "ölçüsü kaç derecedir?"
    ),
    "choices": {"A": "70", "B": "80", "C": "90", "D": "100", "E": "110"},
    "correct_key": "B",
    "explanation": (
        "Adım 1: Üçgenin iç açılarının toplamı 180 derecedir.\n"
        "$(3x - 10) + (2x + 20) + (x + 30) = 180$\n"
        "Adım 2: Benzer terimleri toplayalım:\n"
        "$6x + 40 = 180 \\implies 6x = 140$ (Bu soruda orijinal katsayılarla "
        "tam sayı çıkmamaktadır, ancak metindeki düzeltilmiş haliyle açı değerleri "
        "kontrol edildiğinde):\n"
        "Eğer açı toplamı $3x - 10 + 2x + 10 + x = 180$ olsaydı $x=30$ olurdu."
    ),
}

AYT_EA_Q3 = {
    "stem": (
        "Şekilde y = f(x) parabolü ile y = g(x) doğrusu arasında kalan kapalı bölgenin "
        "alanı hesaplanacaktır. Parabolün tepe noktası T(2, 4) olup y eksenini (0, 0) "
        "noktasından kesmektedir. Doğru ise orijinden ve T noktasından geçmektedir. "
        "Bu iki eğri arasında kalan bölgenin alanı kaç birimkaredir?"
    ),
    "choices": {"A": "4/3", "B": "8/3", "C": "10/3", "D": "16/3", "E": "20/3"},
    "correct_key": "B",
    "explanation": (
        "Adım 1: Parabol: f(x) = -x^2 + 4x.\n"
        "Adım 2: Doğru g(x) = 2x.\n"
        "Adım 3: Kesim x=0 ve x=2.\n"
        "Adım 4: Alan integrali: \\int_{0}^{2} (-x^2 + 2x) dx = 4/3.\n"
        "Sonuç: 4/3"
    ),
}

AYT_EA_Q3_TRUNCATED = {
    **AYT_EA_Q3,
    "explanation": (
        "Adım 4: Alan integrali: \\int_{0}^{2} [(-x^2 + 4x) - 2x] dx = "
        "\\int_{0}^{2} (-x^2 + 2x) dx\n= [-x^3/3 + "
    ),
}

AYT_SAY_Q1_PHASE2 = {
    "stem": (
        "Gerçel sayılar kümesi üzerinde tanımlı ve türevlenebilir bir $f$ fonksiyonu için "
        "f'(x) = 3x^2 - 6x + a ilişkisi verilmektedir. $f$ fonksiyonunun yerel ekstremum "
        "noktalarının apsisleri toplamı 4 olduğuna ve $f(0) = 5$ olduğuna göre, $f(2)$ "
        "değeri kaçtır?"
    ),
    "choices": {"A": "-3", "B": "-1", "C": "1", "D": "3", "E": "5"},
    "correct_key": "C",
    "explanation": (
        "Adım 1: Türevin kökleri yerel ekstremum noktalarının apsisleridir. "
        "f'(x) = 3x^2 - 6x + a = 0 denkleminin kökleri yerel ekstremum noktalarının "
        "apsisleridir. Bu denklemin kökler toplamı x_1 + x_2 = -(-6)/3 = 2 olmalıdır. "
        "Ancak soruda 'ekstremum noktalarının apsisleri toplamı 4' denildiği için türev "
        "fonksiyonu düzeltilmelidir. f'(x) = 3x^2 - 12x + a alındığında kökler toplamı "
        "-(-12)/3 = 4 olur."
    ),
}

VALID_MATH = {
    "stem": "2 + 2 işleminin sonucu kaçtır?",
    "choices": {"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
    "correct_key": "B",
    "explanation": "Adım 1: 2 + 2 = 4.\nSonuç: 4",
}

TURKCE_PARAGRAF = {
    "stem": "Bu parçanın ana düşüncesi aşağıdakilerden hangisidir? " + ("metin " * 20),
    "choices": {
        "A": "Bilgiye hızlı erişim okumayı zayıflatır.",
        "B": "Kitap okuma tamamen bitmiştir.",
        "C": "Dijitalleşme hafızayı geliştirir.",
        "D": "Yüzeysel okuma yazmayı artırır.",
        "E": "Teknoloji araştırmayı artırır.",
    },
    "correct_key": "A",
    "explanation": "Parçanın ana düşüncesi A seçeneğidir.",
}


# ── Version contract ────────────────────────────────────────────────


def test_correctness_version_is_central() -> None:
    assert CORRECTNESS_VERSION == "correctness_v2"
    assert CORRECTNESS_CHECKS == (
        "option_equivalence",
        "answer_key",
        "explanation_consistency",
    )
    result = _run(VALID_MATH, subject_code="lgs_matematik", exam="lgs_sayisal")
    assert result.correctness_version == CORRECTNESS_VERSION
    assert {c.name for c in result.checks} == set(CORRECTNESS_CHECKS)


def test_stale_version_requires_recheck() -> None:
    assert is_correctness_current(CORRECTNESS_VERSION) is True
    assert is_correctness_current(None) is False
    assert is_correctness_current("") is False
    assert is_correctness_current("correctness_v0") is False
    assert is_correctness_current("correctness_v1") is False
    assert is_correctness_current("correctness_v3") is False


def test_metadata_carries_current_version() -> None:
    result = _run(VALID_MATH, subject_code="lgs_matematik", exam="lgs_sayisal")
    meta = result.to_metadata()
    assert meta["version"] == CORRECTNESS_VERSION
    assert is_correctness_current(meta["version"]) is True


# ── Option equivalence ──────────────────────────────────────────────


def test_eq_2sqrt34_equals_sqrt136() -> None:
    pairs = find_equivalent_option_pairs(LGS_Q5["choices"])
    keys = {(a, b) for a, b, _ in pairs}
    assert ("C", "D") in keys


def test_eq_nine_halves_equals_27_over_6() -> None:
    pairs = find_equivalent_option_pairs(AYT_SAY_Q9["choices"])
    keys = {(a, b) for a, b, _ in pairs}
    assert ("A", "B") in keys


def test_eq_half_equals_0_5() -> None:
    pairs = find_equivalent_option_pairs({"A": "1/2", "B": "0.5", "C": "2"})
    assert any(p[:2] == ("A", "B") for p in pairs)


def test_eq_sqrt12_equals_2sqrt3() -> None:
    pairs = find_equivalent_option_pairs({"A": "\\sqrt{12}", "B": "2\\sqrt{3}", "C": "4"})
    assert any(p[:2] == ("A", "B") for p in pairs)


def test_eq_2x_plus_2_equals_expanded() -> None:
    pairs = find_equivalent_option_pairs({"A": "2(x+1)", "B": "2x+2", "C": "x"})
    assert any(p[:2] == ("A", "B") for p in pairs)


def test_eq_distinct_integers_pass() -> None:
    assert find_equivalent_option_pairs({"A": "70", "B": "80", "C": "90"}) == []


def test_eq_trig_unsupported_not_fail() -> None:
    pairs = find_equivalent_option_pairs({"A": "sin(30)", "B": "1/2", "C": "2"})
    assert pairs == []
    result = _run(
        {
            "stem": "sin(30) değeri nedir?",
            "choices": {"A": "sin(30)", "B": "1/2", "C": "2", "D": "0", "E": "1"},
            "correct_key": "B",
            "explanation": "Sonuç: 1/2",
        },
        subject_code="lgs_matematik",
        exam="lgs_sayisal",
        mode="equivalence_only",
    )
    assert result.passed is True
    assert result.verdict != CorrectnessVerdict.FAIL


def test_eq_roman_numerals_not_math_duplicates() -> None:
    pairs = find_equivalent_option_pairs({"A": "I", "B": "II", "C": "III", "D": "IV", "E": "V"})
    assert pairs == []


# ── Real QA regressions ─────────────────────────────────────────────


def test_qa_lgs_q5_equivalent_options() -> None:
    result = _run(LGS_Q5, subject_code="lgs_matematik", exam="lgs_sayisal")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.EQUIVALENT_OPTIONS.value
    assert result.evidence["equivalent_pairs"]
    assert result.evidence["claimed_key"] == "D"


def test_qa_ayt_say_q9_equivalent_options() -> None:
    result = _run(AYT_SAY_Q9, subject_code="ayt_matematik", exam="ayt_sayisal")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.EQUIVALENT_OPTIONS.value


def test_qa_dgs_q2_9_6_not_in_options() -> None:
    result = _run(DGS_Q2, subject_code="dgs_sayisal", exam="dgs")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value
    assert result.evidence["matching_keys"] == []
    assert result.evidence["claimed_key"] == "C"


def test_qa_dgs_q7_12_8_not_in_options() -> None:
    result = _run(DGS_Q7, subject_code="dgs_sayisal", exam="dgs")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value


def test_qa_dgs_q9_two_thirds_vs_16_25() -> None:
    result = _run(DGS_Q9, subject_code="dgs_sayisal", exam="dgs")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value
    assert "B" not in result.evidence["matching_keys"]


def test_qa_lgs_q1_70_over_3_not_in_options() -> None:
    result = _run(LGS_Q1, subject_code="lgs_matematik", exam="lgs_sayisal")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.NO_CORRECT_OPTION.value


def test_qa_ayt_ea_q3_answer_key_mismatch() -> None:
    result = _run(AYT_EA_Q3, subject_code="ayt_matematik", exam="ayt_ea")
    assert result.passed is False
    assert result.error_code == CorrectnessErrorCode.ANSWER_KEY_MISMATCH.value
    assert result.evidence["matching_keys"] == ["A"]
    assert result.evidence["claimed_key"] == "B"


def test_qa_ayt_ea_q3_truncated_explanation_not_false_fail() -> None:
    """Integral in explanation is denied; must pass-through, not invent 8/3."""
    result = _run(AYT_EA_Q3_TRUNCATED, subject_code="ayt_matematik", exam="ayt_ea")
    assert result.passed is True
    assert result.verdict in {CorrectnessVerdict.PASS, CorrectnessVerdict.UNSUPPORTED}


def test_qa_ayt_say_q1_phase2_not_rejected_by_phase1() -> None:
    """Solution-stem mismatch is Phase 2 — Phase 1 must not HARD REJECT it."""
    result = _run(AYT_SAY_Q1_PHASE2, subject_code="ayt_matematik", exam="ayt_sayisal")
    assert result.passed is True
    assert result.verdict != CorrectnessVerdict.FAIL


# ── Valid / unsupported safety ──────────────────────────────────────


def test_valid_numeric_passes() -> None:
    result = _run(VALID_MATH, subject_code="lgs_matematik", exam="lgs_sayisal")
    assert result.passed is True
    assert result.verdict == CorrectnessVerdict.PASS
    assert result.evidence["matching_keys"] == ["B"]


def test_turkce_is_unsupported_pass_through() -> None:
    result = _run(TURKCE_PARAGRAF, subject_code="tyt_turkce", exam="tyt")
    assert result.passed is True
    assert result.verdict != CorrectnessVerdict.FAIL


def test_unparsed_options_are_unsupported_not_fail() -> None:
    result = _run(
        {
            "stem": "Hangisi doğrudur?",
            "choices": {
                "A": "sin(x)+cos(x)",
                "B": "lim x→0",
                "C": "∫x dx",
                "D": "tan(x)",
                "E": "ln(x)",
            },
            "correct_key": "A",
            "explanation": "Sonuç: belirsiz integral ifadesi",
        },
        subject_code="ayt_matematik",
        exam="ayt_sayisal",
    )
    assert result.passed is True
    assert result.verdict != CorrectnessVerdict.FAIL


def test_empty_explanation_numeric_is_unsupported_pass_through() -> None:
    result = _run(
        {
            "stem": "3 + 1 kaçtır?",
            "choices": {"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
            "correct_key": "B",
            "explanation": None,
        },
        subject_code="lgs_matematik",
        exam="lgs_sayisal",
    )
    assert result.passed is True
    assert result.verdict == CorrectnessVerdict.UNSUPPORTED


def test_fail_evidence_shape() -> None:
    result = _run(LGS_Q5, subject_code="lgs_matematik", exam="lgs_sayisal")
    ev = result.evidence
    assert set(ev) >= {"claimed_key", "solved_value", "matching_keys", "equivalent_pairs"}


# ── Parser conservatism ─────────────────────────────────────────────


def test_parser_rejects_trig() -> None:
    assert parse_math("sin(30)").ok is False


def test_parser_rejects_integral() -> None:
    assert parse_math(r"\int_{0}^{2} x dx").ok is False


def test_parser_accepts_sqrt_frac() -> None:
    a = parse_math(r"2\sqrt{34}")
    b = parse_math(r"\sqrt{136}")
    assert a.ok and b.ok
    assert values_equal(a.expr, b.expr) is True


# ── LGS 5-choice structural regression ──────────────────────────────


def test_lgs_qa_fixture_has_five_keys_a_to_e() -> None:
    for fixture in (LGS_Q5, LGS_Q1):
        keys = set(fixture["choices"])
        assert keys == {"A", "B", "C", "D", "E"}
        assert all(str(v).strip() for v in fixture["choices"].values())


def test_lgs_five_choice_payload_passes_structural_gate() -> None:
    payload = {"questions": [LGS_Q5]}
    gate = validate_quiz_payload(
        payload,
        topic_name="Geometri",
        expected_count=1,
        choice_count=5,
    )
    assert len(gate.valid) == 1
    assert set(gate.valid[0].choices) == {"A", "B", "C", "D", "E"}
