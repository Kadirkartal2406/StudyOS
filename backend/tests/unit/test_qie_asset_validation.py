"""
Unit tests for QIE M34 EAE Node Verifier.
"""

from app.services.question_intelligence.eae_node_verifier import EAENodeVerifier

def test_m34_node_verifier_valid_question():
    verifier = EAENodeVerifier()
    available = [
        "turkey_admin_v1::province::konya",
        "turkey_admin_v1::province::ankara",
    ]

    question_payload = {
        "stem": "Haritada gösterilen il hangisidir?",
        "choices": {
            "A": "turkey_admin_v1::province::konya",
            "B": "turkey_admin_v1::province::ankara",
        },
        "target_node_id": "turkey_admin_v1::province::konya",
    }

    res = verifier.verify_question_grounding(question_payload, available)
    assert res.is_valid
    assert len(res.referenced_node_ids) == 2
    assert res.missing_node_ids == []

def test_m34_node_verifier_missing_node_invalid():
    verifier = EAENodeVerifier()
    available = ["turkey_admin_v1::province::konya"]

    question_payload = {
        "stem": "Soru?",
        "choices": {"A": "turkey_admin_v1::province::non_existent_city"},
    }

    res = verifier.verify_question_grounding(question_payload, available)
    assert not res.is_valid
    assert "turkey_admin_v1::province::non_existent_city" in res.missing_node_ids
