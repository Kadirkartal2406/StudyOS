"""RC2 M22.2 — EI blueprint bridge unit tests (no new assessment logic)."""

from app.services.ai.exam_question_blueprint import ExamBlueprint, get_exam_blueprint
from app.services.ai.ei_blueprint import _legacy_or_code


class _Subj:
    def __init__(self, code, legacy=None):
        self.code = code
        self.legacy_subject_code = legacy


def test_legacy_or_code_prefers_legacy():
    assert _legacy_or_code(_Subj("ei_turkce", "tyt_turkce")) == "tyt_turkce"
    assert _legacy_or_code(_Subj("tyt_turkce", None)) == "tyt_turkce"


def test_hard_blueprint_still_available_as_fallback():
    bp = get_exam_blueprint("kpss", "lisans")
    assert isinstance(bp, ExamBlueprint)
    assert bp.total_count > 0
    assert any(s.subject_code.startswith("kpss_") for s in bp.sections)


def test_tyt_blueprint_sections():
    bp = get_exam_blueprint("tyt")
    codes = {s.subject_code for s in bp.sections}
    assert "tyt_turkce" in codes
    assert "tyt_matematik" in codes
