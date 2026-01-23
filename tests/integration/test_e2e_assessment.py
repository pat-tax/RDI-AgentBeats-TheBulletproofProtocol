"""End-to-end integration tests for purple → green evaluation flow (STORY-015).

This test module validates complete agent-to-agent evaluation:
- Purple agent generates narrative
- Green agent evaluates the generated narrative
- Results are output to results/local_benchmark.json
- Results are queryable with DuckDB
"""

import json
from pathlib import Path

import httpx
import pytest


class TestE2EAssessment:
    """Test end-to-end purple → green evaluation flow."""

    @pytest.fixture
    def purple_agent_url(self):
        """Return purple agent URL."""
        return "http://localhost:8002"

    @pytest.fixture
    def green_agent_url(self):
        """Return green agent URL."""
        return "http://localhost:8001"

    @pytest.fixture
    def results_dir(self):
        """Return results directory path."""
        return Path(__file__).parent.parent.parent / "results"

    @pytest.mark.integration
    def test_purple_generates_narrative_green_evaluates(
        self, purple_agent_url, green_agent_url
    ):
        """Test purple agent generates narrative and green agent evaluates it."""
        # Step 1: Purple agent generates narrative
        purple_task = {
            "context_id": "e2e-test-001",
            "input": {
                "parts": [{"text": "Generate a qualifying R&D narrative"}]
            },
        }

        purple_response = httpx.post(
            f"{purple_agent_url}/task/send",
            json=purple_task,
            timeout=10.0,
        )

        assert purple_response.status_code == 200
        purple_result = purple_response.json()

        # Extract generated narrative
        narrative = purple_result["artifacts"][0]["parts"][0]["text"]
        assert len(narrative) > 0

        # Step 2: Green agent evaluates the narrative
        green_task = {
            "context_id": "e2e-test-001-eval",
            "input": {
                "parts": [{"text": narrative}]
            },
        }

        green_response = httpx.post(
            f"{green_agent_url}/task/send",
            json=green_task,
            timeout=10.0,
        )

        assert green_response.status_code == 200
        green_result = green_response.json()

        # Extract evaluation result
        evaluation_text = green_result["artifacts"][0]["parts"][0]["text"]
        evaluation = json.loads(evaluation_text)

        # Verify evaluation structure
        assert "risk_score" in evaluation
        assert "classification" in evaluation
        assert "component_scores" in evaluation
        assert "redline" in evaluation

    @pytest.mark.integration
    def test_e2e_outputs_results_to_local_benchmark_json(
        self, purple_agent_url, green_agent_url, results_dir
    ):
        """Test E2E flow outputs results to results/local_benchmark.json."""
        # Run multiple iterations to generate benchmark data
        results = []
        n_tasks = 5

        for i in range(n_tasks):
            # Generate narrative
            purple_task = {
                "context_id": f"benchmark-{i}",
                "input": {
                    "parts": [{"text": f"Generate narrative variation {i}"}]
                },
            }

            purple_response = httpx.post(
                f"{purple_agent_url}/task/send",
                json=purple_task,
                timeout=10.0,
            )

            narrative = purple_response.json()["artifacts"][0]["parts"][0]["text"]

            # Evaluate narrative
            green_task = {
                "context_id": f"benchmark-{i}-eval",
                "input": {
                    "parts": [{"text": narrative}]
                },
            }

            green_response = httpx.post(
                f"{green_agent_url}/task/send",
                json=green_task,
                timeout=10.0,
            )

            evaluation_text = green_response.json()["artifacts"][0]["parts"][0]["text"]
            evaluation = json.loads(evaluation_text)

            results.append(evaluation)

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

    @pytest.mark.integration
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

    @pytest.mark.integration
    def test_e2e_validates_green_agent_structured_output(
        self, purple_agent_url, green_agent_url
    ):
        """Test E2E validates green agent returns structured output (not string)."""
        # Generate narrative
        purple_task = {
            "context_id": "validation-test",
            "input": {
                "parts": [{"text": "Generate test narrative"}]
            },
        }

        purple_response = httpx.post(
            f"{purple_agent_url}/task/send",
            json=purple_task,
            timeout=10.0,
        )

        narrative = purple_response.json()["artifacts"][0]["parts"][0]["text"]

        # Evaluate narrative
        green_task = {
            "context_id": "validation-test-eval",
            "input": {
                "parts": [{"text": narrative}]
            },
        }

        green_response = httpx.post(
            f"{green_agent_url}/task/send",
            json=green_task,
            timeout=10.0,
        )

        evaluation_text = green_response.json()["artifacts"][0]["parts"][0]["text"]

        # Must be valid JSON
        evaluation = json.loads(evaluation_text)

        # Must be dict, not string
        assert isinstance(evaluation, dict)

        # Must have all required structured fields
        required_fields = ["risk_score", "classification", "component_scores", "redline"]
        for field in required_fields:
            assert field in evaluation

    @pytest.mark.integration
    def test_multiple_narratives_produce_varied_risk_scores(
        self, purple_agent_url, green_agent_url
    ):
        """Test that different narrative types produce varied risk scores."""
        prompts = [
            "Generate a qualifying R&D narrative",
            "Generate a non-qualifying routine narrative",
            "Generate an edge case narrative",
        ]

        risk_scores = []

        for prompt in prompts:
            # Generate narrative
            purple_task = {
                "context_id": f"variety-{prompt[:10]}",
                "input": {
                    "parts": [{"text": prompt}]
                },
            }

            purple_response = httpx.post(
                f"{purple_agent_url}/task/send",
                json=purple_task,
                timeout=10.0,
            )

            narrative = purple_response.json()["artifacts"][0]["parts"][0]["text"]

            # Evaluate narrative
            green_task = {
                "context_id": f"variety-eval-{prompt[:10]}",
                "input": {
                    "parts": [{"text": narrative}]
                },
            }

            green_response = httpx.post(
                f"{green_agent_url}/task/send",
                json=green_task,
                timeout=10.0,
            )

            evaluation_text = green_response.json()["artifacts"][0]["parts"][0]["text"]
            evaluation = json.loads(evaluation_text)

            risk_scores.append(evaluation["risk_score"])

        # Should have variation in risk scores
        assert len(set(risk_scores)) > 1  # Not all the same
        assert all(0 <= score <= 100 for score in risk_scores)
