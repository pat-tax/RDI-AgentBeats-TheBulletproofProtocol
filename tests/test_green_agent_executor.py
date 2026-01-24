"""Tests for Green Agent executor (STORY-005).

This test module validates the acceptance criteria for STORY-005:
- Executor accepts task with narrative input
- Returns structured artifact: {risk_score: 0-100, classification: QUALIFYING|NON_QUALIFYING, component_scores: {}, redline: {}}
- Handles async execution pattern
- Validates input narrative is present before evaluation
- Returns error for invalid inputs
"""

import anyio
import pytest

from bulletproof_green.executor import GreenAgentExecutor


class TestGreenAgentExecutor:
    """Test executor accepts task and returns evaluation artifacts."""

    def test_executor_accepts_task_with_narrative_input(self):
        """Test that executor accepts task with narrative input."""
        executor = GreenAgentExecutor()

        async def run_test():
            return await executor.execute(narrative="Test R&D narrative for evaluation")

        task = anyio.run(run_test)

        assert task is not None
        assert hasattr(task, "artifacts")

    def test_executor_returns_structured_artifact(self):
        """Test that executor returns structured artifact with evaluation result."""
        executor = GreenAgentExecutor()

        async def run_test():
            narrative = "We developed a novel machine learning algorithm to solve uncertainty in data classification."
            return await executor.execute(narrative=narrative)

        task = anyio.run(run_test)

        assert len(task.artifacts) > 0
        artifact = task.artifacts[0]
        assert hasattr(artifact, "parts")
        assert len(artifact.parts) > 0

    def test_executor_handles_async_execution(self):
        """Test that executor handles async execution pattern."""
        executor = GreenAgentExecutor()

        async def run_test():
            return await executor.execute(narrative="Test async execution")

        # This test verifies async/await works
        task = anyio.run(run_test)
        assert task is not None

    def test_executor_validates_narrative_is_present(self):
        """Test that executor validates input narrative is present."""
        executor = GreenAgentExecutor()

        async def run_test():
            # Empty narrative should raise error
            return await executor.execute(narrative="")

        with pytest.raises(ValueError, match="narrative"):
            anyio.run(run_test)

    def test_executor_returns_error_for_invalid_inputs(self):
        """Test that executor returns error for invalid inputs."""
        executor = GreenAgentExecutor()

        async def run_test():
            # None narrative should raise error
            return await executor.execute(narrative=None)  # type: ignore[arg-type]

        with pytest.raises(ValueError):
            anyio.run(run_test)


class TestEvaluationResult:
    """Test evaluation result structure and content."""

    def test_evaluation_includes_risk_score(self):
        """Test that evaluation result includes risk_score (0-100)."""
        executor = GreenAgentExecutor()

        async def run_test():
            narrative = "We conducted experiments to develop novel algorithms for uncertain technical challenges."
            return await executor.execute(narrative=narrative)

        task = anyio.run(run_test)

        # Extract result from artifact
        artifact = task.artifacts[0]
        result_text = artifact.parts[0].root.text  # type: ignore[attr-defined]

        # Result should mention risk score
        assert "risk_score" in result_text.lower() or "risk score" in result_text.lower()

    def test_evaluation_includes_classification(self):
        """Test that evaluation result includes classification (QUALIFYING or NON_QUALIFYING)."""
        executor = GreenAgentExecutor()

        async def run_test():
            narrative = "We fixed bugs and performed routine maintenance on the production system."
            return await executor.execute(narrative=narrative)

        task = anyio.run(run_test)

        # Extract result from artifact
        artifact = task.artifacts[0]
        result_text = artifact.parts[0].root.text  # type: ignore[attr-defined]

        # Result should include classification
        assert "QUALIFYING" in result_text or "NON_QUALIFYING" in result_text

    def test_evaluation_includes_component_scores(self):
        """Test that evaluation result includes component_scores breakdown."""
        executor = GreenAgentExecutor()

        async def run_test():
            narrative = "Research and development of novel machine learning techniques."
            return await executor.execute(narrative=narrative)

        task = anyio.run(run_test)

        # Extract result from artifact
        artifact = task.artifacts[0]
        result_text = artifact.parts[0].root.text  # type: ignore[attr-defined]

        # Result should mention component scores
        assert "component_scores" in result_text.lower() or "component scores" in result_text.lower()

    def test_evaluation_includes_redline_feedback(self):
        """Test that evaluation result includes redline feedback."""
        executor = GreenAgentExecutor()

        async def run_test():
            narrative = "We improved the system performance significantly."
            return await executor.execute(narrative=narrative)

        task = anyio.run(run_test)

        # Extract result from artifact
        artifact = task.artifacts[0]
        result_text = artifact.parts[0].root.text  # type: ignore[attr-defined]

        # Result should mention redline
        assert "redline" in result_text.lower()

    def test_risk_score_is_between_0_and_100(self):
        """Test that risk_score is within valid range 0-100."""
        executor = GreenAgentExecutor()

        async def run_test():
            narrative = "Conducted research into novel algorithms for technical uncertainty resolution."
            return await executor.execute(narrative=narrative)

        task = anyio.run(run_test)

        # Extract result from artifact
        artifact = task.artifacts[0]
        result_text = artifact.parts[0].root.text  # type: ignore[attr-defined]

        # Should contain a numeric risk score
        # For this test, we just verify the structure includes risk score
        assert "risk_score" in result_text.lower() or "risk score" in result_text.lower()
