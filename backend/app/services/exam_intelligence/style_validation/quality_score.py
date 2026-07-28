"""Per-contract quality score 0–100."""

from __future__ import annotations

from typing import Any


def score_contract(
    contract: dict[str, Any],
    *,
    contract_result: dict[str, Any] | None = None,
    reading_result: dict[str, Any] | None = None,
    reasoning_result: dict[str, Any] | None = None,
    trap_result: dict[str, Any] | None = None,
    difficulty_result: dict[str, Any] | None = None,
    bloom_result: dict[str, Any] | None = None,
    similarity_bonus: float = 0.0,
) -> dict[str, Any]:
    """
    Weights:
      completeness 25, reasoning 20, reading 15, trap 10,
      difficulty 10, bloom 10, similarity 10
    """
    c_res = contract_result or {}
    r_res = reading_result or {}
    reason_res = reasoning_result or {}
    t_res = trap_result or {}
    d_res = difficulty_result or {}
    b_res = bloom_result or {}

    completeness = 25.0 if c_res.get("passed", False) else max(
        0.0, 25.0 - 5.0 * len(c_res.get("issues") or [])
    )

    reasoning = 20.0 if reason_res.get("passed", True) else 8.0
    reasoning -= min(8.0, 2.0 * len(reason_res.get("warnings") or []))
    reasoning = max(0.0, reasoning)

    reading = 15.0 if r_res.get("passed", True) else 5.0
    reading -= min(6.0, 2.0 * len(r_res.get("warnings") or []))
    reading = max(0.0, reading)

    trap = 10.0 if t_res.get("passed", True) else 3.0
    trap -= min(4.0, 1.5 * len(t_res.get("warnings") or []))
    trap = max(0.0, trap)

    difficulty = 10.0 if d_res.get("passed", True) else 4.0
    if (d_res.get("max_jump") or 0) >= 3:
        difficulty -= 2.0
    difficulty = max(0.0, difficulty)

    bloom = 10.0 if b_res.get("passed", True) else 3.0
    bloom -= min(3.0, 1.5 * len(b_res.get("warnings") or []))
    bloom = max(0.0, bloom)

    # similarity_bonus in [0,1] from related pair pass rate contribution
    similarity = round(10.0 * max(0.0, min(1.0, similarity_bonus)), 2)

    total = round(
        completeness + reasoning + reading + trap + difficulty + bloom + similarity, 1
    )
    total = max(0.0, min(100.0, total))

    return {
        "topic_code": contract.get("topic_code"),
        "exam_code": contract.get("exam_code"),
        "breakdown": {
            "completeness": round(completeness, 1),
            "reasoning": round(reasoning, 1),
            "reading": round(reading, 1),
            "trap": round(trap, 1),
            "difficulty": round(difficulty, 1),
            "bloom": round(bloom, 1),
            "similarity": similarity,
        },
        "score": total,
    }
