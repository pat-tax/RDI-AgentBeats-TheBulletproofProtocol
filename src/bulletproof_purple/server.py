"""Purple Agent A2A server for IRS Section 41 narrative generation.

Exposes narrative generation via JSON-RPC 2.0 protocol following A2A specification.
"""

import asyncio
from collections.abc import AsyncGenerator

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
)
from a2a.utils import new_agent_parts_message, new_task

from bulletproof_purple.generator import NarrativeGenerator

DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 300


def get_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Create the AgentCard for Purple Agent.

    Args:
        base_url: Base URL where the agent is hosted.

    Returns:
        Configured AgentCard with narrative generation capability.
    """
    return AgentCard(
        name="Bulletproof Purple Agent",
        description="IRS Section 41 R&D tax credit narrative generator. "
        "Generates Four-Part Test compliant narratives from engineering signals.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
        defaultInputModes=["text"],
        defaultOutputModes=["text", "data"],
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
        # Extract request from message parts
        template_type = "qualifying"
        signals: dict | None = None

        if params.message and params.message.parts:
            for part in params.message.parts:
                part_data = part.root if hasattr(part, "root") else part
                if hasattr(part_data, "text"):
                    text = part_data.text.lower()
                    if "non-qualifying" in text or "non_qualifying" in text:
                        template_type = "non_qualifying"
                    elif "edge" in text:
                        template_type = "edge_case"
                elif hasattr(part_data, "data") and isinstance(part_data.data, dict):
                    if "template_type" in part_data.data:
                        template_type = part_data.data["template_type"]
                    if "signals" in part_data.data:
                        signals = part_data.data["signals"]

        # Update task to running
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
            task.status = TaskStatus(
                state=TaskState.failed,
                message={"role": "agent", "parts": [{"text": "Task timed out"}]},
            )
            yield task


class PurpleRequestHandler(DefaultRequestHandler):
    """Request handler for Purple Agent A2A server."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.task_store = InMemoryTaskStore()
        self.executor = PurpleAgentExecutor(timeout=timeout)
        super().__init__(
            agent_executor=self.executor,
            task_store=self.task_store,
        )

    async def on_message_send(self, params: MessageSendParams, context=None) -> Message | Task:
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


def create_app(timeout: int = DEFAULT_TIMEOUT):
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


def main():
    """Run the Purple Agent A2A server."""
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
