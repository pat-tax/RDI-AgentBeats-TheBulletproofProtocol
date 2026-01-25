"""AgentCard module for Green Agent.

Provides AgentCard creation, JSON schema validation, discovery, and caching for A2A protocol.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

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

DEFAULT_TIMEOUT = 30
DEFAULT_CACHE_TTL = 300  # 5 minutes


class AgentCardDiscoveryError(Exception):
    """Exception raised when agent discovery fails."""


class AgentCardValidationError(Exception):
    """Exception raised when AgentCard validation fails."""


class AgentCardCache:
    """Cache for storing discovered AgentCards with TTL.

    Attributes:
        ttl_seconds: Time-to-live for cached entries in seconds.
    """

    def __init__(self, ttl_seconds: int = DEFAULT_CACHE_TTL):
        """Initialize the cache.

        Args:
            ttl_seconds: Time-to-live for cached entries (default 300 seconds).
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}

    def get(self, url: str) -> dict[str, Any] | None:
        """Get cached AgentCard for a URL.

        Args:
            url: Base URL of the agent.

        Returns:
            Cached AgentCard if valid and not expired, None otherwise.
        """
        if url not in self._cache:
            return None

        card, timestamp = self._cache[url]
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[url]
            return None

        return card

    def set(self, url: str, card: dict[str, Any]) -> None:
        """Cache an AgentCard for a URL.

        Args:
            url: Base URL of the agent.
            card: AgentCard to cache.
        """
        self._cache[url] = (card, time.time())

    def invalidate(self, url: str) -> None:
        """Invalidate cached entry for a URL.

        Args:
            url: Base URL to invalidate.
        """
        if url in self._cache:
            del self._cache[url]

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


def create_agent_card(base_url: str = "http://localhost:8000") -> dict[str, Any]:
    """Create the AgentCard for Green Agent.

    Args:
        base_url: Base URL where the agent is hosted.

    Returns:
        AgentCard as a dictionary with capabilities, endpoints, and name.
    """
    return {
        "name": "Bulletproof Green Agent",
        "description": "IRS Section 41 R&D tax credit narrative evaluator. "
        "Evaluates Four-Part Test narratives against IRS audit standards.",
        "url": base_url,
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "defaultInputModes": ["text", "data"],
        "defaultOutputModes": ["data"],
        "skills": [
            {
                "id": "evaluate_narrative",
                "name": "Evaluate Narrative",
                "description": "Evaluate IRS Section 41 R&D tax credit narrative "
                "against audit standards and return compliance scores.",
                "tags": ["irs", "r&d", "tax-credit", "evaluation", "scoring"],
                "examples": [
                    "Evaluate this R&D narrative for IRS compliance",
                    "Score my Four-Part Test documentation",
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


async def discover_agent(
    base_url: str,
    timeout: int = DEFAULT_TIMEOUT,
    cache: AgentCardCache | None = None,
) -> dict[str, Any]:
    """Discover an agent via its /.well-known/agent-card.json endpoint.

    Args:
        base_url: Base URL of the agent to discover.
        timeout: Request timeout in seconds.
        cache: Optional cache instance for caching discovered cards.

    Returns:
        The discovered AgentCard as a dictionary.

    Raises:
        AgentCardDiscoveryError: If discovery fails due to network issues.
        AgentCardValidationError: If the returned AgentCard is invalid.
    """
    # Check cache first
    if cache is not None:
        cached = cache.get(base_url)
        if cached is not None:
            return cached

    url = f"{base_url}/.well-known/agent-card.json"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            card = response.json()
    except httpx.TimeoutException as e:
        raise AgentCardDiscoveryError(f"Timeout discovering agent at {url}: {e}") from e
    except httpx.ConnectError as e:
        raise AgentCardDiscoveryError(f"Connection error discovering agent at {url}: {e}") from e
    except httpx.HTTPStatusError as e:
        raise AgentCardDiscoveryError(f"HTTP error discovering agent at {url}: {e}") from e
    except Exception as e:
        raise AgentCardDiscoveryError(f"Error discovering agent at {url}: {e}") from e

    # Validate the discovered card
    if not validate_agent_card(card):
        raise AgentCardValidationError(f"Invalid AgentCard from {url}")

    # Cache the result
    if cache is not None:
        cache.set(base_url, card)

    return card
