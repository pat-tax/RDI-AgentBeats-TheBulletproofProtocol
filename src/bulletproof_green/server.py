"""Green Agent A2A server for IRS Section 41 narrative evaluation.

Exposes narrative evaluation and scoring via JSON-RPC 2.0 protocol following A2A specification.
"""

from __future__ import annotations

import asyncio
import os
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

from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor
from bulletproof_green.evaluator import RuleBasedEvaluator
from bulletproof_green.llm_judge import LLMJudge
from bulletproof_green.models import GreenAgentOutput
from bulletproof_green.scorer import AgentBeatsScorer

if TYPE_CHECKING:
    from a2a.server.context import ServerCallContext

DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 300
DEFAULT_PURPLE_AGENT_URL = "http://localhost:8001"


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

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        purple_agent_url: str | None = None,
    ):
        self.evaluator = RuleBasedEvaluator()
        self.scorer = AgentBeatsScorer()
        self.llm_judge = LLMJudge()  # Initialize LLM judge for hybrid scoring
        self.timeout = timeout
        self.purple_agent_url = purple_agent_url or os.getenv(
            "PURPLE_AGENT_URL", DEFAULT_PURPLE_AGENT_URL
        )

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

    def _extract_mode_params(self, params: MessageSendParams) -> dict[str, Any]:
        """Extract mode and configuration parameters from message.

        Args:
            params: Message parameters from the request.

        Returns:
            Dict containing mode and optional configuration parameters.
        """
        mode_params: dict[str, Any] = {"mode": "single-shot"}

        # Get data from first part with data content
        data = self._get_first_data_part(params)
        if data:
            # Extract mode and arena configuration parameters
            param_keys = ["mode", "context", "max_iterations", "target_risk_score"]
            mode_params.update({k: data[k] for k in param_keys if k in data})

        return mode_params

    def _get_first_data_part(self, params: MessageSendParams) -> dict[str, Any] | None:
        """Get data from first message part that contains data.

        Args:
            params: Message parameters from the request.

        Returns:
            Data dict from first data part, or None if no data part found.
        """
        if not params.message or not params.message.parts:
            return None

        for part in params.message.parts:
            data = self._extract_data_from_part(part)
            if data:
                return data

        return None

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
        # Extract mode and parameters
        mode_params = self._extract_mode_params(params)
        mode = mode_params.get("mode", "single-shot")

        # Update task to working
        task.status = TaskStatus(state=TaskState.working)
        yield task

        try:
            if mode == "arena":
                # Arena mode - multi-turn iterative refinement
                async for event in self._execute_arena_mode(params, task, mode_params):
                    yield event
            else:
                # Single-shot mode - traditional evaluation
                async for event in self._execute_single_shot(params, task):
                    yield event

        except TimeoutError:
            task.status = TaskStatus(state=TaskState.failed)
            yield task

    async def _execute_single_shot(
        self, params: MessageSendParams, task: Task
    ) -> AsyncGenerator[Message | Task]:
        """Execute single-shot narrative evaluation with hybrid scoring.

        Args:
            params: Message parameters from the request.
            task: The task being executed.

        Yields:
            Task updates and final Message with evaluation scores.
        """
        # Extract narrative from message
        narrative = self._extract_narrative(params)

        # Evaluate and score with timeout
        eval_result = await asyncio.wait_for(
            asyncio.to_thread(self.evaluator.evaluate, narrative),
            timeout=self.timeout,
        )

        score_result = await asyncio.wait_for(
            asyncio.to_thread(self.scorer.score, eval_result),
            timeout=self.timeout,
        )

        # Apply hybrid scoring using LLM judge
        # Compute rule-based overall score first
        rule_based_overall_score = score_result.overall_score

        # Get hybrid score (combines rule-based + LLM)
        hybrid_result = await asyncio.wait_for(
            self.llm_judge.hybrid_score(narrative, rule_based_overall_score),
            timeout=self.timeout,
        )

        # Use hybrid score as the final overall score
        final_overall_score = hybrid_result.final_score

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
                # Evaluation metrics (using hybrid scoring)
                "overall_score": final_overall_score,  # Hybrid score
                "correctness": score_result.correctness,
                "safety": score_result.safety,
                "specificity": score_result.specificity,
                "experimentation": score_result.experimentation,
                "classification": eval_result.classification,
                "risk_score": eval_result.risk_score,
                "risk_category": eval_result.risk_category,
                "confidence": eval_result.confidence,
                "redline": eval_result.redline.model_dump(),
            }
        )

        # Create response with DataPart in AgentBeats format
        data_part = DataPart(data=output.model_dump())

        # Mark task completed
        task.status = TaskStatus(state=TaskState.completed)
        yield task

        # Return message with evaluation results
        yield new_agent_parts_message(parts=[Part(root=data_part)])

    async def _execute_arena_mode(
        self, params: MessageSendParams, task: Task, mode_params: dict[str, Any]
    ) -> AsyncGenerator[Message | Task]:
        """Execute arena mode multi-turn iterative refinement.

        Args:
            params: Message parameters from the request.
            task: The task being executed.
            mode_params: Mode configuration parameters.

        Yields:
            Task updates and final Message with ArenaResult.
        """
        # Extract context for arena mode
        context = mode_params.get("context", "")

        # Create arena configuration
        config = ArenaConfig(
            max_iterations=mode_params.get("max_iterations", 5),
            target_risk_score=mode_params.get("target_risk_score", 20),
        )

        # Create arena executor
        arena_executor = ArenaExecutor(
            purple_agent_url=self.purple_agent_url,
            config=config,
        )

        # Run arena loop
        arena_result = await asyncio.wait_for(
            arena_executor.run(initial_context=context),
            timeout=self.timeout,
        )

        # Convert ArenaResult to dict for response
        result_data = {
            "success": arena_result.success,
            "iterations": [
                {
                    "iteration_number": iteration.iteration_number,
                    "narrative": iteration.narrative,
                    "risk_score": iteration.risk_score,
                    "state": iteration.state,
                    "critique": iteration.critique,
                    "evaluation": iteration.evaluation,
                }
                for iteration in arena_result.iterations
            ],
            "total_iterations": arena_result.total_iterations,
            "final_risk_score": arena_result.final_risk_score,
            "final_narrative": arena_result.final_narrative,
            "termination_reason": arena_result.termination_reason,
        }

        # Create response with ArenaResult
        data_part = DataPart(data=result_data)

        # Mark task completed
        task.status = TaskStatus(state=TaskState.completed)
        yield task

        # Return message with arena results
        yield new_agent_parts_message(parts=[Part(root=data_part)])


class GreenRequestHandler(DefaultRequestHandler):
    """Request handler for Green Agent A2A server."""

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
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
    timeout: int = DEFAULT_TIMEOUT,
    purple_agent_url: str | None = None,
) -> Any:
    """Create the A2A FastAPI application.

    Args:
        timeout: Task timeout in seconds (default 300).
        purple_agent_url: Optional Purple Agent URL for arena mode.

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
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
