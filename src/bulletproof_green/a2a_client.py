"""A2A client for inter-agent communication with Purple Agent.

Enables Green Agent to call Purple Agent for narrative generation via A2A protocol.
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from bulletproof_green.evals.models import NarrativeRequest, NarrativeResponse
from bulletproof_green.settings import settings


class A2AClientError(Exception):
    """Exception raised for A2A client errors."""


class A2AClient:
    """A2A client for communicating with Purple Agent.

    Provides methods for discovering the agent and sending narrative requests
    via JSON-RPC 2.0 protocol.

    Attributes:
        base_url: Base URL of the Purple Agent.
        timeout: Request timeout in seconds.
    """

    def __init__(self, base_url: str, timeout: int | None = None):
        """Initialize the A2A client.

        Args:
            base_url: Base URL of the Purple Agent (e.g., "http://localhost:8001").
            timeout: Request timeout in seconds (uses settings if not provided).
        """
        self.base_url = base_url
        self.timeout = timeout if timeout is not None else settings.timeout
        self._agent_card: dict[str, Any] | None = None

    async def discover(self) -> dict[str, Any]:
        """Discover Purple Agent via agent-card.json.

        Fetches the AgentCard from the well-known endpoint and caches it.

        Returns:
            The agent card as a dictionary.

        Raises:
            A2AClientError: If discovery fails.
        """
        if self._agent_card is not None:
            return self._agent_card

        self._agent_card = await self._fetch_agent_card()
        return self._agent_card

    async def _fetch_agent_card(self) -> dict[str, Any]:
        """Fetch agent card from well-known endpoint.

        Returns:
            The agent card as a dictionary.

        Raises:
            A2AClientError: If fetch fails.
        """
        url = f"{self.base_url}/.well-known/agent-card.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            raise A2AClientError(f"Timeout fetching agent card: {e}") from e
        except httpx.ConnectError as e:
            raise A2AClientError(f"Connection error fetching agent card: {e}") from e
        except httpx.HTTPStatusError as e:
            raise A2AClientError(f"HTTP error fetching agent card: {e}") from e
        except Exception as e:
            raise A2AClientError(f"Error fetching agent card: {e}") from e

    async def send_request(self, request: NarrativeRequest) -> NarrativeResponse:
        """Send a narrative request to Purple Agent.

        Args:
            request: The narrative request to send.

        Returns:
            NarrativeResponse containing the generated narrative.

        Raises:
            A2AClientError: If the request fails.
        """
        # Build message parts
        parts: list[dict[str, Any]] = []

        # Add context as text if provided
        if request.context:
            parts.append({"text": request.context})

        # Add data part with template_type and signals
        data: dict[str, Any] = {"template_type": request.template_type}
        if request.signals:
            data["signals"] = request.signals
        parts.append({"data": data})

        # Build message/send params
        params = {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": parts,
            }
        }

        try:
            response = await self._send_jsonrpc("message/send", params)
        except TimeoutError as e:
            raise A2AClientError(f"Timeout sending request: {e}") from e
        except ConnectionError as e:
            raise A2AClientError(f"Connection error: {e}") from e

        return await self._parse_response(response)

    async def _send_jsonrpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC 2.0 request.

        Args:
            method: The JSON-RPC method name.
            params: The method parameters.

        Returns:
            The JSON-RPC response.

        Raises:
            A2AClientError: If the request fails.
        """
        request_body = {
            "jsonrpc": "2.0",
            "method": method,
            "id": str(uuid.uuid4()),
            "params": params,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    json=request_body,
                    headers={"Content-Type": "application/json"},
                )
                return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError(str(e)) from e
        except httpx.ConnectError as e:
            raise ConnectionError(str(e)) from e

    async def _parse_response(self, response: dict[str, Any]) -> NarrativeResponse:
        """Parse JSON-RPC response into NarrativeResponse.

        Args:
            response: The JSON-RPC response.

        Returns:
            NarrativeResponse containing the generated narrative.

        Raises:
            A2AClientError: If parsing fails or response indicates error.
        """
        # Check for JSON-RPC error
        if "error" in response:
            error = response["error"]
            raise A2AClientError(f"JSON-RPC error: {error.get('message', 'Unknown error')}")

        result = response.get("result", {})

        # Check for task failure
        if "status" in result:
            state = result["status"].get("state", "")
            if state == "failed":
                raise A2AClientError("Task failed")
            # If task is still working, poll for completion
            if state == "working":
                task_id = result.get("id")
                if task_id:
                    poll_result = await self._poll_task(task_id)
                    return self._extract_narrative_from_result(poll_result)
                raise A2AClientError("Task is working but no task ID provided")

        # Extract narrative from parts
        return self._extract_narrative_from_result(result)

    async def _poll_task(self, task_id: str) -> dict[str, Any]:
        """Poll for task completion.

        Args:
            task_id: The task ID to poll.

        Returns:
            The completed task result.

        Raises:
            A2AClientError: If polling fails.
        """
        # This method exists primarily for mocking in tests
        # In a real implementation, this would poll the task/get endpoint
        raise NotImplementedError("Task polling not implemented")

    def _extract_narrative_from_result(self, result: dict[str, Any]) -> NarrativeResponse:
        """Extract narrative from response result.

        Args:
            result: The result dictionary from JSON-RPC response.

        Returns:
            NarrativeResponse with extracted narrative.

        Raises:
            A2AClientError: If narrative cannot be extracted.
        """
        parts = result.get("parts", [])

        for part in parts:
            if "data" in part:
                data = part["data"]
                narrative = data.get("narrative")
                if narrative:
                    # Validate response from A2A protocol
                    response_data = {
                        "narrative": narrative,
                        "metadata": data.get("metadata"),
                        "task_id": result.get("id"),
                    }
                    return NarrativeResponse.model_validate(response_data)

        raise A2AClientError("No narrative found in response")
