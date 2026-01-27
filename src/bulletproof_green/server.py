"""Green Agent A2A server for IRS Section 41 narrative evaluation.

Exposes narrative evaluation and scoring via JSON-RPC 2.0 protocol following A2A specification.
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
from pydantic import BaseModel

from bulletproof_green.evaluator import RuleBasedEvaluator
from bulletproof_green.scorer import AgentBeatsScorer


class GreenAgentOutput(BaseModel):
    """AgentBeats-compatible output schema for Green Agent evaluation results."""

    # AgentBeats required fields
    domain: str
    score: float
    max_score: int
    pass_rate: float
    task_rewards: dict[str, float]
    time_used: float
    # Evaluation metrics
    overall_score: float
    correctness: float
    safety: float
    specificity: float
    experimentation: float
    classification: str
    risk_score: int
    risk_category: str
    confidence: float
    redline: dict[str, Any]


if TYPE_CHECKING:
    from a2a.server.context import ServerCallContext

DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 300


def get_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Create the AgentCard for Green Agent.

    Args:
        base_url: Base URL where the agent is hosted.

    Returns:
        Configured AgentCard with narrative evaluation capability.
    """
    return AgentCard(
        name="Bulletproof Green Agent",
        description="IRS Section 41 R&D tax credit narrative evaluator. "
        "Evaluates Four-Part Test narratives against IRS audit standards.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,  # type: ignore[call-arg]
        ),
        defaultInputModes=["text", "data"],  # type: ignore[call-arg]
        defaultOutputModes=["data"],  # type: ignore[call-arg]
        skills=[
            AgentSkill(
                id="evaluate_narrative",
                name="Evaluate Narrative",
                description="Evaluate IRS Section 41 R&D tax credit narrative "
                "against audit standards and return compliance scores.",
                tags=["irs", "r&d", "tax-credit", "evaluation", "scoring"],
                examples=[
                    "Evaluate this R&D narrative for IRS compliance",
                    "Score my Four-Part Test documentation",
                ],
            )
        ],
    )


class GreenAgentExecutor:
    """Executor that evaluates narratives using the RuleBasedEvaluator and Scorer."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.evaluator = RuleBasedEvaluator()
        self.scorer = AgentBeatsScorer()
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

    def _extract_narrative(self, params: MessageSendParams) -> str:
        """Extract narrative text from message parameters.

        Args:
            params: Message parameters from the request.

        Returns:
            The narrative text to evaluate.
        """
        narrative = ""

        if params.message and params.message.parts:
            for part in params.message.parts:
                # Try text content first
                text = self._extract_text_from_part(part)
                if text:
                    narrative = text
                    break

                # Try data content (narrative field)
                data = self._extract_data_from_part(part)
                if data and "narrative" in data:
                    narrative = data["narrative"]
                    break

        return narrative

    async def execute(
        self, params: MessageSendParams, task: Task
    ) -> AsyncGenerator[Message | Task]:
        """Execute narrative evaluation for incoming message.

        Args:
            params: Message parameters from the request.
            task: The task being executed.

        Yields:
            Task updates and final Message with evaluation scores.
        """
        # Extract narrative from message
        narrative = self._extract_narrative(params)

        # Update task to working
        task.status = TaskStatus(state=TaskState.working)
        yield task

        # Evaluate and score with timeout
        try:
            eval_result = await asyncio.wait_for(
                asyncio.to_thread(self.evaluator.evaluate, narrative),
                timeout=self.timeout,
            )

            score_result = await asyncio.wait_for(
                asyncio.to_thread(self.scorer.score, eval_result),
                timeout=self.timeout,
            )

            # Calculate task rewards (1.0 if score > 0.5, else 0.0)
            task_rewards = {
                "0": 1.0 if score_result.correctness > 0.5 else 0.0,
                "1": 1.0 if score_result.safety > 0.5 else 0.0,
                "2": 1.0 if score_result.specificity > 0.5 else 0.0,
                "3": 1.0 if score_result.experimentation > 0.5 else 0.0,
            }
            score = sum(task_rewards.values())
            max_score = len(task_rewards)
            pass_rate = (score / max_score) * 100 if max_score > 0 else 0.0

            # Validate output with Pydantic model
            output = GreenAgentOutput.model_validate(
                {
                    # AgentBeats required fields
                    "domain": "irs-r&d",
                    "score": score,
                    "max_score": max_score,
                    "pass_rate": pass_rate,
                    "task_rewards": task_rewards,
                    "time_used": eval_result.evaluation_time_ms / 1000,
                    # Evaluation metrics
                    "overall_score": score_result.overall_score,
                    "correctness": score_result.correctness,
                    "safety": score_result.safety,
                    "specificity": score_result.specificity,
                    "experimentation": score_result.experimentation,
                    "classification": eval_result.classification,
                    "risk_score": eval_result.risk_score,
                    "risk_category": eval_result.risk_category,
                    "confidence": eval_result.confidence,
                    "redline": eval_result.redline.to_dict(),
                }
            )

            # Create response with DataPart in AgentBeats format
            data_part = DataPart(data=output.model_dump())

            # Mark task completed
            task.status = TaskStatus(state=TaskState.completed)
            yield task

            # Return message with evaluation results
            yield new_agent_parts_message(parts=[Part(root=data_part)])

        except TimeoutError:
            task.status = TaskStatus(state=TaskState.failed)
            yield task


class GreenRequestHandler(DefaultRequestHandler):
    """Request handler for Green Agent A2A server."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.task_store = InMemoryTaskStore()
        self.executor = GreenAgentExecutor(timeout=timeout)
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


def create_app(timeout: int = DEFAULT_TIMEOUT) -> Any:
    """Create the A2A FastAPI application.

    Args:
        timeout: Task timeout in seconds (default 300).

    Returns:
        Configured FastAPI application.
    """
    agent_card = get_agent_card()
    handler = GreenRequestHandler(timeout=timeout)

    a2a_app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    return a2a_app.build()


def main() -> None:
    """Run the Green Agent A2A server."""
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
