"""Tests for Green Agent A2A server (STORY-005).

This test module validates the acceptance criteria for STORY-005:
- A2A server on port 8000
- AgentCard at /.well-known/agent-card.json
- Exposes message/send method for receiving narratives
- Returns score in DataPart format
- Integrates evaluator and scorer
- Proper error handling and timeout management
- Python 3.13, a2a-sdk>=0.3.20, uvicorn>=0.38.0
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from bulletproof_green.server import create_app, get_agent_card


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


def make_data_request(data: dict, req_id: str = "test-1") -> dict:
    """Create a message/send request with DataPart containing narrative.

    Args:
        data: The data dict to include in the request.
        req_id: The JSON-RPC request ID.

    Returns:
        A valid message/send JSON-RPC request dict with DataPart.
    """
    return {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": req_id,
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"data": data}],
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
            assert data["name"] == "Bulletproof Green Agent"

    @pytest.mark.asyncio
    async def test_agent_card_has_evaluate_narrative_skill(self):
        """Test AgentCard advertises narrative evaluation capability."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()

            skills = data.get("skills", [])
            skill_ids = [s.get("id") for s in skills]
            assert "evaluate_narrative" in skill_ids

    def test_get_agent_card_returns_agent_card_object(self):
        """Test get_agent_card helper returns AgentCard."""
        card = get_agent_card()
        assert card is not None
        assert card.name == "Bulletproof Green Agent"


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
                "/", json=make_message_send_request("Evaluate this narrative")
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
                "/", json=make_message_send_request("Evaluate this narrative")
            )
            data = response.json()
            # Must have either result or error
            assert "result" in data or "error" in data

    @pytest.mark.asyncio
    async def test_message_send_evaluates_narrative(self):
        """Test message/send evaluates narrative and returns response."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("This is a test narrative to evaluate.")
            )
            data = response.json()
            assert "result" in data


class TestDataPartResponse:
    """Test evaluation returns in DataPart format."""

    @pytest.mark.asyncio
    async def test_response_contains_message_with_parts(self):
        """Test response contains message with parts array."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/", json=make_message_send_request("Evaluate narrative"))
            data = response.json()
            if "result" in data:
                result = data["result"]
                # Result should be a Message or Task with parts
                assert "parts" in result or "status" in result

    @pytest.mark.asyncio
    async def test_response_includes_data_part_with_scores(self):
        """Test response includes DataPart containing score data."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("This narrative describes our R&D work.")
            )
            data = response.json()
            if "result" in data:
                result = data["result"]
                if "parts" in result:
                    parts = result["parts"]
                    # Should have at least one part with data
                    has_data_or_text = any("data" in p or "text" in p for p in parts)
                    assert has_data_or_text


class TestEvaluatorScorerIntegration:
    """Test integration of evaluator and scorer."""

    @pytest.mark.asyncio
    async def test_response_contains_overall_score(self):
        """Test response contains overall_score from scorer."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Send a narrative to evaluate
            response = await client.post(
                "/",
                json=make_message_send_request(
                    "Our hypothesis was that by using a novel algorithm we could "
                    "reduce latency from 500ms to under 100ms. After 15 experiments "
                    "and 8 failures, we achieved 45ms latency."
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            # Find the DataPart with scores in AgentBeats format
            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        assert "score" in score_data
                        assert "max_score" in score_data
                        # Score should be in 0 to max_score range
                        assert 0 <= score_data["score"] <= score_data["max_score"]

    @pytest.mark.asyncio
    async def test_response_contains_agentbeats_fields(self):
        """Test response contains all AgentBeats required fields."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_message_send_request(
                    "We investigated whether our caching approach could achieve "
                    "sub-millisecond response times. Initial attempts failed due to "
                    "cache invalidation complexity. After iterating through 5 different "
                    "strategies we achieved 0.8ms average latency."
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        # Check for AgentBeats required fields
                        assert "domain" in score_data
                        assert "score" in score_data
                        assert "max_score" in score_data
                        assert "pass_rate" in score_data
                        assert "task_rewards" in score_data

    @pytest.mark.asyncio
    async def test_response_contains_task_rewards(self):
        """Test response contains task_rewards with component scores."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/", json=make_message_send_request("Sample narrative for evaluation.")
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        # Should contain task_rewards with 4 component tasks
                        assert "task_rewards" in score_data
                        task_rewards = score_data["task_rewards"]
                        assert "0" in task_rewards  # correctness
                        assert "1" in task_rewards  # safety
                        assert "2" in task_rewards  # specificity
                        assert "3" in task_rewards  # experimentation

    @pytest.mark.asyncio
    async def test_qualifying_narrative_gets_high_pass_rate(self):
        """Test a qualifying narrative gets high pass_rate."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # A well-structured qualifying narrative
            qualifying_narrative = (
                "Our hypothesis was that using a custom B-tree implementation could "
                "reduce database query times from 200ms to under 50ms. We were uncertain "
                "whether memory constraints would allow this optimization. "
                "We conducted 12 experiments testing different node sizes. "
                "Initial attempts with 4KB nodes failed due to cache misses. "
                "After 6 iterations, we discovered that 16KB nodes with prefetching "
                "achieved 35ms query times, a 5.7x improvement. "
                "The technical uncertainty was whether we could maintain ACID guarantees "
                "while achieving this performance target."
            )
            response = await client.post("/", json=make_message_send_request(qualifying_narrative))
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        # Qualifying narratives should have high pass_rate (>50%)
                        assert score_data["pass_rate"] > 50
                        assert score_data["domain"] == "irs-r&d"

    @pytest.mark.asyncio
    async def test_non_qualifying_narrative_gets_low_pass_rate(self):
        """Test a non-qualifying narrative gets low pass_rate."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # A non-qualifying narrative with routine engineering
            non_qualifying_narrative = (
                "We did routine maintenance on our database. "
                "We fixed bugs and applied patches from the vendor. "
                "The migration went smoothly with predictable outcomes. "
                "Sales growth was significant and market share improved greatly."
            )
            response = await client.post(
                "/", json=make_message_send_request(non_qualifying_narrative)
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        # Non-qualifying narratives should have low pass_rate (<=50%)
                        assert score_data["pass_rate"] <= 50
                        assert score_data["domain"] == "irs-r&d"


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
