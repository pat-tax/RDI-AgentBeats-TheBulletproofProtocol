"""A2A Server for Bulletproof Green Agent (IRS Section 41 Evaluator).

This server implements the A2A protocol for the green agent, which evaluates
R&D tax credit narratives for compliance with IRS Section 41 criteria.
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


class GreenAgentHandler(RequestHandler):
    """Request handler for green agent evaluation tasks."""

    async def on_message_send(
        self,
        params: MessageSendParams,
        context=None,
    ) -> Task | Message:
        """Handle message/send requests for narrative evaluation.

        This implements the A2A protocol's message/send JSON-RPC method.

        Args:
            params: Message parameters including the input narrative
            context: Server call context (optional)

        Returns:
            Task object with evaluation result artifact
        """
        # Extract message text from params
        message_text = ""
        if params.message and hasattr(params.message, "parts"):
            for part in params.message.parts:
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    message_text += part.root.text  # type: ignore[attr-defined]

        # Simple evaluation placeholder (STORY-005 will implement full evaluator)
        evaluation_result = (
            "Evaluation: Risk score 15, Classification: QUALIFYING. "
            "Narrative demonstrates technical uncertainty and process of experimentation."
        )

        # Return a Task with the evaluation as an artifact
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
                    name="evaluation",
                    parts=[Part(root=TextPart(text=evaluation_result))],
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
    """Create A2A FastAPI application for green agent.

    Args:
        card_url: Public URL where the agent card is accessible

    Returns:
        Configured A2A FastAPI application
    """
    agent_card = AgentCard(
        name="bulletproof-green-examiner",
        description=(
            "IRS Section 41 Evaluator - Benchmark for R&D Tax Credit Narrative Assessment"
        ),
        version="0.0.0",
        url=card_url,
        capabilities=AgentCapabilities(),  # Use empty AgentCapabilities object
        skills=[],  # No specific skills defined
        default_input_modes=["text"],  # Accepts text input
        default_output_modes=["text"],  # Returns text output
    )

    handler = GreenAgentHandler()

    return A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=handler,
    )


def main() -> None:
    """Run the green agent A2A server."""
    parser = argparse.ArgumentParser(description="Bulletproof Green Agent - A2A Server")
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
