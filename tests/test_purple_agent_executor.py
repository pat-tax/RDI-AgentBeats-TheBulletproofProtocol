"""Tests for Purple Agent executor (STORY-002).

This test module validates the acceptance criteria for STORY-002:
- Executor accepts task with prompt input
- Generates 300-500 word R&D narrative in IRS Section 41 format
- Returns structured artifact with narrative text
- Handles async execution pattern
- Includes at least 3 narrative templates (qualifying, non-qualifying, edge cases)
"""

import anyio

from bulletproof_purple.executor import PurpleAgentExecutor
from bulletproof_purple.generator import NarrativeGenerator
from bulletproof_purple.templates import NarrativeTemplates


class TestPurpleAgentExecutor:
    """Test executor accepts task and returns artifacts."""

    def test_executor_accepts_task_with_prompt(self):
        """Test that executor accepts task with prompt input."""
        executor = PurpleAgentExecutor()

        async def run_test():
            return await executor.execute(prompt="Generate qualifying R&D narrative")

        task = anyio.run(run_test)

        assert task is not None
        assert hasattr(task, "artifacts")

    def test_executor_returns_structured_artifact(self):
        """Test that executor returns structured artifact with narrative text."""
        executor = PurpleAgentExecutor()

        async def run_test():
            return await executor.execute(prompt="Generate narrative")

        task = anyio.run(run_test)

        assert len(task.artifacts) > 0
        artifact = task.artifacts[0]
        assert hasattr(artifact, "parts")
        assert len(artifact.parts) > 0
        # The part is wrapped - access the root TextPart
        part = artifact.parts[0]
        assert hasattr(part, "root") and hasattr(part.root, "text")

    def test_executor_handles_async_execution(self):
        """Test that executor handles async execution pattern."""
        executor = PurpleAgentExecutor()

        async def run_test():
            return await executor.execute(prompt="Test async")

        # This test verifies async/await works
        task = anyio.run(run_test)
        assert task is not None


class TestNarrativeGenerator:
    """Test narrative generation logic."""

    def test_generator_creates_300_to_500_word_narrative(self):
        """Test that generator creates narratives between 300-500 words."""
        generator = NarrativeGenerator()
        narrative = generator.generate(template_type="qualifying")

        word_count = len(narrative.split())
        assert 300 <= word_count <= 500, f"Expected 300-500 words, got {word_count}"

    def test_generator_produces_irs_section_41_format(self):
        """Test that narrative follows IRS Section 41 format."""
        generator = NarrativeGenerator()
        narrative = generator.generate(template_type="qualifying")

        # IRS Section 41 narratives should mention technical elements
        assert len(narrative) > 100
        # Should be substantive text, not just placeholders
        assert "R&D" in narrative or "research" in narrative.lower() or "development" in narrative.lower()

    def test_generator_handles_different_template_types(self):
        """Test that generator accepts different template types."""
        generator = NarrativeGenerator()

        qualifying = generator.generate(template_type="qualifying")
        non_qualifying = generator.generate(template_type="non_qualifying")
        edge_case = generator.generate(template_type="edge_case")

        # All should be valid narratives
        assert len(qualifying) > 0
        assert len(non_qualifying) > 0
        assert len(edge_case) > 0


class TestNarrativeTemplates:
    """Test narrative template library."""

    def test_templates_include_at_least_three_types(self):
        """Test that at least 3 narrative templates exist."""
        templates = NarrativeTemplates()

        assert hasattr(templates, "qualifying")
        assert hasattr(templates, "non_qualifying")
        assert hasattr(templates, "edge_case")

    def test_qualifying_template_exists(self):
        """Test that qualifying template is available."""
        templates = NarrativeTemplates()
        qualifying = templates.qualifying()

        assert isinstance(qualifying, str)
        assert len(qualifying) > 100

    def test_non_qualifying_template_exists(self):
        """Test that non-qualifying template is available."""
        templates = NarrativeTemplates()
        non_qualifying = templates.non_qualifying()

        assert isinstance(non_qualifying, str)
        assert len(non_qualifying) > 100

    def test_edge_case_template_exists(self):
        """Test that edge case template is available."""
        templates = NarrativeTemplates()
        edge_case = templates.edge_case()

        assert isinstance(edge_case, str)
        assert len(edge_case) > 100
