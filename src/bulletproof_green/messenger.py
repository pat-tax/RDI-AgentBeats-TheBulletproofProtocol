"""A2A messaging utilities for Green Agent to Purple Agent communication.

This module provides simple utilities for constructing and sending A2A protocol messages:
- create_message(): Construct A2A-compliant message structures
- send_message(): Send HTTP POST requests to purple agents via A2A protocol
- Messenger: High-level class for agent-to-agent communication
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx

DEFAULT_TIMEOUT = 300


class MessengerError(Exception):
    """Exception raised for messenger errors."""


def create_message(
    text: str | None = None,
    data: dict[str, Any] | None = None,
    role: str = "user",
) -> dict[str, Any]:
    """Create an A2A-compliant message structure.

    Args:
        text: Optional text content for the message
        data: Optional data payload for the message
        role: Message role (default: "user")

    Returns:
        A2A message dictionary with messageId, role, and parts

    Examples:
        >>> msg = create_message(text="Generate a narrative")
        >>> msg = create_message(data={"template_type": "qualifying"})
        >>> msg = create_message(text="Context", data={"template_type": "qualifying"})
    """
    parts: list[dict[str, Any]] = []

    # Add text part if provided
    if text is not None:
        parts.append({"text": text})

    # Add data part if provided
    if data is not None:
        parts.append({"data": data})

    return {
        "messageId": str(uuid.uuid4()),
        "role": role,
        "parts": parts,
    }


async def send_message(
    url: str,
    message: dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Send an A2A message via HTTP POST to a purple agent.

    Args:
        url: Base URL of the purple agent
        message: A2A message structure (from create_message)
        timeout: Request timeout in seconds (default: 300)

    Returns:
        Response data extracted from JSON-RPC result

    Raises:
        MessengerError: If the request fails or response is invalid

    Examples:
        >>> msg = create_message(text="Generate narrative")
        >>> response = await send_message("http://localhost:8001", msg)
        >>> narrative = response["narrative"]
    """
    # Build JSON-RPC 2.0 request
    request_body = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": str(uuid.uuid4()),
        "params": {"message": message},
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                json=request_body,
                headers={"Content-Type": "application/json"},
            )
            response_data = response.json()

            # Check for JSON-RPC error
            if "error" in response_data:
                error = response_data["error"]
                raise MessengerError(f"JSON-RPC error: {error.get('message', 'Unknown error')}")

            # Extract result
            result = response_data.get("result", {})

            # Extract narrative from parts
            return _extract_data_from_result(result)

    except httpx.TimeoutException as e:
        raise MessengerError(f"Timeout sending message: {e}") from e
    except httpx.ConnectError as e:
        raise MessengerError(f"Connection error: {e}") from e
    except Exception as e:
        if isinstance(e, MessengerError):
            raise
        raise MessengerError(f"Error sending message: {e}") from e


def _extract_data_from_result(result: dict[str, Any]) -> dict[str, Any]:
    """Extract data from JSON-RPC result.

    Args:
        result: The result dictionary from JSON-RPC response

    Returns:
        Data dictionary extracted from parts

    Raises:
        MessengerError: If data cannot be extracted
    """
    parts = result.get("parts", [])

    for part in parts:
        if "data" in part:
            return part["data"]

    raise MessengerError("No data found in response")


class Messenger:
    """High-level API for agent-to-agent communication.

    Provides a simple interface for sending messages to purple agents,
    combining create_message and send_message functionality.

    Attributes:
        base_url: Base URL of the purple agent
        timeout: Request timeout in seconds

    Examples:
        >>> messenger = Messenger(base_url="http://localhost:8001")
        >>> response = await messenger.send(text="Generate narrative")
        >>> narrative = response["narrative"]
    """

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the messenger.

        Args:
            base_url: Base URL of the purple agent
            timeout: Request timeout in seconds (default: 300)
        """
        self.base_url = base_url
        self.timeout = timeout

    async def send(
        self,
        text: str | None = None,
        data: dict[str, Any] | None = None,
        role: str = "user",
    ) -> dict[str, Any]:
        """Send a message to the purple agent.

        Args:
            text: Optional text content for the message
            data: Optional data payload for the message
            role: Message role (default: "user")

        Returns:
            Response data from the purple agent

        Raises:
            MessengerError: If the request fails

        Examples:
            >>> messenger = Messenger(base_url="http://localhost:8001")
            >>> response = await messenger.send(text="Generate narrative")
            >>> response = await messenger.send(
            ...     text="Context", data={"template_type": "qualifying"}
            ... )
        """
        message = create_message(text=text, data=data, role=role)
        return await send_message(self.base_url, message, timeout=self.timeout)
