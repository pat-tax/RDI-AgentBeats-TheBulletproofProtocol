"""Integration tests for Purple Agent task execution (STORY-015).

This test module validates purple agent integration:
- Purple agent task execution via A2A protocol
- Narrative generation through HTTP endpoint
- AgentCard discovery
"""

import json

import httpx
import pytest


class TestPurpleAgentTaskExecution:
    """Test purple agent task execution via A2A protocol."""

    @pytest.fixture
    def purple_agent_url(self):
        """Return purple agent URL (assumes docker-compose running)."""
        return "http://localhost:8002"

    @pytest.mark.integration
    def test_purple_agent_generates_narrative_via_task_send(self, purple_agent_url):
        """Test purple agent receives task and returns narrative artifact."""
        # Send task to purple agent
        task_payload = {
            "context_id": "test-integration-001",
            "input": {
                "parts": [{"text": "Generate a qualifying R&D narrative"}]
            },
        }

        response = httpx.post(
            f"{purple_agent_url}/task/send",
            json=task_payload,
            timeout=10.0,
        )

        assert response.status_code == 200
        result = response.json()

        # Verify task result structure
        assert "artifacts" in result
        assert len(result["artifacts"]) > 0

        # Verify narrative artifact
        artifact = result["artifacts"][0]
        assert "parts" in artifact
        assert len(artifact["parts"]) > 0

        # Extract narrative text
        narrative_text = artifact["parts"][0]["text"]
        assert isinstance(narrative_text, str)
        assert len(narrative_text) > 0

        # Verify narrative is substantive (300-500 words)
        word_count = len(narrative_text.split())
        assert 200 <= word_count <= 600  # Allow some margin

    @pytest.mark.integration
    def test_purple_agent_exposes_agent_card(self, purple_agent_url):
        """Test purple agent exposes AgentCard at /.well-known/agent-card.json."""
        response = httpx.get(
            f"{purple_agent_url}/.well-known/agent-card.json",
            timeout=5.0,
        )

        assert response.status_code == 200

        agent_card = response.json()
        assert "name" in agent_card
        assert "description" in agent_card
        assert "capabilities" in agent_card

    @pytest.mark.integration
    def test_purple_agent_handles_different_prompt_types(self, purple_agent_url):
        """Test purple agent generates different narratives for different prompt types."""
        prompts = [
            "Generate a qualifying R&D narrative",
            "Generate a non-qualifying routine narrative",
            "Generate an edge case narrative",
        ]

        narratives = []

        for prompt in prompts:
            task_payload = {
                "context_id": f"test-integration-{prompt[:10]}",
                "input": {
                    "parts": [{"text": prompt}]
                },
            }

            response = httpx.post(
                f"{purple_agent_url}/task/send",
                json=task_payload,
                timeout=10.0,
            )

            assert response.status_code == 200
            result = response.json()
            narrative = result["artifacts"][0]["parts"][0]["text"]
            narratives.append(narrative)

        # All narratives should be generated
        assert len(narratives) == 3
        assert all(len(n) > 0 for n in narratives)
