"""Agent executor for Purple Agent.

Handles task execution and returns structured artifacts.
"""

import uuid

from a2a.types import Artifact, Task, TaskStatus, TextPart

from bulletproof_purple.generator import NarrativeGenerator


class PurpleAgentExecutor:
    """Executes narrative generation tasks for Purple Agent."""

    def __init__(self) -> None:
        """Initialize the executor with a narrative generator."""
        self.generator = NarrativeGenerator()

    async def execute(self, prompt: str, context_id: str | None = None) -> Task:
        """Execute a narrative generation task.

        Args:
            prompt: Input prompt for narrative generation
            context_id: Optional context ID for the task

        Returns:
            Task object with narrative artifact
        """
        # Determine template type from prompt (simple keyword matching)
        template_type = self._select_template_type(prompt)

        # Generate narrative using the selected template
        narrative = self.generator.generate(template_type=template_type)

        # Create structured artifact
        artifact = Artifact(
            artifact_id=str(uuid.uuid4()),
            name="narrative",
            parts=[TextPart(text=narrative)],
        )

        # Return task with completed status
        return Task(
            id=str(uuid.uuid4()),
            context_id=context_id or str(uuid.uuid4()),
            status=TaskStatus(state="completed"),
            artifacts=[artifact],
        )

    def _select_template_type(self, prompt: str) -> str:
        """Select template type based on prompt keywords.

        Args:
            prompt: Input prompt text

        Returns:
            Template type (qualifying, non_qualifying, or edge_case)
        """
        prompt_lower = prompt.lower()

        if "non" in prompt_lower or "routine" in prompt_lower or "disqualify" in prompt_lower:
            return "non_qualifying"
        elif "edge" in prompt_lower or "borderline" in prompt_lower:
            return "edge_case"
        else:
            # Default to qualifying
            return "qualifying"
