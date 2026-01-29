"""Green Agent domain logic - "What the agent does"

This module defines:
- AgentCard definition (agent metadata and capabilities)
- GreenAgent class (core evaluation logic)
- Domain models (if any)

Pattern: agent.py = Domain implementation, separated from protocol (executor.py)
         and transport (server.py)
"""

from __future__ import annotations

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from bulletproof_green.settings import settings


def get_agent_card(base_url: str | None = None) -> AgentCard:
    """Create the AgentCard for Green Agent.

    Args:
        base_url: Base URL where the agent is hosted. If None, uses
                 GREEN_AGENT_CARD_URL env var or falls back to
                 http://{host}:{port} from settings.

    Returns:
        Configured AgentCard with narrative evaluation capability.
    """
    if base_url is None:
        # Use env var if set, otherwise construct from host:port
        if settings.agent_card_url:
            base_url = settings.agent_card_url
        else:
            base_url = f"http://{settings.host}:{settings.port}"

    return AgentCard(
        name="Bulletproof Green Agent",
        description="IRS Section 41 R&D tax credit narrative evaluator. "
        "Evaluates Four-Part Test narratives against IRS audit standards.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,  # type: ignore[call-arg]
        ),
        defaultInputModes=["text", "data"],  # type: ignore[call-arg]
        defaultOutputModes=["data"],  # type: ignore[call-arg]
        skills=[
            AgentSkill(
                id="evaluate_narrative",
                name="Evaluate Narrative",
                description="Evaluate IRS Section 41 R&D tax credit narrative "
                "against audit standards and return compliance scores.",
                tags=["irs", "r&d", "tax-credit", "evaluation", "scoring"],
                examples=[
                    "Evaluate this R&D narrative for IRS compliance",
                    "Score my Four-Part Test documentation",
                ],
            )
        ],
    )


# TODO: Create GreenAgent class following debate_judge pattern
# class GreenAgent:
#     """IRS Section 41 narrative evaluation agent - domain logic only."""
#
#     def __init__(self):
#         self.evaluator = RuleBasedEvaluator()
#         self.scorer = AgentBeatsScorer()
#         self.llm_judge = LLMJudge()
#
#     def run(self, params: MessageSendParams) -> GreenAgentOutput:
#         """Main entry point - evaluates narrative."""
#         pass
