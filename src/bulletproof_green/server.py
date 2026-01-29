"""Green Agent server - "How to expose it" (transport layer)

Responsibilities:
- HTTP server setup (FastAPI/Uvicorn)
- Request routing (A2A JSON-RPC 2.0 endpoints)
- Entry point (main() with CLI args)

Pattern: server.py = Transport layer, separated from protocol (executor.py)
         and domain (agent.py)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    Message,
    MessageSendParams,
    Task,
)
from a2a.utils import new_task

from bulletproof_green.agent import get_agent_card
from bulletproof_green.executor import GreenAgentExecutor
from bulletproof_green.settings import settings

if TYPE_CHECKING:
    from a2a.server.context import ServerCallContext


class GreenRequestHandler(DefaultRequestHandler):
    """Request handler for Green Agent A2A server."""

    def __init__(
        self,
        timeout: int | None = None,
        purple_agent_url: str | None = None,
    ):
        self.task_store = InMemoryTaskStore()
        self.executor = GreenAgentExecutor(
            timeout=timeout,
            purple_agent_url=purple_agent_url,
        )
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
            Message with evaluation scores or Task status.
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


def create_app(
    timeout: int | None = None,
    purple_agent_url: str | None = None,
) -> Any:
    """Create the A2A FastAPI application.

    Args:
        timeout: Task timeout in seconds (uses settings.timeout if not provided).
        purple_agent_url: Purple Agent URL for arena mode (uses settings if not provided).

    Returns:
        Configured FastAPI application.
    """
    agent_card = get_agent_card()
    handler = GreenRequestHandler(
        timeout=timeout,
        purple_agent_url=purple_agent_url,
    )

    a2a_app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    return a2a_app.build()


def main() -> None:
    """Run the Green Agent A2A server."""
    import sys

    import uvicorn
    from pydantic import ValidationError

    # Validate settings on startup (fail fast)
    try:
        _ = settings.model_dump()
    except ValidationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    app = create_app()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
