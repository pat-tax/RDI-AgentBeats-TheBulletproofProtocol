"""Green Agent - IRS Section 41 narrative evaluator."""

from bulletproof_green import (
    agent,
    arena,
    evals,
    executor,
    messenger,
    models,
)
from bulletproof_green.agent import get_agent_card
from bulletproof_green.arena import (
    ArenaConfig,
    ArenaExecutor,
    ArenaResult,
    IterationRecord,
)
from bulletproof_green.evals import (
    AgentBeatsScorer,
    EvaluationResult,
    GreenAgentOutput,
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
    "evals",
    # Models
    "EvaluationResult",
    "ScoreResult",
    "Issue",
    "Redline",
    "NarrativeRequest",
    "NarrativeResponse",
    "LLMJudgeConfig",
    "LLMScoreResult",
    "HybridScoreResult",
    "GreenAgentOutput",
    "models",
    # Messaging
    "Messenger",
    "MessengerError",
    "create_message",
    "send_message",
    "messenger",
    # Arena mode
    "ArenaExecutor",
    "ArenaConfig",
    "ArenaResult",
    "IterationRecord",
    "arena",
    # Execution
    "GreenAgentExecutor",
    "executor",
    # Agent
    "get_agent_card",
    "agent",
]
