"""Purple Agent A2A server for IRS Section 41 narrative generation.

Exposes narrative generation via JSON-RPC 2.0 protocol following A2A specification.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    DataPart,
    Message,
    MessageSendParams,
    Part,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)
from a2a.utils import new_agent_parts_message, new_task

from bulletproof_purple.generator import NarrativeGenerator

if TYPE_CHECKING:
    from a2a.server.context import ServerCallContext

DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 300


def get_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Create the AgentCard for Purple Agent.

    Args:
        base_url: Base URL where the agent is hosted.

    Returns:
        Configured AgentCard with narrative generation capability.
    """
    # Note: a2a-sdk uses camelCase for pydantic model field aliases but pyright
    # doesn't recognize them, hence the type: ignore comments
    return AgentCard(
        name="Bulletproof Purple Agent",
        description="IRS Section 41 R&D tax credit narrative generator. "
        "Generates Four-Part Test compliant narratives from engineering signals.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,  # type: ignore[call-arg]
        ),
        defaultInputModes=["text"],  # type: ignore[call-arg]
        defaultOutputModes=["text", "data"],  # type: ignore[call-arg]
        skills=[
            AgentSkill(
                id="generate_narrative",
                name="Generate Narrative",
                description="Generate IRS Section 41 compliant Four-Part Test narrative "
                "from engineering project signals.",
                tags=["irs", "r&d", "tax-credit", "narrative"],
                examples=[
                    "Generate a qualifying R&D narrative",
                    "Create a Four-Part Test narrative for my project",
                ],
            )
        ],
    )


class PurpleAgentExecutor:
    """Executor that generates narratives using the NarrativeGenerator."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.generator = NarrativeGenerator()
        self.timeout = timeout

    def _extract_text_from_part(self, part: Any) -> str | None:
        """Extract text content from a message part.

        Args:
            part: A message part (TextPart, DataPart, FilePart, or Part).

        Returns:
            The text content if available, None otherwise.
        """
        # Handle Part wrapper
        part_data = part.root if hasattr(part, "root") else part

        # Check for TextPart
        if isinstance(part_data, TextPart):
            return part_data.text
        if hasattr(part_data, "text") and isinstance(part_data.text, str):
            return part_data.text
        return None

    def _extract_data_from_part(self, part: Any) -> dict[str, Any] | None:
        """Extract data content from a message part.

        Args:
            part: A message part (TextPart, DataPart, FilePart, or Part).

        Returns:
            The data dict if available, None otherwise.
        """
        # Handle Part wrapper
        part_data = part.root if hasattr(part, "root") else part

        # Check for DataPart
        if isinstance(part_data, DataPart) and isinstance(part_data.data, dict):  # type: ignore[reportUnnecessaryIsInstance]
            return part_data.data
        if hasattr(part_data, "data") and isinstance(part_data.data, dict):
            return part_data.data
        return None

    def _infer_template_from_text(self, text: str) -> str | None:
        """Infer template type from text content.

        Args:
            text: Text content to analyze.

        Returns:
            Template type string or None if not determinable.
        """
        text_lower = text.lower()
        if "non-qualifying" in text_lower or "non_qualifying" in text_lower:
            return "non_qualifying"
        if "edge" in text_lower:
            return "edge_case"
        return None

    def _parse_request(self, params: MessageSendParams) -> tuple[str, dict[str, Any] | None]:
        """Parse template type and signals from message params.

        Args:
            params: Message parameters from the request.

        Returns:
            Tuple of (template_type, signals).
        """
        template_type = "qualifying"
        signals: dict[str, Any] | None = None

        if not (params.message and params.message.parts):
            return template_type, signals

        for part in params.message.parts:
            text = self._extract_text_from_part(part)
            if text and (inferred := self._infer_template_from_text(text)):
                template_type = inferred

            data = self._extract_data_from_part(part)
            if data:
                template_type = data.get("template_type", template_type)
                signals = data.get("signals", signals)

        return template_type, signals

    async def execute(
        self, params: MessageSendParams, task: Task
    ) -> AsyncGenerator[Message | Task]:
        """Execute narrative generation for incoming message.

        Args:
            params: Message parameters from the request.
            task: The task being executed.

        Yields:
            Task updates and final Message with generated narrative.
        """
        template_type, signals = self._parse_request(params)

        # Update task to working
        task.status = TaskStatus(state=TaskState.working)
        yield task

        # Generate narrative with timeout
        try:
            narrative = await asyncio.wait_for(
                asyncio.to_thread(self.generator.generate, template_type, signals),
                timeout=self.timeout,
            )

            # Create response with DataPart
            data_part = DataPart(
                data={
                    "narrative": narrative.text,
                    "metadata": narrative.metadata,
                }
            )

            # Mark task completed
            task.status = TaskStatus(state=TaskState.completed)
            yield task

            # Return message with narrative
            yield new_agent_parts_message(parts=[Part(root=data_part)])

        except TimeoutError:
            task.status = TaskStatus(state=TaskState.failed)
            yield task


class PurpleRequestHandler(DefaultRequestHandler):
    """Request handler for Purple Agent A2A server."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.task_store = InMemoryTaskStore()
        self.executor = PurpleAgentExecutor(timeout=timeout)
        super().__init__(
            agent_executor=self.executor,  # type: ignore[arg-type]
            task_store=self.task_store,
        )

    async def on_message_send(
        self, params: MessageSendParams, context: ServerCallContext | None = None
    ) -> Message | Task:
        """Handle message/send requests.

        Args:
            params: Message send parameters.
            context: Optional server call context.

        Returns:
            Message with generated narrative or Task status.
        """
        # Create a new task from the incoming message
        task = new_task(params.message)

        # Store the task
        await self.task_store.save(task)

        # Execute and collect final result
        final_result: Message | Task = task
        async for event in self.executor.execute(params, task):
            if isinstance(event, Task):
                await self.task_store.save(event)
                final_result = event
            else:
                final_result = event

        return final_result


def create_app(timeout: int = DEFAULT_TIMEOUT) -> Any:
    """Create the A2A FastAPI application.

    Args:
        timeout: Task timeout in seconds (default 300).

    Returns:
        Configured FastAPI application.
    """
    agent_card = get_agent_card()
    handler = PurpleRequestHandler(timeout=timeout)

    a2a_app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    return a2a_app.build()


def main() -> None:
    """Run the Purple Agent A2A server."""
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
