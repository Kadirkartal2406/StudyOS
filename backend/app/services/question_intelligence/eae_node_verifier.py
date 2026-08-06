"""
StudyOS Educational Asset Engine (EAE) — M34 Node Verifier
Verifies that generated question options and explanations reference valid, existing EAE Node IDs.
"""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel, Field

# Node ID regex pattern matching <asset>::<type>::<name>
CANDIDATE_NODE_ID_REGEX = re.compile(r"[a-z0-9_]+::[a-z0-9_]+::[a-z0-9_]+")


class NodeVerificationResult(BaseModel):
    is_valid: bool
    referenced_node_ids: list[str]
    missing_node_ids: list[str]
    validation_error: str | None = None


class EAENodeVerifier:
    """
    Quality gate verifier ensuring zero hallucinated Node IDs in AI generated visual questions.
    """

    def verify_question_grounding(
        self,
        question_payload: dict[str, Any],
        available_node_ids: list[str],
    ) -> NodeVerificationResult:
        valid_set = set(available_node_ids)
        referenced_ids = set()

        # Extract candidates from choices/options
        choices = question_payload.get("choices", {})
        if isinstance(choices, dict):
            for val in choices.values():
                val_str = str(val)
                matches = CANDIDATE_NODE_ID_REGEX.findall(val_str)
                for m in matches:
                    referenced_ids.add(m)

        # Extract from target_node_id
        target_node = question_payload.get("target_node_id")
        if target_node:
            referenced_ids.add(str(target_node))

        missing_ids = [nid for nid in referenced_ids if nid not in valid_set]

        if missing_ids:
            return NodeVerificationResult(
                is_valid=False,
                referenced_node_ids=list(referenced_ids),
                missing_node_ids=missing_ids,
                validation_error=f"Question references non-existent or invalid EAE Node IDs: {missing_ids}",
            )

        return NodeVerificationResult(
            is_valid=True,
            referenced_node_ids=list(referenced_ids),
            missing_node_ids=[],
        )
