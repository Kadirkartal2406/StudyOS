"""Planner draft read — legacy parent exam codes must not 500 dashboard."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from app.models.planner_draft import PlannerDraftStatus
from app.models.question_record import ExamType
from app.services.planner_service import PlannerService, _coerce_exam_type


def test_coerce_exam_type_maps_legacy_kpss():
    assert _coerce_exam_type("kpss") == ExamType.KPSS_LISANS
    assert _coerce_exam_type("kpss_onlisans") == ExamType.KPSS_ONLISANS
    assert _coerce_exam_type(ExamType.TYT) == ExamType.TYT


def test_to_read_accepts_legacy_kpss_target_exam():
    draft = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=PlannerDraftStatus.DRAFT,
        target_exam="kpss",
        target_net=80.0,
        available_days=[0, 1, 2],
        available_hours=2.0,
        plan_payload={
            "items": [],
            "summary": {},
            "rationale": {"overview": "legacy kpss draft"},
        },
        created_at=datetime.now(UTC),
        accepted_at=None,
    )
    svc = object.__new__(PlannerService)
    read = svc._to_read(draft)
    assert read.target_exam == ExamType.KPSS_LISANS
    assert read.rationale["overview"] == "legacy kpss draft"
