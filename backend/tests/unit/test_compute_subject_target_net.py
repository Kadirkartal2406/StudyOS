"""Overall exam target must not become each subject's hedef."""

from app.services.subject_net_targets import (
    compute_subject_target_net,
    exam_total_question_count,
    official_subject_question_count,
)


def test_kpss_overall_85_distributes_to_matematik():
    q = official_subject_question_count(exam_type="kpss", subject_name="Matematik")
    total = exam_total_question_count("kpss")
    assert q == 30
    assert total == 120
    tgt = compute_subject_target_net(
        user_target_net=85,
        subject_question_count=q,
        total_question_count=total,
    )
    # 85 * (30/120) = 21.25
    assert 20 <= tgt <= 22
    assert tgt < 85


def test_explicit_per_subject_target_capped_by_capacity():
    tgt = compute_subject_target_net(
        user_target_net=20,
        subject_question_count=30,
        total_question_count=120,
    )
    assert tgt == 20.0


def test_kpss_total_ignores_alias_double_count():
    assert exam_total_question_count("kpss") == 120
