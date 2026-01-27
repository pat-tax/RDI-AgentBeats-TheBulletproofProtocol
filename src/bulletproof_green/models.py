"""Pydantic models for Green Agent A2A server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GreenAgentOutput(BaseModel):
    """AgentBeats-compatible output schema for Green Agent evaluation results."""

    # AgentBeats required fields
    domain: str
    score: float
    max_score: int
    pass_rate: float
    task_rewards: dict[str, float]
    time_used: float
    # Evaluation metrics
    overall_score: float
    correctness: float
    safety: float
    specificity: float
    experimentation: float
    classification: str
    risk_score: int
    risk_category: str
    confidence: float
    redline: dict[str, Any]
