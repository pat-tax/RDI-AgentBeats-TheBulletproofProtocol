"""Arena Mode orchestration for multi-turn adversarial narrative improvement.

Implements the iterative loop where Green Agent evaluates narratives from Purple Agent
and provides critique for iterative refinement until quality threshold is reached.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

from bulletproof_green.a2a_client import A2AClient
from bulletproof_green.evals.evaluator import RuleBasedEvaluator
from bulletproof_green.evals.models import NarrativeRequest


def _get_arena_max_iterations() -> int:
    from bulletproof_green.settings import settings

    return settings.arena_max_iterations


def _get_arena_target_risk_score() -> int:
    from bulletproof_green.settings import settings

    return settings.arena_target_risk_score


@dataclass
class ArenaConfig:
    """Configuration for Arena Mode execution.

    Attributes:
        max_iterations: Maximum number of iterations before stopping.
        target_risk_score: Target risk score threshold for success.

    Defaults are loaded from settings.
    """

    max_iterations: int = dataclasses.field(default_factory=_get_arena_max_iterations)
    target_risk_score: int = dataclasses.field(default_factory=_get_arena_target_risk_score)


@dataclass
class IterationRecord:
    """Record of a single iteration in the arena loop.

    Attributes:
        iteration_number: Sequential iteration number (1-indexed).
        narrative: The narrative text generated in this iteration.
        risk_score: Risk score from evaluation.
        state: Task state (pending, running, completed, failed).
        critique: Optional critique sent to Purple Agent for next iteration.
        evaluation: Optional full evaluation result dictionary.
    """

    iteration_number: int
    narrative: str
    risk_score: int
    state: str
    critique: str | None = None
    evaluation: dict[str, Any] | None = None


@dataclass
class ArenaResult:
    """Result of an Arena Mode execution.

    Attributes:
        success: Whether target risk score was achieved.
        iterations: List of all iteration records.
        total_iterations: Total number of iterations performed.
        final_risk_score: Risk score of the final iteration.
        final_narrative: Optional final narrative text.
        termination_reason: Reason for loop termination.
    """

    success: bool
    iterations: list[IterationRecord]
    total_iterations: int
    final_risk_score: int
    final_narrative: str | None = None
    termination_reason: str | None = None


class ArenaExecutor:
    """Orchestrates multi-turn adversarial loop for narrative improvement.

    The executor coordinates between Green Agent (evaluator) and Purple Agent
    (narrative generator) in an iterative refinement loop.

    Attributes:
        purple_agent_url: URL of the Purple Agent A2A endpoint.
        config: Arena configuration settings.
    """

    def __init__(
        self,
        purple_agent_url: str,
        config: ArenaConfig | None = None,
    ) -> None:
        """Initialize the ArenaExecutor.

        Args:
            purple_agent_url: URL of the Purple Agent A2A endpoint.
            config: Optional arena configuration (uses defaults if not provided).
        """
        self.purple_agent_url = purple_agent_url
        self.config = config if config is not None else ArenaConfig()
        self._a2a_client = A2AClient(base_url=purple_agent_url)
        self._evaluator = RuleBasedEvaluator()

    async def run(self, initial_context: str) -> ArenaResult:
        """Execute the arena mode loop.

        Args:
            initial_context: Initial context/prompt for narrative generation.

        Returns:
            ArenaResult containing success status and iteration history.
        """
        iterations: list[IterationRecord] = []
        current_critique: str | None = None
        current_context = initial_context

        for iteration_num in range(1, self.config.max_iterations + 1):
            # Run single iteration
            narrative, risk_score, evaluation = await self._run_iteration(
                context=current_context,
                critique=current_critique,
                iteration_number=iteration_num,
            )

            # Record iteration
            record = IterationRecord(
                iteration_number=iteration_num,
                narrative=narrative,
                risk_score=risk_score,
                state="completed",
                critique=current_critique,
                evaluation=evaluation,
            )
            iterations.append(record)

            # Check if target reached
            if risk_score < self.config.target_risk_score:
                return ArenaResult(
                    success=True,
                    iterations=iterations,
                    total_iterations=iteration_num,
                    final_risk_score=risk_score,
                    final_narrative=narrative,
                    termination_reason="target_reached",
                )

            # Generate critique for next iteration
            current_critique = self._generate_critique(evaluation)

        # Max iterations reached without success
        final_iteration = iterations[-1]
        return ArenaResult(
            success=False,
            iterations=iterations,
            total_iterations=len(iterations),
            final_risk_score=final_iteration.risk_score,
            final_narrative=final_iteration.narrative,
            termination_reason="max_iterations_reached",
        )

    async def _run_iteration(
        self,
        context: str,
        critique: str | None,
        iteration_number: int,
    ) -> tuple[str, int, dict[str, Any]]:
        """Run a single iteration of the arena loop.

        Args:
            context: Context for narrative generation.
            critique: Optional critique from previous iteration.
            iteration_number: Current iteration number.

        Returns:
            Tuple of (narrative, risk_score, evaluation_dict).
        """
        # Call Purple Agent to generate narrative
        narrative = await self._call_purple_agent(context, critique)

        # Evaluate the narrative
        risk_score, evaluation = self._evaluate_narrative(narrative)

        return narrative, risk_score, evaluation

    async def _call_purple_agent(
        self,
        context: str,
        critique: str | None = None,
    ) -> str:
        """Call Purple Agent via A2A to generate narrative.

        Args:
            context: Context for narrative generation.
            critique: Optional critique to guide regeneration.

        Returns:
            Generated narrative text.
        """
        # Build context with critique if provided
        full_context = context
        if critique:
            full_context = f"{context}\n\nCritique from previous iteration:\n{critique}"

        request = NarrativeRequest(
            template_type="qualifying",
            context=full_context,
        )

        response = await self._a2a_client.send_request(request)
        return response.narrative

    def _evaluate_narrative(self, narrative: str) -> tuple[int, dict[str, Any]]:
        """Evaluate a narrative using the rule-based evaluator.

        Args:
            narrative: Narrative text to evaluate.

        Returns:
            Tuple of (risk_score, evaluation_dict).
        """
        result = self._evaluator.evaluate(narrative)

        evaluation_dict: dict[str, Any] = {
            "classification": result.classification,
            "confidence": result.confidence,
            "risk_score": result.risk_score,
            "risk_category": result.risk_category,
            "component_scores": result.component_scores,
            "redline": {
                "total_issues": result.redline.total_issues,
                "issues": [
                    {
                        "category": issue.category,
                        "severity": issue.severity,
                        "text": issue.text,
                        "suggestion": issue.suggestion,
                    }
                    for issue in result.redline.issues
                ],
            },
        }

        return result.risk_score, evaluation_dict

    def _generate_critique(self, evaluation: dict[str, Any]) -> str:
        """Generate actionable critique from evaluation results.

        Args:
            evaluation: Evaluation result dictionary.

        Returns:
            Critique text for Purple Agent.
        """
        if not evaluation:
            return "Please improve the narrative to meet IRS Section 41 standards."

        critique_parts: list[str] = []

        # Add classification context
        classification = evaluation.get("classification", "UNKNOWN")
        risk_score = evaluation.get("risk_score", 100)
        critique_parts.append(
            f"Current classification: {classification} (risk score: {risk_score})"
        )

        # Add suggestions from issues
        redline = evaluation.get("redline", {})
        issues = redline.get("issues", [])

        if issues:
            critique_parts.append("\nAreas for improvement:")
            for issue in issues:
                category = issue.get("category", "unknown")
                suggestion = issue.get("suggestion", "")
                if suggestion:
                    critique_parts.append(f"- [{category}] {suggestion}")

        # Add general guidance if no specific issues
        if not issues:
            critique_parts.append(
                "\nGeneral guidance: Include specific technical uncertainties, "
                "documented failures, quantitative metrics, and evidence of "
                "iterative experimentation."
            )

        return "\n".join(critique_parts)
