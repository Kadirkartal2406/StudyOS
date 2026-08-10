"""Glue helpers for soft measurement side-channel (default OFF)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.services.ai.compact_generation_contract import (
    CompactGenerationContract,
    build_compact_generation_contract,
)
from app.services.ai.measurement_decision import MeasurementDecision, decide_measurement_action
from app.services.ai.soft_measurement_scorer import SoftMeasurementScore, score_against_contract
from app.services.ai_cost.measurement_flags import measurement_enabled, measurement_mode

logger = logging.getLogger("studyos.measurement")


def load_contract_for_context(
    *,
    exam: str | None,
    subject_code: str | None = None,
    topic_code: str | None = None,
) -> CompactGenerationContract | None:
    """Always load compact contract for prompt guidance when calibration exists.

    Scoring / regen / hold remain gated by MEASUREMENT_MODE inside
    apply_soft_measurement / decide_measurement_action (default off = noop).
    """
    return build_compact_generation_contract(
        exam=exam, subject_code=subject_code, topic_code=topic_code
    )


def prompt_block_from_contract(contract: CompactGenerationContract | None) -> str | None:
    if contract is None:
        return None
    return contract.to_prompt_block()


def inject_measurement_into_style(
    style: dict[str, Any] | None,
    contract: CompactGenerationContract | None,
) -> dict[str, Any]:
    out = dict(style or {})
    block = prompt_block_from_contract(contract)
    if block:
        out["measurement_soft_block"] = block
    return out


def quality_status_from_gate(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def apply_soft_measurement(
    *,
    stem: str,
    choices: dict[str, str] | list[str] | None,
    quality_passed: bool,
    contract: CompactGenerationContract | None,
    retry_count: int = 0,
    generation_id: str | None = None,
    subject: str | None = None,
    topic: str | None = None,
) -> tuple[SoftMeasurementScore | None, MeasurementDecision]:
    """Score + decide. When mode=off, returns noop decision without scoring."""
    mode = measurement_mode()
    q_status = quality_status_from_gate(quality_passed)
    if mode == "off":
        decision = decide_measurement_action(
            quality_status=q_status,
            score=None,
            mode=mode,
            retry_count=retry_count,
            generation_id=generation_id,
        )
        return None, decision

    choice_list: list[str]
    if isinstance(choices, dict):
        choice_list = [str(v) for v in choices.values()]
    elif isinstance(choices, list):
        choice_list = [str(v) for v in choices]
    else:
        choice_list = []

    score = score_against_contract(stem=stem, choices=choice_list, contract=contract)
    decision = decide_measurement_action(
        quality_status=q_status,
        score=score,
        mode=mode,
        retry_count=retry_count,
        generation_id=generation_id or str(uuid.uuid4()),
        exam_unit=contract.exam_unit if contract else None,
        subject=subject,
        topic=topic,
        contract_version=contract.contract_version if contract else None,
        visual_status=score.visual_status,
    )
    if mode == "shadow":
        logger.info(
            "measurement_shadow status=%s distance=%s exam_unit=%s final=%s",
            score.status,
            score.distance,
            contract.exam_unit if contract else None,
            decision.final_action,
        )
    elif mode == "soft_review":
        logger.info(
            "measurement_soft_review status=%s distance=%s final=%s autopool=%s regen=%s",
            score.status,
            score.distance,
            decision.final_action,
            decision.allow_autopool,
            decision.should_regen,
        )
    return score, decision


def measurement_meta_payload(
    score: SoftMeasurementScore | None,
    decision: MeasurementDecision,
) -> dict[str, Any]:
    return {
        **decision.provenance,
        "final_action": decision.final_action,
        "allow_autopool": decision.allow_autopool,
        "should_regen": decision.should_regen,
        "score": score.to_dict() if score else None,
    }


def allow_autopool_from_meta(meta: dict[str, Any] | None) -> bool:
    if not meta:
        return True
    if measurement_mode() == "off":
        return True
    if meta.get("final_action") == "measurement_review_hold":
        return False
    if meta.get("allow_autopool") is False:
        return False
    return True
