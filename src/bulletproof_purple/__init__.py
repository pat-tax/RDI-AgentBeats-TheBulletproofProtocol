"""Purple Agent - IRS Section 41 narrative generator."""

from bulletproof_purple import agent_card
from bulletproof_purple.agent_card import (
    AGENT_CARD_SCHEMA,
    create_agent_card,
    validate_agent_card,
)
from bulletproof_purple.generator import NarrativeGenerator
from bulletproof_purple.models import Narrative

__all__ = [
    "NarrativeGenerator",
    "Narrative",
    "agent_card",
    "create_agent_card",
    "validate_agent_card",
    "AGENT_CARD_SCHEMA",
]
