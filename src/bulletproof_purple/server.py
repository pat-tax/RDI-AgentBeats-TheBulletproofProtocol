"""A2A Server for Bulletproof Purple Agent (R&D Narrative Generator).

This server implements the A2A protocol for the purple agent, which generates
R&D tax credit narratives as a reference implementation for testing the
green agent benchmark.
"""

import argparse
from typing import Any

import uvicorn
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.handlers import DefaultRequestHandler
from a2a.types import AgentCard


class PurpleAgentHandler(DefaultRequestHandler):
    """Request handler for purple agent tasks."""

    async def handle_task(self, task_input: dict[str, Any]) -> dict[str, Any]:
        """Handle task execution for narrative generation.

        Args:
            task_input: Task input containing prompt or parameters

        Returns:
            Task result with generated narrative artifact
        """
        # Simple narrative generation for now (STORY-002 will implement full executor)
        prompt = task_input.get("prompt", "Generate an R&D narrative")

        # Return a simple narrative artifact
        narrative = (
            "Our engineering team developed a novel distributed caching system "
            "to reduce database latency by 40ms. The technical uncertainty centered "
            "on implementing consistent hashing with minimal overhead. We experimented "
            "with three different algorithms before finding a solution."
        )

        return {
            "narrative": narrative,
            "prompt": prompt,
            "status": "completed",
        }


def create_app(card_url: str) -> A2AFastAPIApplication:
    """Create A2A FastAPI application for purple agent.

    Args:
        card_url: Public URL where the agent card is accessible

    Returns:
        Configured A2A FastAPI application
    """
    agent_card = AgentCard(
        name="bulletproof-purple-substantiator",
        description="R&D Tax Credit Narrative Generator - Reference Implementation for AgentBeats Legal Track",
        version="0.0.0",
        url=card_url,
    )

    handler = PurpleAgentHandler()

    return A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=handler,
    )


def main() -> None:
    """Run the purple agent A2A server."""
    parser = argparse.ArgumentParser(
        description="Bulletproof Purple Agent - A2A Server"
    )
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
