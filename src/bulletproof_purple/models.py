"""Pydantic models for Purple Agent A2A server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PurpleAgentOutput(BaseModel):
    """Output schema for Purple Agent narrative generation results."""

    narrative: str
    metadata: dict[str, Any]
