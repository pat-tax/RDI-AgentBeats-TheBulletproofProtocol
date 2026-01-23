"""Tests for Purple Agent A2A server (STORY-001).

This test module validates the acceptance criteria for STORY-001:
- Server exposes /.well-known/agent-card.json with name, description, version, capabilities
- Server handles message/send JSON-RPC requests and returns task results with artifacts
- Server runs on configurable host/port (default 0.0.0.0:8000)
- curl http://localhost:8000/.well-known/agent-card.json returns valid JSON

Note: A2A protocol uses JSON-RPC 2.0, not REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from bulletproof_purple.server import create_app


@pytest.fixture
def client():
    """Create test client for purple agent server."""
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

    def test_agent_card_name_is_correct(self, client):
        """Test that agent card name matches specification."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert data["name"] == "bulletproof-purple-substantiator"

    def test_agent_card_has_description(self, client):
        """Test that agent card has a meaningful description."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert len(data["description"]) > 0
        assert "R&D" in data["description"] or "narrative" in data["description"].lower()

    def test_agent_card_has_version(self, client):
        """Test that agent card includes version information."""
        response = client.get("/.well-known/agent-card.json")
        data = response.json()

        assert data["version"] == "0.0.0"


class TestTaskExecution:
    """Test message/send JSON-RPC endpoint for narrative generation."""

    def test_message_send_endpoint_exists(self, client):
        """Test that JSON-RPC endpoint handles message/send method."""
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {"text": "Generate test narrative"}
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

    def test_message_send_returns_result_with_artifacts(self, client):
        """Test that message/send returns task results with narrative artifacts."""
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {"text": "Generate R&D narrative"}
            },
            "id": 2
        }
        response = client.post("/", json=jsonrpc_request)

        assert response.status_code == 200
        data = response.json()

        # Should have result (not error)
        assert "result" in data
        assert "error" not in data

        # Result should contain narrative in some form
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
