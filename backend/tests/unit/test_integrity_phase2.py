"""Phase 2 integrity — unit + pipeline tests. Phase 1 gate remains unchanged."""

from __future__ import annotations

from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.correctness import (
    CORRECTNESS_CHECKS,
    CORRECTNESS_VERSION,
    CorrectnessErrorCode,
    CorrectnessInput,
    CorrectnessVerdict,
    evaluate_item_correctness,
    run_correctness_gate,
    run_integrity_gate,
)
from app.services.correctness.choice_count import expected_choice_count
from app.services.qie.types import QuestionPlan
from tests.unit.test_correctness_gate import AYT_SAY_Q1_PHASE2, LGS_Q5, VALID_MATH
from tests.unit.test_correctness_phase1_integration import (
    _m34_pass,
    _plan,
    _run_batch,
    _run_orch_fresh,
)

DGS_Q5_NOTEBOOKS = {
    "stem": (
        "Bir kırtasiyeci defterleri koliler halinde alıp tanesi üzerinden satmaktadır. "
        "Aldığı bir koli defterin maliyeti 480 TL'dir. Kolideki defterlerin %20'si "
        "taşıma sırasında hasar gördüğü için satılamamıştır. Kırtasiyeci kalan "
        "defterlerin tanesini kaç TL'den satarsa tüm satış sonucunda %25 kâr elde etmiş olur?"
    ),
    "choices": {"A": "15", "B": "18", "C": "20", "D": "24", "E": "30"},
    "correct_key": "C",
    "explanation": (
        "Adım 2: Kolide 40 defter olduğu varsayılırsa, hasar oranı %20 olduğunda "
        "8 defter hasar görür ve 32 defter sağlam kalır."
    ),
}

DGS_Q4_MOTION = {
    "stem": (
        "Şehirler arası bir yolda hareket eden iki araçtan birincisi saatte 70 km, "
        "ikincisi ise saatte 90 km hızla aynı anda aynı noktadan aynı yöne doğru "
        "hareket etmiştir. Hızlı olan araç gideceği yere ulaştıktan hemen sonra geri "
        "dönmüş ve ilk araçla karşılaşmıştır. İki aracın ilk karşılaşmasından sonraki "
        "bu ikinci karşılaşma başlangıç noktasından kaç kilometre uzakta gerçekleşmiştir?"
    ),
    "choices": {"A": "315", "B": "335", "C": "350", "D": "375", "E": "395"},
    "correct_key": "A",
    "explanation": "Adım 1: Hız oranı 9/7'dir. Sonuç: 315 km.",
}

ALGEBRA_OK = {
    "stem": "y = 2(x+1) ifadesinin açılımı aşağıdakilerden hangisidir?",
    "choices": {"A": "2x+2", "B": "2x+1", "C": "x+2", "D": "2x", "E": "x+1"},
    "correct_key": "A",
    "explanation": "Adım 1: y = 2(x+1) = 2x+2.\nSonuç: 2x+2",
}

MISSING_GRAPH = {
    "stem": "Aşağıdaki grafikte f fonksiyonunun grafiği verilmektedir. f(2) kaçtır?",
    "choices": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
    "correct_key": "B",
    "explanation": "Grafikten okunur.",
}

MISSING_PASSAGE = {
    "stem": "According to the passage, the author's main claim is which of the following?",
    "choices": {"A": "A", "B": "B", "C": "C", "D": "D", "E": "E"},
    "correct_key": "A",
    "explanation": "The passage supports A.",
}

INLINE_PASSAGE = {
    "stem": (
        "The passage: " + ("Institutions gain trust when they explain decisions clearly. " * 12)
        + "According to the passage, the author's main claim is which of the following?"
    ),
    "choices": {
        "A": "Trust needs explanation",
        "B": "Trust is random",
        "C": "X",
        "D": "Y",
        "E": "Z",
    },
    "correct_key": "A",
    "explanation": "The passage argues that explanation builds trust.",
}

LGS_4 = {
    "stem": "2 + 2 işleminin sonucu kaçtır?",
    "choices": {"A": "3", "B": "4", "C": "5", "D": "6"},
    "correct_key": "B",
    "explanation": "Adım 1: 2 + 2 = 4.\nSonuç: 4",
}

LGS_5_UNIQUE = {
    "stem": "2 + 2 işleminin sonucu kaçtır?",
    "choices": {"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
    "correct_key": "B",
    "explanation": "Adım 1: 2 + 2 = 4.\nSonuç: 4",
}

ORDER_OK = {
    "stem": (
        "Hangisi doğru sıralamadır?\n"
        "I. Öncelikle tohum ekilir.\n"
        "II. Daha sonra tarla sulanır.\n"
        "III. Bunun sonucunda filizlenir."
    ),
    "choices": {
        "A": "I-II-III",
        "B": "II-I-III",
        "C": "III-II-I",
        "D": "I-III-II",
        "E": "II-III-I",
    },
    "correct_key": "A",
    "explanation": "Öncelikle, sonra, sonuç sırası I-II-III.",
}

ORDER_AMBIG = {
    "stem": (
        "Hangisi doğru sıralamadır?\n"
        "I. Ali okula gitti.\n"
        "II. Veli evde kaldı.\n"
        "III. Ayşe kitap okudu."
    ),
    "choices": {
        "A": "I-II-III",
        "B": "II-I-III",
        "C": "III-II-I",
        "D": "I-III-II",
        "E": "II-III-I",
    },
    "correct_key": "A",
    "explanation": "Sıralama A.",
}

ORDER_UNSUPPORTED = {
    "stem": "Hangisi doğru sıralamadır? Metindeki göndermeler karmaşıktır.",
    "choices": {
        "A": "I-II-III",
        "B": "II-I-III",
        "C": "III-I-II",
        "D": "I-III-II",
        "E": "II-III-I",
    },
    "correct_key": "A",
    "explanation": "A",
}


def _item(q: dict) -> ValidatedQuizItem:
    return ValidatedQuizItem(
        stem=q["stem"],
        choices=dict(q["choices"]),
        correct_key=q["correct_key"],
        explanation=q.get("explanation"),
        eae_interaction=q.get("eae_interaction"),
    )


def _integ(q: dict, *, exam: str, subject: str):
    return run_integrity_gate(
        CorrectnessInput.from_dict(q, subject_code=subject, exam=exam)
    )


def test_phase1_gate_contract_unchanged() -> None:
    assert CORRECTNESS_VERSION == "correctness_v2"
    assert CORRECTNESS_CHECKS == (
        "option_equivalence",
        "answer_key",
        "explanation_consistency",
    )
    result = run_correctness_gate(
        CorrectnessInput.from_dict(
            AYT_SAY_Q1_PHASE2, subject_code="ayt_matematik", exam="ayt_sayisal"
        )
    )
    assert result.verdict != CorrectnessVerdict.FAIL


def test_sc01_ayt_q1_solution_stem_mismatch() -> None:
    r = _integ(AYT_SAY_Q1_PHASE2, exam="ayt_sayisal", subject="ayt_matematik")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value
    assert r.evidence["solution_consistency"]["changed_equations"]


def test_sc02_dgs_q5_unexpected_assumption() -> None:
    r = _integ(DGS_Q5_NOTEBOOKS, exam="dgs_sayisal", subject="dgs_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value
    assert "40" in r.evidence["solution_consistency"]["unexpected_literals"]


def test_sc03_valid_algebraic_transformation() -> None:
    r = _integ(ALGEBRA_OK, exam="ayt_sayisal", subject="ayt_matematik")
    sc = next(c for c in r.checks if c.name == "solution_consistency")
    assert sc.status == "pass"


def test_sv01_dgs_q4_unsolvable() -> None:
    r = _integ(DGS_Q4_MOTION, exam="dgs_sayisal", subject="dgs_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.UNSOLVABLE.value


def test_sv02_dgs_q5_insufficient_information() -> None:
    q = dict(DGS_Q5_NOTEBOOKS)
    q["explanation"] = "Adım 1: Maliyet 480 TL'dir."
    r = _integ(q, exam="dgs_sayisal", subject="dgs_sayisal")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.UNSOLVABLE.value


def test_sv03_valid_solvable_math() -> None:
    r = _integ(VALID_MATH, exam="ayt_sayisal", subject="ayt_matematik")
    sv = next(c for c in r.checks if c.name == "solvability")
    assert sv.status == "pass"


def test_as01_missing_graph() -> None:
    r = _integ(MISSING_GRAPH, exam="ayt_ea", subject="ayt_matematik")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.MISSING_REQUIRED_ASSET.value


def test_as02_missing_passage() -> None:
    r = _integ(MISSING_PASSAGE, exam="yds", subject="yds_ingilizce")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.MISSING_REQUIRED_ASSET.value


def test_as03_valid_asset_backed() -> None:
    r = _integ(INLINE_PASSAGE, exam="yds", subject="yds_ingilizce")
    asset = next(c for c in r.checks if c.name == "asset")
    assert asset.status == "pass"


def test_lg01_lgs_five_choices_rejected() -> None:
    assert expected_choice_count("lgs") == 4
    assert expected_choice_count("lgs_sayisal") == 4
    r = _integ(LGS_5_UNIQUE, exam="lgs_sayisal", subject="lgs_matematik")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.INVALID_CHOICE_COUNT.value


def test_lg02_lgs_four_choices_pass() -> None:
    r = _integ(LGS_4, exam="lgs_sayisal", subject="lgs_matematik")
    cc = next(c for c in r.checks if c.name == "choice_count")
    assert cc.status == "pass"


def test_lg_other_exams_keep_five() -> None:
    assert expected_choice_count("tyt") == 5
    assert expected_choice_count("ayt_sayisal") == 5
    assert expected_choice_count("kpss") == 5
    assert expected_choice_count("dgs") == 5
    assert expected_choice_count("ales") == 5
    assert expected_choice_count("yds") == 5
    r = _integ(VALID_MATH, exam="tyt", subject="tyt_matematik")
    cc = next(c for c in r.checks if c.name == "choice_count")
    assert cc.status == "pass"


def test_or01_unambiguous_ordering() -> None:
    r = _integ(ORDER_OK, exam="ales", subject="ales_sozel")
    od = next(c for c in r.checks if c.name == "ordering")
    assert od.status == "pass"
    assert od.evidence.get("valid_orders") == 1


def test_or02_multiple_valid_orders() -> None:
    r = _integ(ORDER_AMBIG, exam="ales", subject="ales_sozel")
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.AMBIGUOUS_ORDERING.value


def test_or03_unsupported_semantic_case() -> None:
    r = _integ(ORDER_UNSUPPORTED, exam="ales", subject="ales_sozel")
    od = next(c for c in r.checks if c.name == "ordering")
    assert od.status == "unsupported"
    assert r.passed is True


def test_p2_evaluate_combines_phase1_and_phase2() -> None:
    plan = _plan()
    r = evaluate_item_correctness(_item(AYT_SAY_Q1_PHASE2), plan)
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value
    assert r.evidence["integrity"]["verdict"] == "fail"


def test_p2_phase1_fail_still_rejects_without_needing_phase2() -> None:
    plan = _plan()
    r = evaluate_item_correctness(_item(LGS_Q5), plan)
    assert r.passed is False
    assert r.error_code == CorrectnessErrorCode.EQUIVALENT_OPTIONS.value
    assert "integrity" not in (r.evidence or {})


async def test_p2_01_phase2_fail_no_pool_write(monkeypatch) -> None:
    cards, pool = await _run_orch_fresh(monkeypatch, AYT_SAY_Q1_PHASE2, m34=_m34_pass)
    assert cards == []
    pool.put_card.assert_not_called()


async def test_p2_02_phase2_pass_normal_pipeline(monkeypatch) -> None:
    cards = await _run_batch(monkeypatch, VALID_MATH, m34=_m34_pass)
    assert len(cards) == 1
    assert cards[0].correctness_meta["verdict"] == "pass"


async def test_p2_03_phase2_unsupported_passthrough(monkeypatch) -> None:
    from tests.unit.test_correctness_gate import TURKCE_PARAGRAF

    plan = _plan(
        exam="tyt",
        subject_code="tyt_turkce",
        subject_name="Türkçe",
        topic_code="paragraf",
        topic_name="Paragraf",
        skill="inference",
    )
    cards = await _run_batch(monkeypatch, TURKCE_PARAGRAF, m34=_m34_pass, plan=plan)
    assert len(cards) == 1
    assert cards[0].correctness_meta["verdict"] == "unsupported"


async def test_p2_04_phase1_fail_still_rejects(monkeypatch) -> None:
    cards = await _run_batch(monkeypatch, LGS_Q5, m34=_m34_pass)
    assert cards == []


async def test_p2_05_phase1_pass_phase2_fail_reject(monkeypatch) -> None:
    cards = await _run_batch(monkeypatch, AYT_SAY_Q1_PHASE2, m34=_m34_pass)
    assert cards == []


async def test_p2_06_all_gates_pass_pool_write(monkeypatch) -> None:
    cards, pool = await _run_orch_fresh(monkeypatch, VALID_MATH, m34=_m34_pass)
    assert len(cards) == 1
    pool.put_card.assert_awaited()
    assert cards[0].correctness_meta["verdict"] == "pass"
    assert "integrity" in cards[0].correctness_meta
