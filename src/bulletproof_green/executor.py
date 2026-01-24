"""Agent executor for Green Agent.

Handles task execution and returns structured evaluation artifacts.
"""

import json
import uuid

from a2a.types import Artifact, Part, Task, TaskStatus, TextPart

from bulletproof_green.evaluator import NarrativeEvaluator


class GreenAgentExecutor:
    """Executes narrative evaluation tasks for Green Agent."""

    def __init__(self) -> None:
        """Initialize the executor with a narrative evaluator."""
        self.evaluator = NarrativeEvaluator()

    async def execute(self, narrative: str | None, context_id: str | None = None) -> Task:
        """Execute a narrative evaluation task.

        Args:
            narrative: Input narrative text for evaluation
            context_id: Optional context ID for the task

        Returns:
            Task object with evaluation artifact

        Raises:
            ValueError: If narrative is None or empty
        """
        # Validate input
        if narrative is None:
            raise ValueError("narrative cannot be None")
        if not narrative or narrative.strip() == "":
            raise ValueError("narrative cannot be empty")

        # Evaluate narrative (returns dict)
        evaluation_result = self.evaluator.evaluate(narrative)

        # Convert dict result to JSON string for artifact
        result_text = json.dumps(evaluation_result, indent=2)

        # Create structured artifact with evaluation result
        artifact = Artifact(
            artifact_id=str(uuid.uuid4()),
            name="evaluation",
            parts=[Part(root=TextPart(text=result_text))],
        )

        # Return task with completed status
        return Task(
            id=str(uuid.uuid4()),
            context_id=context_id or str(uuid.uuid4()),
            status=TaskStatus(state="completed"),  # type: ignore[arg-type]
            artifacts=[artifact],
        )
