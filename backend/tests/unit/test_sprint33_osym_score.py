import pytest
from app.services.osym_score_calculator import SubjectNetInput, calculate_osym_score

def test_kpss_score_calculation():
    inputs = [
        SubjectNetInput(subject_code="kpss_matematik", correct_count=20, wrong_count=4), # 19 net
        SubjectNetInput(subject_code="kpss_turkce", correct_count=25, wrong_count=4),    # 24 net
    ]
    res = calculate_osym_score("kpss", inputs)
    assert res.exam_type == "kpss"
    assert res.total_net == 43.0
    assert res.estimated_score > 50.0
    assert "ÖSYM" in res.disclaimer

def test_tyt_score_calculation():
    inputs = [
        SubjectNetInput(subject_code="tyt_turkce", correct_count=30, wrong_count=4), # 29 net
        SubjectNetInput(subject_code="tyt_matematik", correct_count=20, wrong_count=4), # 19 net
    ]
    res = calculate_osym_score("tyt", inputs)
    assert res.exam_type == "tyt"
    assert res.total_net == 48.0
    assert res.estimated_score > 200.0
