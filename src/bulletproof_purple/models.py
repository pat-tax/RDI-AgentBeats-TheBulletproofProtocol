"""Pydantic models for Purple Agent A2A server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Narrative(BaseModel):
    """Structured narrative output with metadata."""

    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PurpleAgentOutput(BaseModel):
    """Output schema for Purple Agent narrative generation results."""

    narrative: str
    metadata: dict[str, Any]
