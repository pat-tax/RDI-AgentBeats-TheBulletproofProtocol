"""Green Agent - IRS Section 41 narrative evaluator."""

from bulletproof_green import a2a_client, agent_card, arena_executor
from bulletproof_green.a2a_client import (
    A2AClient,
    A2AClientError,
    NarrativeRequest,
    NarrativeResponse,
)
from bulletproof_green.agent_card import (
    AGENT_CARD_SCHEMA,
    AgentCardCache,
    AgentCardDiscoveryError,
    AgentCardValidationError,
    create_agent_card,
    discover_agent,
    validate_agent_card,
)
from bulletproof_green.arena_executor import (
    ArenaConfig,
    ArenaExecutor,
    ArenaResult,
    IterationRecord,
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
    "agent_card",
    "arena_executor",
    "ArenaExecutor",
    "ArenaConfig",
    "ArenaResult",
    "IterationRecord",
    "create_agent_card",
    "validate_agent_card",
    "discover_agent",
    "AgentCardCache",
    "AgentCardDiscoveryError",
    "AgentCardValidationError",
    "AGENT_CARD_SCHEMA",
]
