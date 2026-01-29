"""Pydantic models for Green Agent - All data validation.

This module contains all Pydantic models used throughout the Green Agent:
- Request/Response models (A2A protocol)
- Evaluation models (rule-based evaluator)
- Score models (AgentBeats scoring)
- LLM judge models (hybrid scoring)

All models use model_validate() for incoming data validation from external sources.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class Issue(BaseModel):
    """Represents a detected issue in the narrative."""

    category: str
    severity: str
    text: str
    suggestion: str


class Redline(BaseModel):
    """Redline markup containing detected issues."""

    total_issues: int = 0
    issues: list[Issue] = Field(default_factory=list)
    critical: int = 0
    high: int = 0
    medium: int = 0


class EvaluationResult(BaseModel):
    """Structured evaluation result per Green-Agent-Metrics-Specification.md."""

    # Legacy fields (for backwards compatibility)
    classification: str = "NON_QUALIFYING"
    confidence: float = 0.0
    risk_score: int = 100
    risk_category: str = "CRITICAL"
    component_scores: dict[str, int] = Field(default_factory=dict)
    redline: Redline = Field(default_factory=Redline)

    # New schema fields
    version: str = "1.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    narrative_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    predicted_audit_outcome: str = "FAIL_AUDIT"

    # Diagnostic counters
    routine_patterns_detected: int = 0
    vague_phrases_detected: int = 0
    business_keywords_detected: int = 0
    experimentation_evidence_score: float = 0.0
    specificity_score: float = 0.0

    # Metadata
    evaluation_time_ms: float = 0.0
    rules_version: str = "1.0.0"
    irs_citations: list[str] = Field(
        default_factory=lambda: ["IRS Section 41(d)(1)", "26 CFR § 1.41-4"]
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert evaluation result to dictionary format per specification."""
        # Calculate total_penalty
        total_penalty = sum(
            [
                self.component_scores.get("routine_engineering_penalty", 0),
                self.component_scores.get("business_risk_penalty", 0),
                self.component_scores.get("vagueness_penalty", 0),
                self.component_scores.get("experimentation_penalty", 0),
                self.component_scores.get("specificity_penalty", 0),
            ]
        )

        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "narrative_id": self.narrative_id,
            "primary_metrics": {
                "compliance_classification": self.classification,
                "confidence": self.confidence,
                "risk_score": self.risk_score,
                "risk_category": self.risk_category,
                "predicted_audit_outcome": self.predicted_audit_outcome,
            },
            "component_scores": {
                "routine_engineering_penalty": self.component_scores.get(
                    "routine_engineering_penalty", 0
                ),
                "vagueness_penalty": self.component_scores.get("vagueness_penalty", 0),
                "business_risk_penalty": self.component_scores.get("business_risk_penalty", 0),
                "experimentation_penalty": self.component_scores.get("experimentation_penalty", 0),
                "specificity_penalty": self.component_scores.get("specificity_penalty", 0),
                "total_penalty": total_penalty,
            },
            "diagnostics": {
                "routine_patterns_detected": self.routine_patterns_detected,
                "vague_phrases_detected": self.vague_phrases_detected,
                "business_keywords_detected": self.business_keywords_detected,
                "experimentation_evidence_score": self.experimentation_evidence_score,
                "specificity_score": self.specificity_score,
            },
            "redline": self.redline.model_dump(),
            "metadata": {
                "evaluation_time_ms": self.evaluation_time_ms,
                "rules_version": self.rules_version,
                "irs_citations": self.irs_citations,
            },
        }


class ScoreResult(BaseModel):
    """AgentBeats-compatible score result.

    All scores are in the 0.0-1.0 scale where:
    - 1.0 = perfect score (no issues detected)
    - 0.0 = worst score (maximum penalties applied)
    """

    overall_score: float
    correctness: float
    safety: float
    specificity: float
    experimentation: float


class NarrativeRequest(BaseModel):
    """Request for narrative generation from Purple Agent.

    TODO(review): Added default template_type for graceful degradation.
    Rationale: If A2A request omits template_type, use sensible default
    instead of failing. Aligns with Purple Agent's default behavior.
    """

    template_type: str = "qualifying"  # Default: most common use case
    signals: dict[str, Any] | None = None
    context: str | None = None


class NarrativeResponse(BaseModel):
    """Response containing generated narrative from Purple Agent."""

    narrative: str
    metadata: dict[str, Any] | None = None
    task_id: str | None = None


def _get_llm_alpha() -> float:
    from bulletproof_green.settings import settings

    return settings.llm_alpha


def _get_llm_beta() -> float:
    from bulletproof_green.settings import settings

    return settings.llm_beta


def _get_llm_temperature() -> float:
    from bulletproof_green.settings import settings

    return settings.llm.temperature


def _get_llm_model() -> str:
    from bulletproof_green.settings import settings

    return settings.llm.model


def _get_llm_timeout() -> float:
    from bulletproof_green.settings import settings

    return settings.llm.timeout


class LLMJudgeConfig(BaseModel):
    """Configuration for LLM-as-Judge evaluation.

    Defaults are loaded from settings.
    """

    alpha: float = Field(default_factory=_get_llm_alpha)
    beta: float = Field(default_factory=_get_llm_beta)
    temperature: float = Field(default_factory=_get_llm_temperature)
    model: str = Field(default_factory=_get_llm_model)
    timeout: float = Field(default_factory=_get_llm_timeout)


class LLMScoreResult(BaseModel):
    """Result from LLM evaluation.

    Defaults are provided for graceful degradation when LLM returns incomplete responses.
    """

    score: float = 0.5
    reasoning: str = ""
    categories: dict[str, float] = Field(default_factory=dict)


class HybridScoreResult(BaseModel):
    """Result from hybrid (rule + LLM) evaluation."""

    final_score: float
    rule_score: float
    llm_score: float | None
    alpha: float
    beta: float
    fallback_used: bool
    llm_reasoning: str | None = None


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
    # Optional metadata for debugging and compliance
    metadata: dict[str, Any] | None = None
