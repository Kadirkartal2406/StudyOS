from __future__ import annotations

from app.services.question_intelligence.blueprint_matcher import match_blueprint
from app.services.question_intelligence.exam_feel_v2 import detect_exam_feel_v2
from app.services.question_intelligence.auto_repair import auto_repair
from app.services.question_intelligence.pipeline import evaluate_question
from app.services.question_intelligence.uniqueness_checker import check_uniqueness


def _plan_dict() -> dict:
    return {
        "paragraph_length": 90,
        "reading_time_sec": 45,
        "difficulty": 75,
        "reasoning_type": "inference",
        "stem_type": "inference",
        "distractor_pattern": "meaning_shift",
        "choice_count": 5,
    }


def _balanced_question(*, include_ai_smell: bool = False) -> dict:
    if include_ai_smell:
        opener = "Bu metne göre"
        extra = "Aşağıdaki seçeneklerden"
    else:
        opener = "Aşağıdakilerden"
        extra = "hangisi"

    stem = (
        f"{opener} yazarın vurguladığı ana düşünceyi {extra} en iyi ifade eder? "
        "Kurumların şeffaflığı arttıkça güven ilişkisi güçlenir; buna bağlı olarak "
        "denetim mekanizmalarının da etkinleştirilmesi gerektiği belirtilir. "
        "Buna göre kamuoyunun denetim araçlarının çeşitlendirilmesi ve raporlamanın "
        "süreklilik taşıması gerekir; aksi durumda güven ilişkisi zayıflar. "
        "Yazar, yalnızca bilgi paylaşımının değil aynı zamanda gerekçeli açıklamaların "
        "ve geri bildirim mekanizmalarının da kalıcı davranış değişikliğine "
        "katkı sağladığını vurgular. "
        "Bu nedenle paragrafta savunulan temel düşünce, hesap verebilirliğin "
        "güveni besleyen en kritik koşul olduğudur."
    )
    choices = {
        "A": "Kurumsal şeffaflık güvenin önkoşuludur",
        "B": "Bireysel sorumluluk gereksizdir",
        "C": "Değişim yalnızca rastlantısaldır",
        "D": "Metin yalnızca tarih bilgisini aktarır",
        "E": "Yazar mizah unsuru kullanır",
    }
    return {"stem": stem, "choices": choices, "correct_key": "A", "explanation": None}


def test_exam_feel_v2_banned_phrase_fails():
    q = _balanced_question(include_ai_smell=True)
    res = detect_exam_feel_v2(q)
    assert res.passed is False
    assert res.score < 70


def test_auto_repair_removes_smell_and_improves_exam_feel():
    q = _balanced_question(include_ai_smell=True)
    repaired, repair_result = auto_repair(q)
    assert repair_result.repaired is True
    repaired_res = detect_exam_feel_v2(repaired)
    assert repaired_res.passed is True


def test_blueprint_match_reasonable_question_high_score():
    q = _balanced_question(include_ai_smell=False)
    bp = match_blueprint(q, _plan_dict(), style_dna={})
    assert bp.score >= 85


def test_uniqueness_checker_rejects_near_duplicate():
    q = _balanced_question(include_ai_smell=False)
    existing = [q["stem"]]
    uq = check_uniqueness(q["stem"], existing_stems=existing, threshold=0.55)
    assert uq.is_unique is False


def test_evaluate_question_rejects_when_blueprint_low():
    # Very short stem → blueprint should drop below 85
    q = {"stem": "Hangisi doğrudur?", "choices": {"A": "x", "B": "y", "C": "z", "D": "w", "E": "t"}, "correct_key": "A"}
    result = evaluate_question(q, _plan_dict(), style_dna={}, existing_stems=[])
    assert result["accepted"] is False
    assert str(result["reject_reason"]).startswith("blueprint_low:")

