"""Tests for A2A client module (STORY-006).

Validates core behavior:
- Discovers Purple Agent via agent-card.json
- Sends narrative requests via JSON-RPC
- Handles task lifecycle and errors
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAgentCardDiscovery:
    """Test Purple Agent discovery via agent-card.json."""

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

            await client.discover()
            await client.discover()

            assert mock_fetch.call_count == 1


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
                "parts": [{"data": {"narrative": "Generated text", "metadata": {}}}]
            },
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            response = await client.send_request(request)

            assert isinstance(response, NarrativeResponse)
            assert response.narrative == "Generated text"

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

            method = mock_send.call_args[0][0]
            assert method == "message/send"


class TestTaskLifecycle:
    """Test task lifecycle handling."""

    @pytest.mark.asyncio
    async def test_handles_task_in_working_state(self):
        """Test client polls for completion when task is in working state."""
        from bulletproof_green.a2a_client import A2AClient, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "result": {"status": {"state": "working"}, "id": "task-123"},
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            with patch.object(client, "_poll_task", new_callable=AsyncMock) as mock_poll:
                mock_poll.return_value = {"parts": [{"data": {"narrative": "Final"}}]}
                response = await client.send_request(request)
                assert response.narrative == "Final"

    @pytest.mark.asyncio
    async def test_handles_failed_task(self):
        """Test client raises error for failed task."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001")
        request = NarrativeRequest(template_type="qualifying")

        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "result": {"status": {"state": "failed"}, "id": "task-123"},
        }

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            with pytest.raises(A2AClientError):
                await client.send_request(request)


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_handles_timeout(self):
        """Test request raises timeout error when exceeded."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:8001", timeout=1)
        request = NarrativeRequest(template_type="qualifying")

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = TimeoutError()

            with pytest.raises(A2AClientError) as exc_info:
                await client.send_request(request)
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_handles_connection_error(self):
        """Test client handles connection errors gracefully."""
        from bulletproof_green.a2a_client import A2AClient, A2AClientError, NarrativeRequest

        client = A2AClient(base_url="http://localhost:9999")
        request = NarrativeRequest(template_type="qualifying")

        with patch.object(client, "_send_jsonrpc", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = ConnectionError("Connection refused")

            with pytest.raises(A2AClientError) as exc_info:
                await client.send_request(request)
            assert "connection" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_handles_jsonrpc_error(self):
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
