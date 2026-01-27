"""Green Agent - IRS Section 41 narrative evaluator."""

from bulletproof_green import a2a_client, agent_card, arena_executor, llm_judge
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
from bulletproof_green.evaluator import RuleBasedEvaluator
from bulletproof_green.llm_judge import LLMJudge
from bulletproof_green.models import (
    EvaluationResult,
    HybridScoreResult,
    Issue,
    LLMJudgeConfig,
    LLMScoreResult,
    NarrativeRequest,
    NarrativeResponse,
    Redline,
    ScoreResult,
)
from bulletproof_green.scorer import AgentBeatsScorer

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
    "llm_judge",
    "ArenaExecutor",
    "ArenaConfig",
    "ArenaResult",
    "IterationRecord",
    "LLMJudge",
    "LLMJudgeConfig",
    "LLMScoreResult",
    "HybridScoreResult",
    "create_agent_card",
    "validate_agent_card",
    "discover_agent",
    "AgentCardCache",
    "AgentCardDiscoveryError",
    "AgentCardValidationError",
    "AGENT_CARD_SCHEMA",
]
