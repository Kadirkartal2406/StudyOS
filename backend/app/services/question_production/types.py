"""M34.5 — shared dataclasses for production control."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CostGateResult:
    can_generate: bool
    reason: str | None
    daily_limit: int
    daily_remaining: int
    hourly_limit: int
    hourly_remaining: int
    minute_limit: int
    minute_remaining: int
    estimated_batch_cost: float
    suggested_batch_size: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LiveProgress:
    run_id: str = ""
    status: str = "idle"  # idle|running|stopping|stopped|completed|failed
    exam: str = ""
    subject_code: str = ""
    topic_code: str = ""
    difficulty_band: str = "medium"
    planned: int = 0
    current_index: int = 0
    accepted: int = 0
    rejected: int = 0
    rewrite: int = 0
    failed: int = 0
    gemini_calls: int = 0
    estimated_cost: float = 0.0
    remaining: int = 0
    last_preview: dict[str, Any] | None = None
    approval_mode: str = "auto"  # auto|manual
    started_at: str | None = None
    updated_at: str | None = None
    cost_report: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PendingQuestion:
    id: str
    stem: str
    choices: dict[str, str]
    correct_key: str
    explanation: str | None
    scores: dict[str, Any]
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str
    plan: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BatchCostReport:
    gemini_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost: float = 0.0
    questions_generated: int = 0
    questions_accepted: int = 0
    questions_rejected: int = 0
    average_cost_per_question: float = 0.0
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
