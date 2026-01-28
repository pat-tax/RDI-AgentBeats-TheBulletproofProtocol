"""Tests for A2A client module (STORY-006).

This test module validates the acceptance criteria for STORY-006:
- A2A client module with task send/receive
- Discovers Purple Agent via agent-card.json
- Sends narrative requests with context
- Receives narrative responses
- Handles task lifecycle (pending -> running -> completed)
- Timeout and error handling
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestA2AClientImport:
    """Test A2A client module can be imported."""

    def test_a2a_client_module_exists(self):
        """Test a2a_client module can be imported."""
        from bulletproof_green import a2a_client

        assert a2a_client is not None

    def test_a2a_client_class_exists(self):
        """Test A2AClient class exists."""
        from bulletproof_green.a2a_client import A2AClient

        assert A2AClient is not None

    def test_narrative_request_class_exists(self):
        """Test NarrativeRequest dataclass exists."""
        from bulletproof_green.a2a_client import NarrativeRequest

        assert NarrativeRequest is not None

    def test_narrative_response_class_exists(self):
        """Test NarrativeResponse dataclass exists."""
        from bulletproof_green.a2a_client import NarrativeResponse

        assert NarrativeResponse is not None


class TestA2AClientConstruction:
    """Test A2A client construction."""

    def test_client_accepts_base_url(self):
        """Test client can be constructed with base URL."""
        from bulletproof_green.a2a_client import A2AClient

        client = A2AClient(base_url="http://localhost:8001")
        assert client.base_url == "http://localhost:8001"

    def test_client_has_default_timeout(self):
        """Test client has default timeout configuration."""
        from bulletproof_green.a2a_client import A2AClient

        client = A2AClient(base_url="http://localhost:8001")
        assert client.timeout == 300  # Default 300 seconds

    def test_client_accepts_custom_timeout(self):
        """Test client accepts custom timeout."""
        from bulletproof_green.a2a_client import A2AClient

        client = A2AClient(base_url="http://localhost:8001", timeout=60)
        assert client.timeout == 60


class TestAgentCardDiscovery:
    """Test Purple Agent discovery via agent-card.json."""

    @pytest.mark.asyncio
    async def test_discover_returns_agent_card(self):
        """Test discover method retrieves agent card."""
        from bulletproof_green.a2a_client import A2AClient

        client = A2AClient(base_url="http://localhost:8001")

        # Mock the HTTP response
        mock_card_data = {
            "name": "Bulletproof Purple Agent",
            "description": "IRS Section 41 narrative generator",
            "url": "http://localhost:8001",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "skills": [{"id": "generate_narrative", "name": "Generate Narrative"}],
        }

        with patch.object(client, "_fetch_agent_card", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_card_data
            card = await client.discover()

            assert card is not None
            assert card["name"] == "Bulletproof Purple Agent"

    @pytest.mark.asyncio
    async def test_discover_fetches_from_well_known_endpoint(self):
        """Test discover fetches from /.well-known/agent-card.json."""
        from bulletproof_green.a2a_client import A2AClient

        client = A2AClient(base_url="http://localhost:8001")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"name": "Test Agent"}
            mock_client.get.return_value = mock_response

            await client.discover()

            # Should fetch from well-known endpoint
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "/.well-known/agent-card.json" in str(call_args)

    @pytest.mark.asyncio
    async def test_discover_caches_agent_card(self):
        """Test agent card is cached after discovery."""
        from bulletproof_green.a2a_client import A2AClient

        client = A2AClient(base_url="http://localhost:8001")

        mock_card = {"name": "Test Agent"}
        with patch.object(client, "_fetch_agent_card", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_card

            # First call
            await client.discover()
            # Second call should use cache
            await client.discover()

            # Should only fetch once due to caching
            assert mock_fetch.call_count == 1


class TestNarrativeRequest:
    """Test NarrativeRequest dataclass."""

    def test_narrative_request_has_template_type(self):
        """Test NarrativeRequest has template_type field."""
        from bulletproof_green.a2a_client import NarrativeRequest

        request = NarrativeRequest(template_type="qualifying")
        assert request.template_type == "qualifying"

    def test_narrative_request_has_optional_signals(self):
        """Test NarrativeRequest has optional signals field."""
        from bulletproof_green.a2a_client import NarrativeRequest

        signals = {"project": "test", "metrics": {"latency": 100}}
        request = NarrativeRequest(template_type="qualifying", signals=signals)
        assert request.signals == signals

    def test_narrative_request_has_optional_context(self):
        """Test NarrativeRequest has optional context field."""
        from bulletproof_green.a2a_client import NarrativeRequest

        request = NarrativeRequest(template_type="qualifying", context="Additional context")
        assert request.context == "Additional context"


class TestNarrativeResponse:
    """Test NarrativeResponse dataclass."""

    def test_narrative_response_has_narrative(self):
        """Test NarrativeResponse has narrative field."""
        from bulletproof_green.a2a_client import NarrativeResponse

        response = NarrativeResponse(narrative="Test narrative text")
        assert response.narrative == "Test narrative text"

    def test_narrative_response_has_optional_metadata(self):
        """Test NarrativeResponse has optional metadata field."""
        from bulletproof_green.a2a_client import NarrativeResponse

        metadata = {"word_count": 500, "template_type": "qualifying"}
        response = NarrativeResponse(narrative="Test", metadata=metadata)
        assert response.metadata == metadata

    def test_narrative_response_has_task_id(self):
        """Test NarrativeResponse includes task_id."""
        from bulletproof_green.a2a_client import NarrativeResponse

        task_id = str(uuid.uuid4())
        response = NarrativeResponse(narrative="Test", task_id=task_id)
        assert response.task_id == task_id


class TestSendNarrativeRequest:
    """Test sending narrative requests to Purple Agent."""

    @pytest.mark.asyncio
    async def test_send_request_returns_response(self):
        """Test send_request returns NarrativeResponse."""
        from bulletproof_green.a2a_client import A2AClient, NarrativeRequest, NarrativeResponse

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "result": {
                "parts": [
                    {
                        "data": {
                            "narrative": "Generated narrative text",
                            "metadata": {"template_type": "qualifying"},
                        }
                    }
                ]
            },
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            response = await client.send_request(request)

            assert isinstance(response, NarrativeResponse)
            assert response.narrative == "Generated narrative text"

    @pytest.mark.asyncio
    async def test_send_request_includes_context(self):
        """Test send_request includes context in message."""
        from bulletproof_green.a2a_client import A2AClient, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(
            template_type="qualifying", context="Generate a narrative about caching"
        )

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {
                "jsonrpc": "2.0",
                "id": "test-1",
                "result": {"parts": [{"data": {"narrative": "Test"}}]},
            }
            await client.send_request(request)

            # Check that the request included context
            call_args = mock_send.call_args
            assert call_args is not None
            params = call_args[0][1]  # Second positional arg is params
            assert "message" in params

    @pytest.mark.asyncio
    async def test_send_request_uses_message_send_method(self):
        """Test send_request uses message/send JSON-RPC method."""
        from bulletproof_green.a2a_client import A2AClient, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {
                "jsonrpc": "2.0",
                "id": "test-1",
                "result": {"parts": [{"data": {"narrative": "Test"}}]},
            }
            await client.send_request(request)

            # Check that message/send method was used
            call_args = mock_send.call_args
            method = call_args[0][0]  # First positional arg is method
            assert method == "message/send"


class TestTaskLifecycle:
    """Test task lifecycle handling (pending -> running -> completed)."""

    @pytest.mark.asyncio
    async def test_task_status_pending_to_working(self):
        """Test client handles task transitioning from pending to working."""
        from bulletproof_green.a2a_client import A2AClient, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        # Response with task in working state
        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "result": {
                "status": {"state": "working"},
                "id": "task-123",
            },
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            # Should poll for completion
            with patch.object(client, "_poll_task", new_callable=AsyncMock) as mock_poll:
                mock_poll.return_value = {"parts": [{"data": {"narrative": "Final narrative"}}]}
                response = await client.send_request(request)
                assert response.narrative == "Final narrative"

    @pytest.mark.asyncio
    async def test_task_status_completed(self):
        """Test client handles completed task status."""
        from bulletproof_green.a2a_client import A2AClient, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        # Response with completed task
        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "result": {
                "parts": [{"data": {"narrative": "Completed narrative"}}],
            },
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            response = await client.send_request(request)
            assert response.narrative == "Completed narrative"

    @pytest.mark.asyncio
    async def test_task_status_failed(self):
        """Test client handles failed task status."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        # Response with failed task
        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "result": {
                "status": {"state": "failed"},
                "id": "task-123",
            },
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            with pytest.raises(A2AClientError):
                await client.send_request(request)


class TestTimeoutHandling:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_request_timeout(self):
        """Test request raises timeout error when exceeded."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001", timeout=1)
        request = NarrativeRequest(template_type="qualifying")

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:

            mock_send.side_effect = TimeoutError()

            with pytest.raises(A2AClientError) as exc_info:
                await client.send_request(request)
            assert "timeout" in str(exc_info.value).lower()


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test client handles connection errors gracefully."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:9999")  # Invalid port
        request = NarrativeRequest(template_type="qualifying")

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = ConnectionError("Connection refused")

            with pytest.raises(A2AClientError) as exc_info:
                await client.send_request(request)
            assert "connection" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_jsonrpc_error_response(self):
        """Test client handles JSON-RPC error responses."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "error": {"code": -32600, "message": "Invalid Request"},
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response

            with pytest.raises(A2AClientError) as exc_info:
                await client.send_request(request)
            assert "Invalid Request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_response_format(self):
        """Test client handles invalid response format."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        # Response missing required fields
        mock_response = {"jsonrpc": "2.0", "id": "test-1", "result": {}}

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response

            with pytest.raises(A2AClientError):
                await client.send_request(request)


class TestA2AClientExport:
    """Test A2A client is properly exported from module."""

    def test_a2a_client_exported_from_green_module(self):
        """Test A2AClient is exported from bulletproof_green module."""
        from bulletproof_green import A2AClient

        assert A2AClient is not None

    def test_narrative_request_exported(self):
        """Test NarrativeRequest is exported from bulletproof_green module."""
        from bulletproof_green import NarrativeRequest

        assert NarrativeRequest is not None

    def test_narrative_response_exported(self):
        """Test NarrativeResponse is exported from bulletproof_green module."""
        from bulletproof_green import NarrativeResponse

        assert NarrativeResponse is not None

    def test_a2a_client_error_exported(self):
        """Test A2AClientError is exported from bulletproof_green module."""
        from bulletproof_green import A2AClientError

        assert A2AClientError is not None
