"""
StudyOS — AI Settings şemaları (Sprint-2.4 E2)
"""

from pydantic import BaseModel, Field


class AiSettingsRead(BaseModel):
    preferred_provider: str | None = None
    preferred_model: str | None = None
    effective_provider: str
    effective_model: str | None = None
    fallback_provider: str = "null"
    available_providers: list[str] = Field(
        default_factory=lambda: ["null", "gemini", "openai", "claude"]
    )
    streaming_enabled: bool = False
    debug: dict = Field(default_factory=dict)


class AiSettingsUpdate(BaseModel):
    preferred_provider: str | None = Field(default=None, max_length=40)
    preferred_model: str | None = Field(default=None, max_length=120)
