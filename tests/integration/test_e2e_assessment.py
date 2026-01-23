"""End-to-end integration tests for purple → green evaluation flow (STORY-015).

This test module validates complete agent-to-agent evaluation:
- Purple agent generates narrative
- Green agent evaluates the generated narrative
- Results are output to results/local_benchmark.json
- Results structure is queryable with DuckDB
"""

import json
from pathlib import Path

import anyio
import pytest

from bulletproof_green.executor import GreenAgentExecutor
from bulletproof_purple.executor import PurpleAgentExecutor


class TestE2EAssessment:
    """Test end-to-end purple → green evaluation flow."""

    @pytest.fixture
    def results_dir(self):
        """Return results directory path."""
        return Path(__file__).parent.parent.parent / "results"

    def test_purple_generates_narrative_green_evaluates(self):
        """Test purple agent generates narrative and green agent evaluates it."""
        purple_executor = PurpleAgentExecutor()
        green_executor = GreenAgentExecutor()

        async def run_test():
            # Step 1: Purple agent generates narrative
            purple_task = await purple_executor.execute(
                prompt="Generate a qualifying R&D narrative"
            )

            # Extract generated narrative
            assert purple_task.artifacts is not None
            narrative = purple_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]
            assert len(narrative) > 0

            # Step 2: Green agent evaluates the narrative
            green_task = await green_executor.execute(narrative=narrative)

            # Extract evaluation result
            assert green_task.artifacts is not None
            evaluation_text = green_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]
            evaluation = json.loads(evaluation_text)

            return evaluation

        evaluation = anyio.run(run_test)

        # Verify evaluation structure
        assert "risk_score" in evaluation
        assert "classification" in evaluation
        assert "component_scores" in evaluation
        assert "redline" in evaluation

    def test_e2e_outputs_results_to_local_benchmark_json(self, results_dir):
        """Test E2E flow outputs results to results/local_benchmark.json."""
        purple_executor = PurpleAgentExecutor()
        green_executor = GreenAgentExecutor()

        async def run_benchmark():
            # Run multiple iterations to generate benchmark data
            results = []
            n_tasks = 5

            for i in range(n_tasks):
                # Generate narrative
                purple_task = await purple_executor.execute(
                    prompt=f"Generate narrative variation {i}"
                )

                assert purple_task.artifacts is not None
                narrative = purple_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]

                # Evaluate narrative
                green_task = await green_executor.execute(narrative=narrative)

                assert green_task.artifacts is not None
                evaluation_text = green_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]
                evaluation = json.loads(evaluation_text)

                results.append(evaluation)

            return results

        results = anyio.run(run_benchmark)
        n_tasks = len(results)

        # Calculate benchmark metrics
        risk_scores = [r["risk_score"] for r in results]
        traffic_light_green = sum(1 for score in risk_scores if score < 20)
        traffic_light_green_pct = (traffic_light_green / n_tasks) * 100

        # Create benchmark output
        benchmark_output = {
            "participant_id": "bulletproof-purple-local",
            "pass_rate": traffic_light_green_pct,
            "traffic_light_green_pct": traffic_light_green_pct,
            "n_tasks": n_tasks,
            "risk_scores": risk_scores,
        }

        # Write to results/local_benchmark.json
        results_dir.mkdir(parents=True, exist_ok=True)
        output_file = results_dir / "local_benchmark.json"

        with open(output_file, "w") as f:
            json.dump(benchmark_output, f, indent=2)

        # Verify file was created
        assert output_file.exists()

        # Verify content
        with open(output_file) as f:
            saved_data = json.load(f)

        assert saved_data["participant_id"] == "bulletproof-purple-local"
        assert saved_data["n_tasks"] == n_tasks
        assert len(saved_data["risk_scores"]) == n_tasks
        assert 0 <= saved_data["traffic_light_green_pct"] <= 100

    def test_benchmark_results_structure(self, results_dir):
        """Test results JSON has correct structure for DuckDB querying."""
        # Expected structure
        expected_fields = {
            "participant_id": str,
            "pass_rate": (int, float),
            "traffic_light_green_pct": (int, float),
            "n_tasks": int,
            "risk_scores": list,
        }

        # This test assumes results file exists from previous test
        output_file = results_dir / "local_benchmark.json"

        if output_file.exists():
            with open(output_file) as f:
                data = json.load(f)

            # Verify all expected fields exist
            for field, expected_type in expected_fields.items():
                assert field in data
                assert isinstance(data[field], expected_type)

            # Verify risk_scores is list of integers
            assert all(isinstance(score, int) for score in data["risk_scores"])
            assert all(0 <= score <= 100 for score in data["risk_scores"])

    def test_e2e_validates_green_agent_structured_output(self):
        """Test E2E validates green agent returns structured output (not string)."""
        purple_executor = PurpleAgentExecutor()
        green_executor = GreenAgentExecutor()

        async def run_test():
            # Generate narrative
            purple_task = await purple_executor.execute(prompt="Generate test narrative")

            assert purple_task.artifacts is not None
            narrative = purple_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]

            # Evaluate narrative
            green_task = await green_executor.execute(narrative=narrative)

            assert green_task.artifacts is not None
            evaluation_text = green_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]

            # Must be valid JSON
            evaluation = json.loads(evaluation_text)
            return evaluation

        evaluation = anyio.run(run_test)

        # Must be dict, not string
        assert isinstance(evaluation, dict)

        # Must have all required structured fields
        required_fields = ["risk_score", "classification", "component_scores", "redline"]
        for field in required_fields:
            assert field in evaluation

    def test_multiple_narratives_produce_varied_risk_scores(self):
        """Test that different narrative types produce varied risk scores."""
        purple_executor = PurpleAgentExecutor()
        green_executor = GreenAgentExecutor()

        prompts = [
            "Generate a qualifying R&D narrative",
            "Generate a non-qualifying routine narrative",
            "Generate an edge case narrative",
        ]

        async def run_test():
            risk_scores = []

            for prompt in prompts:
                # Generate narrative
                purple_task = await purple_executor.execute(prompt=prompt)

                assert purple_task.artifacts is not None
                narrative = purple_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]

                # Evaluate narrative
                green_task = await green_executor.execute(narrative=narrative)

                assert green_task.artifacts is not None
                evaluation_text = green_task.artifacts[0].parts[0].root.text  # type: ignore[attr-defined]
                evaluation = json.loads(evaluation_text)

                risk_scores.append(evaluation["risk_score"])

            return risk_scores

        risk_scores = anyio.run(run_test)

        # Should have variation in risk scores
        assert len(set(risk_scores)) > 1  # Not all the same
        assert all(0 <= score <= 100 for score in risk_scores)
