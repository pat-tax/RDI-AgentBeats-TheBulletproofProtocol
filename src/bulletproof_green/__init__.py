"""Green Agent - IRS Section 41 narrative evaluator."""

from bulletproof_green import a2a_client
from bulletproof_green.a2a_client import (
    A2AClient,
    A2AClientError,
    NarrativeRequest,
    NarrativeResponse,
)
from bulletproof_green.evaluator import EvaluationResult, Issue, Redline, RuleBasedEvaluator
from bulletproof_green.scorer import AgentBeatsScorer, ScoreResult

__all__ = [
    "RuleBasedEvaluator",
    "EvaluationResult",
    "Issue",
    "Redline",
    "AgentBeatsScorer",
    "ScoreResult",
    "A2AClient",
    "A2AClientError",
    "NarrativeRequest",
    "NarrativeResponse",
    "a2a_client",
]
