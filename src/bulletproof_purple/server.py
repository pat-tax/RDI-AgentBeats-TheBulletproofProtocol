"""A2A Server for Bulletproof Purple Agent (R&D Narrative Generator).

This server implements the A2A protocol for the purple agent, which generates
R&D tax credit narratives as a reference implementation for testing the
green agent benchmark.
"""

import argparse
import uuid

import uvicorn
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers.request_handler import RequestHandler
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    Artifact,
    Message,
    MessageSendParams,
    Part,
    Task,
    TaskStatus,
    TextPart,
)


class PurpleAgentHandler(RequestHandler):
    """Request handler for purple agent tasks."""

    async def on_message_send(
        self,
        params: MessageSendParams,
        context=None,
    ) -> Task | Message:
        """Handle message/send requests for narrative generation.

        This implements the A2A protocol's message/send JSON-RPC method.

        Args:
            params: Message parameters including the input message
            context: Server call context (optional)

        Returns:
            Task object with generated narrative artifact
        """
        # Extract message text from params
        message_text = ""
        if params.message and hasattr(params.message, "parts"):
            for part in params.message.parts:
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    message_text += part.root.text  # type: ignore[attr-defined]

        # Simple narrative generation for now (STORY-002 will implement full executor)
        narrative = (
            "Our engineering team developed a novel distributed caching system "
            "to reduce database latency by 40ms. The technical uncertainty centered "
            "on implementing consistent hashing with minimal overhead. We experimented "
            "with three different algorithms before finding a solution."
        )

        # Return a Task with the narrative as an artifact
        context_id = (
            params.message.context_id
            if params.message and params.message.context_id
            else str(uuid.uuid4())
        )
        return Task(
            id=str(uuid.uuid4()),
            context_id=context_id,
            status=TaskStatus(state="completed"),  # type: ignore[arg-type]
            artifacts=[
                Artifact(
                    artifact_id=str(uuid.uuid4()),
                    name="narrative",
                    parts=[Part(root=TextPart(text=narrative))],
                )
            ],
        )

    # Stub implementations for other required abstract methods
    async def on_cancel_task(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_delete_task_push_notification_config(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_get_task(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_get_task_push_notification_config(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_list_task_push_notification_config(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_message_send_stream(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_resubscribe_to_task(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError

    async def on_set_task_push_notification_config(self, params, context=None):
        """Not implemented."""
        raise NotImplementedError


def create_app(card_url: str) -> A2AFastAPIApplication:
    """Create A2A FastAPI application for purple agent.

    Args:
        card_url: Public URL where the agent card is accessible

    Returns:
        Configured A2A FastAPI application
    """
    agent_card = AgentCard(
        name="bulletproof-purple-substantiator",
        description=(
            "R&D Tax Credit Narrative Generator - "
            "Reference Implementation for AgentBeats Legal Track"
        ),
        version="0.0.0",
        url=card_url,
        capabilities=AgentCapabilities(),  # Use empty AgentCapabilities object
        skills=[],  # No specific skills defined
        default_input_modes=["text"],  # Accepts text input
        default_output_modes=["text"],  # Returns text output
    )

    handler = PurpleAgentHandler()

    return A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=handler,
    )


def main() -> None:
    """Run the purple agent A2A server."""
    parser = argparse.ArgumentParser(description="Bulletproof Purple Agent - A2A Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    parser.add_argument(
        "--card-url",
        default="http://localhost:8000",
        help="Public URL for the agent card (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    app = create_app(args.card_url).build()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
