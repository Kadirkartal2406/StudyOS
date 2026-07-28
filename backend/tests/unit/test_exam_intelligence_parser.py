"""M27 parser safety + heuristic unit tests (no PDF required)."""

from __future__ import annotations

import pytest

from app.services.exam_intelligence.parser.answer_key_locator import extract_answer_key
from app.services.exam_intelligence.parser.difficulty_estimator import estimate_difficulty
from app.services.exam_intelligence.parser.metadata_writer import write_json
from app.services.exam_intelligence.parser.question_locator import (
    LocatedQuestion,
    locate_questions,
)
from app.services.exam_intelligence.parser.reading_estimator import (
    estimate_reading_time_sec,
)
from app.services.exam_intelligence.parser.subject_detector import detect_subject_topic


def test_locate_questions_numbers_only():
    pages = [
        "1. Bu bir ornek sorudur. Ana dusunce nedir?\nA) x\nB) y\nC) z\nD) t\nE) u\n"
        "2. Ikinci soru metni burada.\nA) 1\nB) 2\nC) 3\nD) 4\nE) 5\n"
    ]
    qs = locate_questions(pages)
    assert [q.number for q in qs] == [1, 2]
    assert all(q.word_count > 0 for q in qs)


def test_answer_key_extractor():
    pages = ["CEVAP ANAHTARI\n1-A 2-C 3-D 4-B 5-E\n"]
    key = extract_answer_key(pages)
    assert key.get("1") == "A"
    assert key.get("2") == "C"


def test_difficulty_and_reading_no_text_fields():
    q = LocatedQuestion(
        number=1,
        page=1,
        _transient_text="ignored",
        word_count=150,
        sentence_count=7,
        option_lengths=[8, 9, 8, 7, 8],
        symbol_count=0,
        equation_count=0,
        has_table=False,
        has_visual_hint=False,
        multi_step=True,
    )
    d = estimate_difficulty(q)
    t = estimate_reading_time_sec(q)
    assert 5 <= d <= 98
    assert 5 <= t <= 180


def test_subject_topic_detection():
    det = detect_subject_topic(
        "kpss",
        "Paragraf sorusu ana düşünce ve yardımcı düşünce içerir.",
    )
    assert det.subject_code is not None
    assert "turkce" in (det.subject_code or "")
    assert det.skill_type in ("inference", "general", "language_rules")


def test_blueprint_tyt_ranges():
    from app.services.exam_intelligence.parser.topic_detector import assign_blueprint

    q1 = assign_blueprint("tyt", 1)
    q70 = assign_blueprint("tyt", 70)
    assert q1 and "turkce" in q1.subject_code
    assert "paragraf" in q1.topic_code
    assert q70 and "matematik" in q70.subject_code


def test_infer_identity_yokdil_pack(tmp_path):
    from app.services.exam_intelligence.parser.page_reader import infer_identity

    pdf = tmp_path / "yokdil" / "fen_bilimleri.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4")
    ident = infer_identity(pdf)
    assert ident.exam_code == "yokdil"
    assert ident.pack == "fen"
    assert ident.session_id == "fen"


def test_write_json_rejects_stem(tmp_path):
    with pytest.raises(ValueError):
        write_json(tmp_path / "bad.json", {"stem": "yasak metin", "question_count": 1})
    path = write_json(tmp_path / "ok.json", {"question_count": 10, "answer_key": {"1": "A"}})
    text = path.read_text(encoding="utf-8")
    assert "stem" not in text
    assert "yasak" not in text
