"""Admin + forgot-password smoke (unit-level imports / helpers)."""

from app.services.subject_net_targets import exam_total_question_count
from app.schemas.auth import ForgotPasswordResponse, ResetPasswordRequest
from app.schemas.admin import AdminOverview


def test_forgot_password_schema_defaults():
    r = ForgotPasswordResponse()
    assert r.email_sent is False
    assert r.dev_reset_token is None


def test_reset_password_schema_min_len():
    body = ResetPasswordRequest(token="x" * 24, new_password="password1")
    assert len(body.token) >= 20


def test_admin_overview_model():
    o = AdminOverview(
        users_total=1,
        users_active=1,
        users_admin=1,
        study_plans=0,
        study_sessions=0,
        question_records=0,
        generated_questions=0,
        pool_cards=0,
        exams=0,
        goals=0,
        conversations=0,
        beta_feedback=0,
    )
    assert o.users_admin == 1


def test_kpss_total_still_sane():
    assert exam_total_question_count("kpss") == 120
