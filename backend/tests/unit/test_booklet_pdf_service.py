"""Smoke test — booklet PDF bytes."""

import uuid
from datetime import date
from types import SimpleNamespace

from app.services.booklet_pdf_service import (
    build_assessment_report_pdf,
    build_booklet_pdf,
)


def test_build_booklet_pdf_returns_pdf_magic():
    q = SimpleNamespace(
        ord_index=0,
        stem="İki artı iki kaçtır?",
        choices={"A": "3", "B": "4", "C": "5", "D": "6", "E": "7"},
        subject_code="kpss_matematik",
        topic_code="toplama",
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
                }
            ]
        },
        questions=[q],
    )
    pdf = build_booklet_pdf(session)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 200


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
