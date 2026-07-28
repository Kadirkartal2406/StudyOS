"""Virtual student profile definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudentProfile:
    name: str
    skill: float  # 0–1 accuracy tendency
    speed: float  # reading speed multiplier (>1 faster)
    carelessness: float  # 0–1 chance to pick attractive wrong
    overthink: float  # 0–1 preference for complex distractors
    prefers_rules: bool = False
    prefers_inference: bool = False


PROFILES: tuple[StudentProfile, ...] = (
    StudentProfile("High Performer", skill=0.92, speed=1.1, carelessness=0.05, overthink=0.1, prefers_inference=True),
    StudentProfile("Average Student", skill=0.62, speed=1.0, carelessness=0.2, overthink=0.25),
    StudentProfile("Weak Student", skill=0.35, speed=0.85, carelessness=0.35, overthink=0.2),
    StudentProfile("Fast Reader", skill=0.58, speed=1.45, carelessness=0.28, overthink=0.1),
    StudentProfile("Slow Reader", skill=0.6, speed=0.65, carelessness=0.15, overthink=0.3),
    StudentProfile("Careless Student", skill=0.55, speed=1.2, carelessness=0.55, overthink=0.1),
    StudentProfile("Overthinker", skill=0.7, speed=0.75, carelessness=0.1, overthink=0.7, prefers_inference=True),
    StudentProfile("Rule Memorizer", skill=0.5, speed=1.0, carelessness=0.2, overthink=0.15, prefers_rules=True),
    StudentProfile("Inference Thinker", skill=0.78, speed=0.95, carelessness=0.12, overthink=0.35, prefers_inference=True),
)


def all_profiles() -> list[StudentProfile]:
    return list(PROFILES)
