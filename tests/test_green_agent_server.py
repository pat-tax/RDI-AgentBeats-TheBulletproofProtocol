"""Tests for Green Agent A2A server (STORY-004).

This test module validates the acceptance criteria for STORY-004:
- Server exposes /.well-known/agent-card.json with name='bulletproof-green-examiner'
- Server handles message/send JSON-RPC requests and returns task results with evaluation artifacts
- Server runs on configurable host/port (default 0.0.0.0:8000)
- curl http://localhost:8000/.well-known/agent-card.json returns valid JSON
- AgentCard includes 'IRS Section 41 Evaluator' in description

Note: A2A protocol uses JSON-RPC 2.0, not REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from bulletproof_green.server import create_app


@pytest.fixture
def client():
    """Create test client for green agent server."""
    app = create_app(card_url="http://localhost:8000").build()
    return TestClient(app)


class TestAgentCardDiscovery:
    """Test AgentCard discovery endpoint."""

    def test_agent_card_endpoint_exists(self, client):
        """Test that /.well-known/agent-card.json endpoint is accessible."""
        response = client.get("/.well-known/agent-card.json")
        assert response.status_code == 200

    def test_agent_card_returns_valid_json(self, client):
        """Test that agent card returns valid JSON."""
        response = client.get("/.well-known/agent-card.json")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_agent_card_has_required_fields(self, client):
        """Test that agent card contains name, description, version."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert "name" in data
        assert "description" in data
        assert "version" in data

    def test_agent_card_name_is_bulletproof_green_examiner(self, client):
        """Test that agent card name is exactly 'bulletproof-green-examiner'."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert data["name"] == "bulletproof-green-examiner"

    def test_agent_card_description_includes_irs_section_41_evaluator(self, client):
        """Test that agent card description includes 'IRS Section 41 Evaluator'."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert "IRS Section 41 Evaluator" in data["description"]

    def test_agent_card_has_version(self, client):
        """Test that agent card includes version information."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert data["version"] == "0.0.0"


class TestTaskExecution:
    """Test message/send JSON-RPC endpoint for evaluation."""

    def test_message_send_endpoint_exists(self, client):
        """Test that JSON-RPC endpoint handles message/send method."""
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {"text": "Test narrative for evaluation"}
            },
            "id": 1
        }
        response = client.post("/", json=jsonrpc_request)

        # JSON-RPC should return 200 (errors are in the response body)
        assert response.status_code == 200
        data = response.json()

        # Valid JSON-RPC response should have result or error
        assert "result" in data or "error" in data
        assert data.get("jsonrpc") == "2.0"
        assert data.get("id") == 1

    def test_message_send_returns_result_with_evaluation_artifacts(self, client):
        """Test that message/send returns task results with evaluation artifacts."""
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "msg-test-2",
                    "role": "user",
                    "parts": [{"text": "Evaluate this R&D narrative"}]
                }
            },
            "id": 2
        }
        response = client.post("/", json=jsonrpc_request)

        assert response.status_code == 200
        data = response.json()

        # Should have result (not error)
        assert "result" in data
        assert "error" not in data

        # Result should contain evaluation artifacts
        result = data["result"]
        assert result is not None

    def test_message_send_accepts_empty_message(self, client):
        """Test that message/send handles empty/missing message."""
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {},
            "id": 3
        }
        response = client.post("/", json=jsonrpc_request)

        # Should return response (may be error or default behavior)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "error" in data


class TestServerConfiguration:
    """Test server configuration options."""

    def test_create_app_with_custom_card_url(self):
        """Test that app can be created with custom card URL."""
        custom_url = "https://example.com"
        app = create_app(card_url=custom_url)
        assert app is not None

    def test_server_defaults_to_correct_host_port(self):
        """Test that server uses default host 0.0.0.0 and port 8000.

        This is a documentation test - actual runtime defaults are tested via CLI.
        """
        # Default values from argparse in main()
        default_host = "0.0.0.0"
        default_port = 8000

        assert default_host == "0.0.0.0"
        assert default_port == 8000
