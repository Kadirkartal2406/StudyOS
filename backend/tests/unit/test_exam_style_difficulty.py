"""Sprint 23 — difficulty analyzer + exam score unit tests."""

from decimal import Decimal

from app.services.ai.difficulty_analyzer import analyze_question_difficulty
from app.services.ai.quiz_quality_gate import ValidatedQuizItem
from app.services.exam_net import compute_exam_net, compute_exam_score
from app.services.exam_style.seed import build_exam_style_seed


def test_exam_style_seed_covers_core_exams():
    codes = {r["exam_code"] for r in build_exam_style_seed()}
    for need in ("kpss", "tyt", "ayt", "ales", "lgs", "dgs", "yds", "ags"):
        assert need in codes


def test_compute_exam_net_yks_penalty():
    assert compute_exam_net(12, 4) == Decimal("11.00")


def test_lgs_no_wrong_penalty():
    r = compute_exam_score(correct=40, wrong=10, blank=0, exam_type="lgs")
    assert r.net == Decimal("40.00")
    assert r.penalty_per_wrong == Decimal("0")


def test_kpss_net_with_penalty():
    r = compute_exam_score(correct=80, wrong=20, blank=20, exam_type="kpss", total_questions=120)
    assert r.net == Decimal("75.00")
    assert r.success_pct == round(80 / 120 * 100, 2)


def test_difficulty_rejects_short_paragraph_style():
    item = ValidatedQuizItem(
        stem="Hangisi doğrudur?",
        choices={"A": "x", "B": "y", "C": "z", "D": "w", "E": "q"},
        correct_key="A",
    )
    score = analyze_question_difficulty(
        item,
        style={
            "paragraph_words": "180-220",
            "difficulty": "high",
            "reasoning_type": "inference",
        },
        topic_name="Paragraf",
    )
    assert score.score < 70
    assert not score.passed


def test_difficulty_accepts_long_self_contained():
    stem = (
        "Bir yazar, toplumsal değişimin bireysel tercihlerle sınırlı olmadığını "
        "savunarak kurumların rolüne dikkat çeker. Metne göre yazarın asıl "
        "vurgusu aşağıdakilerden hangisidir? "
        "Kurumsal yapılar olmadan bireysel tercihler toplumsal dönüşümü "
        "açıklamakta yetersiz kalır çünkü sistematik baskılar tercih alanını "
        "biçimlendirir ve tarihsel süreklilik bireysel iradeden bağımsız "
        "mekanizmalar üretir."
    )
    item = ValidatedQuizItem(
        stem=stem,
        choices={
            "A": "Bireysel tercihler her şeyi açıklar",
            "B": "Kurumlar tercihi biçimlendirir",
            "C": "Tarih önemsizdir",
            "D": "Yazar kurumları reddeder",
            "E": "Değişim rastgeledir",
        },
        correct_key="B",
    )
    score = analyze_question_difficulty(
        item,
        style={"paragraph_words": "40-200", "difficulty": "high", "reasoning_type": "inference"},
        topic_name="Paragraf",
    )
    assert score.passed
