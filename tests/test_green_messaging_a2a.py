"""Tests for messenger.py module (STORY-022).

Validates core behavior:
- create_message() constructs valid A2A messages
- send_message() sends HTTP POST with JSON-RPC format
- Messenger class provides high-level API
- Error handling for timeouts and connection issues
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCreateMessage:
    """Test create_message() function for A2A message construction."""

    def test_creates_message_with_text(self):
        """Test create_message creates valid A2A message with text."""
        from bulletproof_green.messenger import create_message

        message = create_message(text="Please generate a narrative")

        assert "messageId" in message
        assert message["role"] == "user"
        assert message["parts"][0]["text"] == "Please generate a narrative"

    def test_creates_message_with_data(self):
        """Test create_message creates valid A2A message with data."""
        from bulletproof_green.messenger import create_message

        data = {"template_type": "qualifying"}
        message = create_message(data=data)

        assert message["parts"][0]["data"] == data

    def test_creates_message_with_text_and_data(self):
        """Test create_message creates valid A2A message with both."""
        from bulletproof_green.messenger import create_message

        message = create_message(text="Generate", data={"template_type": "qualifying"})

        assert len(message["parts"]) == 2

    def test_generates_unique_ids(self):
        """Test create_message generates unique message IDs."""
        from bulletproof_green.messenger import create_message

        msg1 = create_message(text="test1")
        msg2 = create_message(text="test2")

        assert msg1["messageId"] != msg2["messageId"]
        uuid.UUID(msg1["messageId"])  # Validates UUID format


class TestSendMessage:
    """Test send_message() function for HTTP POST."""

    @pytest.mark.asyncio
    async def test_sends_jsonrpc_format(self):
        """Test send_message wraps message in JSON-RPC 2.0 format."""
        from bulletproof_green.messenger import send_message

        message = {"messageId": str(uuid.uuid4()), "role": "user", "parts": [{"text": "test"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {"parts": [{"data": {"narrative": "test"}}]},
            }
            mock_client.post.return_value = mock_response

            await send_message("http://localhost:8001", message)

            request_body = mock_client.post.call_args[1]["json"]
            assert request_body["jsonrpc"] == "2.0"
            assert request_body["method"] == "message/send"
            assert request_body["params"]["message"] == message

    @pytest.mark.asyncio
    async def test_returns_response_data(self):
        """Test send_message returns parsed response data."""
        from bulletproof_green.messenger import send_message

        message = {"messageId": str(uuid.uuid4()), "role": "user", "parts": [{"text": "test"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {"parts": [{"data": {"narrative": "Generated"}}]},
            }
            mock_client.post.return_value = mock_response

            response = await send_message("http://localhost:8001", message)

            assert response["narrative"] == "Generated"


class TestMessengerClass:
    """Test Messenger class high-level API."""

    @pytest.mark.asyncio
    async def test_send_integrates_functions(self):
        """Test Messenger.send() integrates create_message and send_message."""
        from bulletproof_green.messenger import Messenger

        messenger = Messenger(base_url="http://localhost:8001")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {"parts": [{"data": {"narrative": "test"}}]},
            }
            mock_client.post.return_value = mock_response

            response = await messenger.send(text="Generate narrative")

            assert response["narrative"] == "test"


class TestErrorHandling:
    """Test error handling for A2A protocol errors and timeouts."""

    @pytest.mark.asyncio
    async def test_handles_timeout(self):
        """Test send_message handles timeout gracefully."""
        import httpx

        from bulletproof_green.messenger import MessengerError, send_message

        message = {"messageId": str(uuid.uuid4()), "role": "user", "parts": [{"text": "test"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(MessengerError) as exc_info:
                await send_message("http://localhost:8001", message)
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_handles_connection_error(self):
        """Test send_message handles connection errors gracefully."""
        import httpx

        from bulletproof_green.messenger import MessengerError, send_message

        message = {"messageId": str(uuid.uuid4()), "role": "user", "parts": [{"text": "test"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(MessengerError) as exc_info:
                await send_message("http://localhost:9999", message)
            assert "connection" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_handles_jsonrpc_error(self):
        """Test send_message handles JSON-RPC error responses."""
        from bulletproof_green.messenger import MessengerError, send_message

        message = {"messageId": str(uuid.uuid4()), "role": "user", "parts": [{"text": "test"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "1",
                "error": {"code": -32600, "message": "Invalid Request"},
            }
            mock_client.post.return_value = mock_response

            with pytest.raises(MessengerError) as exc_info:
                await send_message("http://localhost:8001", message)
            assert "Invalid Request" in str(exc_info.value)
