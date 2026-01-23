"""Integration tests for Green Agent evaluation (STORY-015).

This test module validates green agent integration:
- Green agent evaluation via A2A protocol
- Structured evaluation output with risk_score, classification, component_scores, redline
- AgentCard discovery
"""

import json

import httpx
import pytest


class TestGreenAgentEvaluation:
    """Test green agent evaluation via A2A protocol."""

    @pytest.fixture
    def green_agent_url(self):
        """Return green agent URL (assumes docker-compose running)."""
        return "http://localhost:8001"

    @pytest.mark.integration
    def test_green_agent_evaluates_narrative_via_task_send(self, green_agent_url):
        """Test green agent receives narrative and returns evaluation artifact."""
        # Test narrative
        test_narrative = """
        We faced significant technical uncertainty in developing a real-time anomaly detection
        system for high-frequency trading data. The uncertainty stemmed from the need to process
        1 million events per second while maintaining sub-5ms latency.

        We hypothesized that a novel sliding window algorithm with adaptive thresholds could
        solve this challenge. We tested three alternative approaches: fixed-window aggregation,
        streaming quantiles, and our proposed adaptive method.

        The fixed-window approach failed due to 200ms latency. The streaming quantile method
        was unsuccessful as it couldn't handle burst traffic patterns. Our adaptive approach
        reduced latency from 200ms to 3.2ms and increased throughput by 40x.
        """

        # Send evaluation task to green agent
        task_payload = {
            "context_id": "test-green-001",
            "input": {
                "parts": [{"text": test_narrative}]
            },
        }

        response = httpx.post(
            f"{green_agent_url}/task/send",
            json=task_payload,
            timeout=10.0,
        )

        assert response.status_code == 200
        result = response.json()

        # Verify task result structure
        assert "artifacts" in result
        assert len(result["artifacts"]) > 0

        # Extract evaluation result
        artifact = result["artifacts"][0]
        assert "parts" in artifact
        evaluation_text = artifact["parts"][0]["text"]

        # Parse evaluation JSON
        evaluation = json.loads(evaluation_text)

        # Verify structured output
        assert "risk_score" in evaluation
        assert "classification" in evaluation
        assert "component_scores" in evaluation
        assert "redline" in evaluation

    @pytest.mark.integration
    def test_green_agent_returns_structured_output(self, green_agent_url):
        """Test green agent returns structured output with all required fields."""
        test_narrative = "We debugged bugs and performed routine maintenance on production systems."

        task_payload = {
            "context_id": "test-green-002",
            "input": {
                "parts": [{"text": test_narrative}]
            },
        }

        response = httpx.post(
            f"{green_agent_url}/task/send",
            json=task_payload,
            timeout=10.0,
        )

        assert response.status_code == 200
        result = response.json()

        # Extract and parse evaluation
        evaluation_text = result["artifacts"][0]["parts"][0]["text"]
        evaluation = json.loads(evaluation_text)

        # Verify risk_score
        assert isinstance(evaluation["risk_score"], int)
        assert 0 <= evaluation["risk_score"] <= 100

        # Verify classification
        assert evaluation["classification"] in ["QUALIFYING", "NON_QUALIFYING"]

        # Verify component_scores
        assert isinstance(evaluation["component_scores"], dict)
        assert "routine_engineering" in evaluation["component_scores"]
        assert "vagueness" in evaluation["component_scores"]
        assert "business_risk" in evaluation["component_scores"]
        assert "experimentation" in evaluation["component_scores"]
        assert "specificity" in evaluation["component_scores"]

        # Verify redline
        assert isinstance(evaluation["redline"], dict)

    @pytest.mark.integration
    def test_green_agent_exposes_agent_card(self, green_agent_url):
        """Test green agent exposes AgentCard at /.well-known/agent-card.json."""
        response = httpx.get(
            f"{green_agent_url}/.well-known/agent-card.json",
            timeout=5.0,
        )

        assert response.status_code == 200

        agent_card = response.json()
        assert "name" in agent_card
        assert agent_card["name"] == "bulletproof-green-examiner"
        assert "description" in agent_card
        assert "IRS Section 41 Evaluator" in agent_card["description"]

    @pytest.mark.integration
    def test_green_agent_evaluates_qualifying_narrative(self, green_agent_url):
        """Test green agent classifies qualifying narrative correctly."""
        # High-quality qualifying narrative
        qualifying_narrative = """
        We researched novel algorithms facing technical uncertainty in real-time data processing.
        We reduced latency from 100ms to 3.2ms through systematic experimentation.
        We tested multiple alternatives including streaming quantiles and adaptive thresholds.
        We documented failed approaches when fixed-window aggregation proved unsuccessful.
        """

        task_payload = {
            "context_id": "test-green-qualifying",
            "input": {
                "parts": [{"text": qualifying_narrative}]
            },
        }

        response = httpx.post(
            f"{green_agent_url}/task/send",
            json=task_payload,
            timeout=10.0,
        )

        assert response.status_code == 200
        result = response.json()

        evaluation_text = result["artifacts"][0]["parts"][0]["text"]
        evaluation = json.loads(evaluation_text)

        # Should be classified as QUALIFYING (low risk)
        assert evaluation["risk_score"] < 20
        assert evaluation["classification"] == "QUALIFYING"

    @pytest.mark.integration
    def test_green_agent_evaluates_non_qualifying_narrative(self, green_agent_url):
        """Test green agent classifies non-qualifying narrative correctly."""
        # Routine engineering narrative
        non_qualifying_narrative = """
        We fixed bugs in the production system and performed routine maintenance.
        We debugged issues and optimized performance to improve user experience.
        We upgraded the system and enhanced the codebase through refactoring.
        Overall, we made the system better and faster.
        """

        task_payload = {
            "context_id": "test-green-non-qualifying",
            "input": {
                "parts": [{"text": non_qualifying_narrative}]
            },
        }

        response = httpx.post(
            f"{green_agent_url}/task/send",
            json=task_payload,
            timeout=10.0,
        )

        assert response.status_code == 200
        result = response.json()

        evaluation_text = result["artifacts"][0]["parts"][0]["text"]
        evaluation = json.loads(evaluation_text)

        # Should be classified as NON_QUALIFYING (high risk)
        assert evaluation["risk_score"] >= 20
        assert evaluation["classification"] == "NON_QUALIFYING"
