"""Green Agent messenger - A2A SDK client integration (communication layer).

Responsibilities:
- A2A messaging via a2a-sdk ClientFactory.connect() pattern
- Inter-agent communication (Green -> Purple, Purple -> Green)
- Per-URL client caching with lifecycle management

Pattern: messenger.py = Communication utilities, used by arena/executor.py
         for A2A protocol messaging
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx
from a2a.client import (
    A2AClientHTTPError,
    A2AClientTimeoutError,
    Client,
    ClientConfig,
    ClientFactory,
)
from a2a.types import (
    DataPart,
    Message,
    Part,
    Role,
    Task,
    TaskState,
    TextPart,
)

from bulletproof_green.settings import settings


class MessengerError(Exception):
    """Exception raised for messenger errors."""


async def send_message(
    url: str,
    message: dict[str, Any],
    timeout: int | None = None,
) -> dict[str, Any]:
    """Send an A2A message to an agent (backward-compatible free function).

    FIXME: Creates+closes a Messenger per call (no client reuse). If called
    in a loop, callers should use Messenger class directly instead.

    Wraps Messenger internally for SDK client usage while preserving the
    original call signature.

    Args:
        url: Base URL of the target agent
        message: A2A message structure (from create_message)
        timeout: Request timeout in seconds (uses settings if not provided)

    Returns:
        Response data extracted from task artifacts

    Raises:
        MessengerError: If the request fails or response is invalid
    """
    messenger = Messenger(base_url=url, timeout=timeout)
    try:
        # Extract text/data from the raw dict to rebuild as SDK Message
        text = None
        data = None
        for part in message.get("parts", []):
            if "text" in part:
                text = part["text"]
            elif "data" in part:
                data = part["data"]
        return await messenger.send(text=text, data=data)
    finally:
        await messenger.close()


def _build_sdk_message(
    text: str | None = None,
    data: dict[str, Any] | None = None,
    role: Role = Role.user,
) -> Message:
    """Build an a2a-sdk Message with TextPart/DataPart support."""
    parts: list[Part] = []

    if text is not None:
        parts.append(Part(root=TextPart(text=text)))

    if data is not None:
        parts.append(Part(root=DataPart(data=data)))

    return Message(
        role=role,
        message_id=str(uuid.uuid4()),
        parts=parts,
    )


def _extract_data_from_task(task: Task) -> dict[str, Any]:
    """Extract response data from a completed Task's artifacts.

    Returns:
        dict extracted from the first DataPart, or {"text": ...} from TextPart.

    Raises:
        MessengerError: If no artifacts or no extractable parts found.
    """
    if not task.artifacts:
        raise MessengerError("No artifacts in completed task")

    for artifact in task.artifacts:
        for part in artifact.parts:
            if isinstance(part.root, DataPart):
                return part.root.data
            if isinstance(part.root, TextPart):
                return {"text": part.root.text}

    raise MessengerError("No data found in task artifacts")


class Messenger:
    """High-level API for agent-to-agent communication via a2a-sdk.

    Uses ClientFactory.connect() with per-URL client caching.

    Attributes:
        base_url: Base URL of the target agent
        timeout: Request timeout in seconds
    """

    def __init__(self, base_url: str, timeout: int | None = None):
        self.base_url = base_url
        self.timeout = timeout if timeout is not None else settings.timeout
        self._clients: dict[str, Client] = {}
        self._httpx_clients: dict[str, httpx.AsyncClient] = {}

    async def _get_client(self, url: str) -> Client:
        """Get or create a cached SDK Client for the given URL."""
        if url not in self._clients:
            httpx_client = httpx.AsyncClient(timeout=self.timeout)
            self._httpx_clients[url] = httpx_client

            config = ClientConfig(
                streaming=False,
                httpx_client=httpx_client,
            )
            self._clients[url] = await ClientFactory.connect(
                url, client_config=config
            )
        return self._clients[url]

    async def send(
        self,
        text: str | None = None,
        data: dict[str, Any] | None = None,
        role: str = "user",
    ) -> dict[str, Any]:
        """Send a message to the target agent via a2a-sdk.

        Args:
            text: Optional text content for the message
            data: Optional data payload for the message
            role: Message role (default: "user")

        Returns:
            Response data dict from the agent

        Raises:
            MessengerError: If the request fails
        """
        try:
            client = await self._get_client(self.base_url)
            sdk_role = Role.user if role == "user" else Role.agent
            message = _build_sdk_message(text=text, data=data, role=sdk_role)

            async for event in client.send_message(message):
                # Events are (Task, UpdateEvent | None) tuples or Message
                if isinstance(event, Message):
                    continue

                task, _update_event = event

                if task.status.state == TaskState.failed:
                    msg = task.status.message or "Task failed"
                    raise MessengerError(f"Task failed: {msg}")

                if task.status.state == TaskState.completed:
                    return _extract_data_from_task(task)

            raise MessengerError("No completed task received")

        except MessengerError:
            raise
        except A2AClientTimeoutError as e:
            raise MessengerError(f"Timeout: {e}") from e
        except A2AClientHTTPError as e:
            raise MessengerError(f"HTTP error {e.status_code}: {e}") from e
        except httpx.ConnectError as e:
            raise MessengerError(f"Connection error: {e}") from e
        except Exception as e:
            raise MessengerError(f"Error sending message: {e}") from e

    async def close(self) -> None:
        """Close managed httpx clients and clear caches."""
        for httpx_client in self._httpx_clients.values():
            await httpx_client.aclose()
        self._httpx_clients.clear()
        self._clients.clear()
