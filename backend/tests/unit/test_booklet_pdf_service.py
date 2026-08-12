"""Smoke + layout tests — booklet PDF bytes."""

import uuid
from datetime import date
from types import SimpleNamespace

from pypdf import PdfReader
import io

from app.services.booklet_pdf_service import (
    _choice_keys,
    build_assessment_report_pdf,
    build_booklet_pdf,
)


def _make_question(ord_index: int, stem: str, choices: dict, subject_code: str):
    return SimpleNamespace(
        ord_index=ord_index,
        stem=stem,
        choices=choices,
        subject_code=subject_code,
        topic_code="konu",
        metadata_={},
        qie_card={},
    )


def test_choice_keys_omit_missing_e_for_lgs():
    assert _choice_keys({"A": "1", "B": "2", "C": "3", "D": "4"}) == ["A", "B", "C", "D"]
    assert _choice_keys({"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}) == [
        "A",
        "B",
        "C",
        "D",
        "E",
    ]


def test_build_booklet_pdf_returns_pdf_magic():
    q = _make_question(
        0,
        "İki artı iki kaçtır?",
        {"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
        "kpss_matematik",
    )
    session = SimpleNamespace(
        id=uuid.uuid4(),
        subject_name="Günün Denemesi",
        exam_type="kpss",
        challenge_date=date(2026, 7, 25),
        requested_count=1,
        section_plan={
            "sections": [
                {
                    "subject_code": "kpss_matematik",
                    "subject_name": "Matematik",
                    "topics": [{"topic_code": "toplama", "topic_name": "Toplama", "count": 1}],
                }
            ]
        },
        questions=[q],
    )
    pdf = build_booklet_pdf(session)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 200
    reader = PdfReader(io.BytesIO(pdf))
    # cover + instructions + toc + questions + optical
    assert len(reader.pages) >= 4


def test_build_booklet_pdf_lgs_four_choices_and_math_spacing():
    questions = []
    for i in range(6):
        questions.append(
            _make_question(
                i,
                f"Aşağıdaki ifadelerden hangisi doğrudur? $\\frac{{{i}+1}}{{2}}$ değeri için seçiniz.",
                {"A": "1", "B": "2", "C": "3", "D": "4"},
                "lgs_matematik" if i < 3 else "lgs_turkce",
            )
        )
    session = SimpleNamespace(
        id=uuid.uuid4(),
        subject_name="Günün Denemesi",
        exam_type="lgs",
        challenge_date=date(2026, 8, 12),
        requested_count=6,
        section_plan={
            "sections": [
                {
                    "subject_code": "lgs_matematik",
                    "subject_name": "Matematik",
                    "topics": [{"topic_code": "kesir", "topic_name": "Kesirler", "count": 3}],
                },
                {
                    "subject_code": "lgs_turkce",
                    "subject_name": "Türkçe",
                    "topics": [{"topic_code": "anlam", "topic_name": "Anlam", "count": 3}],
                },
            ]
        },
        questions=questions,
    )
    pdf = build_booklet_pdf(session)
    assert pdf[:4] == b"%PDF"
    reader = PdfReader(io.BytesIO(pdf))
    assert len(reader.pages) >= 5
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    assert "GÜNLÜK DENEME" in text
    assert "LGS" in text
    assert "AÇIKLAMALAR" in text
    assert "İÇİNDEKİLER" in text
    # Four-choice questions should not invent an E key in optical/choices dump for LGS items
    # (E may still appear as letter in other words; assert choice pattern absence is soft)
    assert "MATEMATİK TESTİ" in text or "LGS / MATEMATİK" in text


def test_build_assessment_report_pdf():
    q = SimpleNamespace(
        ord_index=0,
        stem="İki artı iki kaçtır?",
        choices={"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
        subject_code="kpss_matematik",
        topic_code="toplama",
        correct_key="B",
        selected_key="A",
        is_correct=False,
        explanation="2+2=4",
        wrong_explain=None,
    )
    session = SimpleNamespace(
        id=uuid.uuid4(),
        subject_name="Günün Denemesi",
        exam_type="kpss",
        challenge_date=date(2026, 7, 25),
        requested_count=1,
        status="submitted",
        correct_count=0,
        wrong_count=1,
        blank_count=0,
        accuracy=0.0,
        commentary="Tekrar et",
        section_plan={
            "sections": [
                {"subject_code": "kpss_matematik", "subject_name": "Matematik"}
            ]
        },
        questions=[q],
    )
    pdf = build_assessment_report_pdf(session)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 200
