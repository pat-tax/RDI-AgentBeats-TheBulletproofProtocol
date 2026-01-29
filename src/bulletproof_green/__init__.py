"""Green Agent - IRS Section 41 narrative evaluator."""

from bulletproof_green import a2a_client, agent_card, arena_executor, evals, executor, messenger
from bulletproof_green.a2a_client import A2AClient, A2AClientError
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
from bulletproof_green.evals import (
    AgentBeatsScorer,
    EvaluationResult,
    HybridScoreResult,
    Issue,
    LLMJudge,
    LLMJudgeConfig,
    LLMScoreResult,
    NarrativeRequest,
    NarrativeResponse,
    Redline,
    RuleBasedEvaluator,
    ScoreResult,
)
from bulletproof_green.executor import GreenAgentExecutor
from bulletproof_green.messenger import Messenger, MessengerError, create_message, send_message

__all__ = [
    # Evaluation domain
    "RuleBasedEvaluator",
    "AgentBeatsScorer",
    "LLMJudge",
    "EvaluationResult",
    "ScoreResult",
    "Issue",
    "Redline",
    "NarrativeRequest",
    "NarrativeResponse",
    "LLMJudgeConfig",
    "LLMScoreResult",
    "HybridScoreResult",
    "evals",
    # A2A protocol
    "A2AClient",
    "A2AClientError",
    "a2a_client",
    "agent_card",
    "Messenger",
    "MessengerError",
    "create_message",
    "send_message",
    "messenger",
    "create_agent_card",
    "validate_agent_card",
    "discover_agent",
    "AgentCardCache",
    "AgentCardDiscoveryError",
    "AgentCardValidationError",
    "AGENT_CARD_SCHEMA",
    # Arena mode
    "ArenaExecutor",
    "ArenaConfig",
    "ArenaResult",
    "IterationRecord",
    "arena_executor",
    # Execution
    "GreenAgentExecutor",
    "executor",
]
