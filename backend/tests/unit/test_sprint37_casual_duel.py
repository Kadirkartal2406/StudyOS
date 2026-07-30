import pytest
from app.services.casual_duel_service import DuelMatchRead

def test_casual_duel_isolation_flag():
    import uuid
    match = DuelMatchRead(
        challenger_id=uuid.uuid4(),
        opponent_id=uuid.uuid4(),
        subject_code="kpss_matematik",
        status="active",
        questions=[],
        is_casual_duel=True,
    )
    assert match.is_casual_duel is True
    assert "akademiniz veya koçluk" in match.disclaimer.lower() or "eğlence" in match.disclaimer.lower()
