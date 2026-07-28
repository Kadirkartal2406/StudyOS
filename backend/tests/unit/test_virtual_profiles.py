"""M31 virtual student profiles tests."""

from __future__ import annotations

from app.services.question_virtual_student.profiles import PROFILES, all_profiles


def test_expected_profiles_present():
    names = {p.name for p in all_profiles()}
    for required in (
        "High Performer",
        "Average Student",
        "Weak Student",
        "Fast Reader",
        "Slow Reader",
        "Careless Student",
        "Overthinker",
        "Rule Memorizer",
        "Inference Thinker",
    ):
        assert required in names


def test_profile_count():
    assert len(PROFILES) == 9
    assert all(0.0 <= p.skill <= 1.0 for p in PROFILES)
