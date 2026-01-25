"""AgentCard module for Purple Agent.

Provides AgentCard creation and JSON schema validation for A2A protocol.
"""

from __future__ import annotations

from typing import Any

# JSON Schema for A2A AgentCard validation
AGENT_CARD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["name", "url", "version"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "url": {"type": "string"},
        "version": {"type": "string"},
        "capabilities": {"type": "object"},
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "description"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "examples": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "defaultInputModes": {"type": "array", "items": {"type": "string"}},
        "defaultOutputModes": {"type": "array", "items": {"type": "string"}},
    },
}


def create_agent_card(base_url: str = "http://localhost:8000") -> dict[str, Any]:
    """Create the AgentCard for Purple Agent.

    Args:
        base_url: Base URL where the agent is hosted.

    Returns:
        AgentCard as a dictionary with capabilities, endpoints, and name.
    """
    return {
        "name": "Bulletproof Purple Agent",
        "description": "IRS Section 41 R&D tax credit narrative generator. "
        "Generates Four-Part Test compliant narratives from engineering signals.",
        "url": base_url,
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text", "data"],
        "skills": [
            {
                "id": "generate_narrative",
                "name": "Generate Narrative",
                "description": "Generate IRS Section 41 compliant Four-Part Test narrative "
                "from engineering project signals.",
                "tags": ["irs", "r&d", "tax-credit", "narrative"],
                "examples": [
                    "Generate a qualifying R&D narrative",
                    "Create a Four-Part Test narrative for my project",
                ],
            }
        ],
    }


def validate_agent_card(card: dict[str, Any]) -> bool:
    """Validate an AgentCard against the JSON schema.

    Args:
        card: AgentCard dictionary to validate.

    Returns:
        True if valid, False otherwise.
    """
    # Check required fields
    for field in AGENT_CARD_SCHEMA["required"]:
        if field not in card:
            return False

    # Check capabilities type if present
    if "capabilities" in card and not isinstance(card["capabilities"], dict):
        return False

    # Check skills type if present
    if "skills" in card and not isinstance(card["skills"], list):
        return False

    # Validate each skill has required fields
    if "skills" in card:
        for skill in card["skills"]:
            if not isinstance(skill, dict):
                return False
            for field in ["id", "name", "description"]:
                if field not in skill:
                    return False

    return True
