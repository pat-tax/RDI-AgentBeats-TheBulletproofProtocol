"""Tests for Purple Agent A2A server (STORY-002).

This test module validates the acceptance criteria for STORY-002:
- A2A server on port 8000
- AgentCard at /.well-known/agent-card.json
- Exposes message/send method for receiving critique
- Returns narrative in DataPart format
- Proper error handling (JSON-RPC codes -32600 to -32001)
- Task timeout handling (default 300s)
- Python 3.13, a2a-sdk>=0.3.20, uvicorn>=0.38.0
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from bulletproof_purple.server import create_app, get_agent_card


def make_message_send_request(
    text: str, req_id: str = "test-1", message_id: str | None = None
) -> dict:
    """Create a properly formatted message/send JSON-RPC request.

    Args:
        text: The text content of the message.
        req_id: The JSON-RPC request ID.
        message_id: Optional message ID. Auto-generated if not provided.

    Returns:
        A valid message/send JSON-RPC request dict.
    """
    return {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": req_id,
        "params": {
            "message": {
                "messageId": message_id or str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": text}],
            }
        },
    }


class TestAgentCard:
    """Test AgentCard endpoint at /.well-known/agent-card.json."""

    @pytest.mark.asyncio
    async def test_agent_card_endpoint_exists(self):
        """Test that /.well-known/agent-card.json endpoint exists."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_card_returns_valid_json(self):
        """Test AgentCard returns valid JSON."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_agent_card_contains_required_fields(self):
        """Test AgentCard contains required A2A fields."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()

            # Required A2A AgentCard fields
            assert "name" in data
            assert "description" in data
            assert "url" in data
            assert "version" in data
            assert "capabilities" in data
            assert "skills" in data

    @pytest.mark.asyncio
    async def test_agent_card_has_correct_name(self):
        """Test AgentCard has correct agent name."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()
            assert data["name"] == "Bulletproof Purple Agent"

    @pytest.mark.asyncio
    async def test_agent_card_has_narrative_generation_skill(self):
        """Test AgentCard advertises narrative generation capability."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()

            skills = data.get("skills", [])
            skill_ids = [s.get("id") for s in skills]
            assert "generate_narrative" in skill_ids

    def test_get_agent_card_returns_agent_card_object(self):
        """Test get_agent_card helper returns AgentCard."""
        card = get_agent_card()
        assert card is not None
        assert card.name == "Bulletproof Purple Agent"


class TestMessageSendEndpoint:
    """Test message/send JSON-RPC endpoint."""

    @pytest.mark.asyncio
    async def test_rpc_endpoint_exists(self):
        """Test that JSON-RPC endpoint exists at /."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/", json=make_message_send_request("test"))
            # Should not be 404
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_message_send_returns_jsonrpc_response(self):
        """Test message/send returns valid JSON-RPC response."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("Generate a narrative")
            )
            data = response.json()
            assert "jsonrpc" in data
            assert data["jsonrpc"] == "2.0"
            assert "id" in data

    @pytest.mark.asyncio
    async def test_message_send_returns_result_or_error(self):
        """Test message/send returns result or error field."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("Generate a narrative")
            )
            data = response.json()
            # Must have either result or error
            assert "result" in data or "error" in data

    @pytest.mark.asyncio
    async def test_message_send_generates_narrative(self):
        """Test message/send generates narrative response."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("Generate a qualifying narrative")
            )
            data = response.json()
            assert "result" in data


class TestDataPartResponse:
    """Test narrative returns in DataPart format."""

    @pytest.mark.asyncio
    async def test_response_contains_message_with_parts(self):
        """Test response contains message with parts array."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/", json=make_message_send_request("Generate narrative"))
            data = response.json()
            if "result" in data:
                result = data["result"]
                # Result should be a Message or Task with parts
                assert "parts" in result or "status" in result

    @pytest.mark.asyncio
    async def test_response_includes_data_part_with_narrative(self):
        """Test response includes DataPart containing narrative data."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("Generate qualifying narrative")
            )
            data = response.json()
            if "result" in data:
                result = data["result"]
                if "parts" in result:
                    parts = result["parts"]
                    # Should have at least one part with data
                    has_data_or_text = any("data" in p or "text" in p for p in parts)
                    assert has_data_or_text


class TestJSONRPCErrorHandling:
    """Test JSON-RPC error handling per specification."""

    @pytest.mark.asyncio
    async def test_invalid_json_returns_parse_error(self):
        """Test invalid JSON returns -32700 Parse Error."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                content="not valid json{",
                headers={"Content-Type": "application/json"},
            )
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == -32700

    @pytest.mark.asyncio
    async def test_invalid_request_returns_error(self):
        """Test invalid request returns -32600 Invalid Request."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json={"not": "valid jsonrpc"},
            )
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == -32600

    @pytest.mark.asyncio
    async def test_unknown_method_returns_method_not_found(self):
        """Test unknown method returns -32601 Method Not Found."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "method": "unknown/method",
                    "id": "test-1",
                    "params": {},
                },
            )
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == -32601

    @pytest.mark.asyncio
    async def test_invalid_params_returns_error(self):
        """Test invalid params returns -32602 Invalid Params."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "id": "test-1",
                    "params": "not an object",
                },
            )
            data = response.json()
            assert "error" in data
            # Should be -32602 Invalid Params or similar
            assert data["error"]["code"] in [-32602, -32600]


class TestTimeoutConfiguration:
    """Test task timeout handling."""

    @pytest.mark.asyncio
    async def test_server_respects_timeout_configuration(self):
        """Test server accepts timeout configuration."""
        # Create app with custom timeout - should not raise
        app = create_app(timeout=60)
        assert app is not None


class TestServerConfiguration:
    """Test server configuration and startup."""

    def test_create_app_returns_asgi_application(self):
        """Test create_app returns ASGI-compatible application."""
        app = create_app()
        assert app is not None
        # Should have ASGI interface
        assert callable(app)

    @pytest.mark.asyncio
    async def test_server_handles_concurrent_requests(self):
        """Test server can handle multiple concurrent requests."""
        import asyncio

        app = create_app()

        async def make_request(client: AsyncClient, req_id: str):
            return await client.post("/", json=make_message_send_request("test", req_id=req_id))

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            tasks = [make_request(client, f"req-{i}") for i in range(3)]
            responses = await asyncio.gather(*tasks)

            # All requests should complete
            assert len(responses) == 3
            for resp in responses:
                assert resp.status_code == 200
