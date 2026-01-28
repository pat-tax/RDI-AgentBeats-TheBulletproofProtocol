"""Tests for messenger.py module (STORY-022).

This test module validates the acceptance criteria for STORY-022:
- messenger.py exposes create_message() function for A2A message construction
- messenger.py exposes send_message() function for HTTP POST to purple agents
- Messenger class provides high-level API for agent-to-agent communication
- Handles A2A protocol errors and timeouts gracefully
- Unit tests verify message format and sending logic
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMessengerImport:
    """Test messenger module can be imported."""

    def test_messenger_module_exists(self):
        """Test messenger module can be imported."""
        from bulletproof_green import messenger

        assert messenger is not None

    def test_create_message_function_exists(self):
        """Test create_message function exists."""
        from bulletproof_green.messenger import create_message

        assert create_message is not None
        assert callable(create_message)

    def test_send_message_function_exists(self):
        """Test send_message function exists."""
        from bulletproof_green.messenger import send_message

        assert send_message is not None
        assert callable(send_message)

    def test_messenger_class_exists(self):
        """Test Messenger class exists."""
        from bulletproof_green.messenger import Messenger

        assert Messenger is not None


class TestCreateMessage:
    """Test create_message() function for A2A message construction."""

    def test_create_message_with_text_only(self):
        """Test create_message creates valid A2A message with text."""
        from bulletproof_green.messenger import create_message

        message = create_message(text="Please generate a narrative")

        assert "messageId" in message
        assert message["role"] == "user"
        assert "parts" in message
        assert len(message["parts"]) == 1
        assert message["parts"][0]["text"] == "Please generate a narrative"

    def test_create_message_with_data_only(self):
        """Test create_message creates valid A2A message with data."""
        from bulletproof_green.messenger import create_message

        data = {"template_type": "qualifying", "signals": {"project": "test"}}
        message = create_message(data=data)

        assert "messageId" in message
        assert message["role"] == "user"
        assert "parts" in message
        assert len(message["parts"]) == 1
        assert message["parts"][0]["data"] == data

    def test_create_message_with_text_and_data(self):
        """Test create_message creates valid A2A message with both text and data."""
        from bulletproof_green.messenger import create_message

        text = "Generate a narrative"
        data = {"template_type": "qualifying"}
        message = create_message(text=text, data=data)

        assert "messageId" in message
        assert message["role"] == "user"
        assert "parts" in message
        assert len(message["parts"]) == 2
        assert message["parts"][0]["text"] == text
        assert message["parts"][1]["data"] == data

    def test_create_message_generates_unique_id(self):
        """Test create_message generates unique message IDs."""
        from bulletproof_green.messenger import create_message

        msg1 = create_message(text="test1")
        msg2 = create_message(text="test2")

        assert msg1["messageId"] != msg2["messageId"]
        # Validate UUIDs
        uuid.UUID(msg1["messageId"])
        uuid.UUID(msg2["messageId"])

    def test_create_message_with_custom_role(self):
        """Test create_message accepts custom role."""
        from bulletproof_green.messenger import create_message

        message = create_message(text="test", role="assistant")

        assert message["role"] == "assistant"

    def test_create_message_default_role_is_user(self):
        """Test create_message defaults to 'user' role."""
        from bulletproof_green.messenger import create_message

        message = create_message(text="test")

        assert message["role"] == "user"


class TestSendMessage:
    """Test send_message() function for HTTP POST to purple agents."""

    @pytest.mark.asyncio
    async def test_send_message_posts_to_url(self):
        """Test send_message sends HTTP POST to specified URL."""
        from bulletproof_green.messenger import send_message

        url = "http://localhost:8001"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {"parts": [{"data": {"narrative": "test narrative"}}]},
            }
            mock_client.post.return_value = mock_response

            response = await send_message(url, message)

            mock_client.post.assert_called_once()
            assert response is not None

    @pytest.mark.asyncio
    async def test_send_message_uses_jsonrpc_format(self):
        """Test send_message wraps message in JSON-RPC 2.0 format."""
        from bulletproof_green.messenger import send_message

        url = "http://localhost:8001"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

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

            await send_message(url, message)

            # Check JSON-RPC wrapper
            call_args = mock_client.post.call_args
            request_body = call_args[1]["json"]
            assert request_body["jsonrpc"] == "2.0"
            assert request_body["method"] == "message/send"
            assert "id" in request_body
            assert request_body["params"]["message"] == message

    @pytest.mark.asyncio
    async def test_send_message_accepts_timeout(self):
        """Test send_message accepts custom timeout parameter."""
        from bulletproof_green.messenger import send_message

        url = "http://localhost:8001"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

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

            await send_message(url, message, timeout=60)

            # Check timeout passed to client
            call_args = mock_client_class.call_args
            assert call_args[1]["timeout"] == 60

    @pytest.mark.asyncio
    async def test_send_message_returns_response_data(self):
        """Test send_message returns parsed response data."""
        from bulletproof_green.messenger import send_message

        url = "http://localhost:8001"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

        expected_narrative = "Generated test narrative"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {"parts": [{"data": {"narrative": expected_narrative}}]},
            }
            mock_client.post.return_value = mock_response

            response = await send_message(url, message)

            assert response["narrative"] == expected_narrative


class TestMessengerClass:
    """Test Messenger class provides high-level API."""

    def test_messenger_accepts_base_url(self):
        """Test Messenger can be constructed with base URL."""
        from bulletproof_green.messenger import Messenger

        messenger = Messenger(base_url="http://localhost:8001")
        assert messenger.base_url == "http://localhost:8001"

    def test_messenger_has_default_timeout(self):
        """Test Messenger has default timeout configuration."""
        from bulletproof_green.messenger import Messenger

        messenger = Messenger(base_url="http://localhost:8001")
        assert messenger.timeout == 300  # Default 300 seconds

    def test_messenger_accepts_custom_timeout(self):
        """Test Messenger accepts custom timeout."""
        from bulletproof_green.messenger import Messenger

        messenger = Messenger(base_url="http://localhost:8001", timeout=60)
        assert messenger.timeout == 60

    @pytest.mark.asyncio
    async def test_messenger_send_integrates_functions(self):
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
                "result": {"parts": [{"data": {"narrative": "test narrative"}}]},
            }
            mock_client.post.return_value = mock_response

            response = await messenger.send(text="Generate narrative")

            assert response is not None
            assert response["narrative"] == "test narrative"

    @pytest.mark.asyncio
    async def test_messenger_send_with_data(self):
        """Test Messenger.send() accepts data parameter."""
        from bulletproof_green.messenger import Messenger

        messenger = Messenger(base_url="http://localhost:8001")
        data = {"template_type": "qualifying"}

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

            response = await messenger.send(text="Generate", data=data)

            assert response is not None


class TestErrorHandling:
    """Test error handling for A2A protocol errors and timeouts."""

    @pytest.mark.asyncio
    async def test_send_message_handles_timeout(self):
        """Test send_message handles timeout gracefully."""
        from bulletproof_green.messenger import MessengerError, send_message

        url = "http://localhost:8001"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            import httpx

            mock_client.post.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(MessengerError) as exc_info:
                await send_message(url, message)
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_message_handles_connection_error(self):
        """Test send_message handles connection errors gracefully."""
        from bulletproof_green.messenger import MessengerError, send_message

        url = "http://localhost:9999"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            import httpx

            mock_client.post.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(MessengerError) as exc_info:
                await send_message(url, message)
            assert "connection" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_message_handles_jsonrpc_error(self):
        """Test send_message handles JSON-RPC error responses."""
        from bulletproof_green.messenger import MessengerError, send_message

        url = "http://localhost:8001"
        message = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "test"}],
        }

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
                await send_message(url, message)
            assert "Invalid Request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_messenger_class_handles_errors(self):
        """Test Messenger class propagates errors from send_message."""
        from bulletproof_green.messenger import Messenger, MessengerError

        messenger = Messenger(base_url="http://localhost:8001")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            import httpx

            mock_client.post.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(MessengerError):
                await messenger.send(text="test")


class TestMessengerExport:
    """Test messenger module exports are available."""

    def test_messenger_exported_from_green_module(self):
        """Test Messenger is exported from bulletproof_green module."""
        from bulletproof_green import Messenger

        assert Messenger is not None

    def test_create_message_exported(self):
        """Test create_message is exported from bulletproof_green module."""
        from bulletproof_green import create_message

        assert create_message is not None

    def test_send_message_exported(self):
        """Test send_message is exported from bulletproof_green module."""
        from bulletproof_green import send_message

        assert send_message is not None

    def test_messenger_error_exported(self):
        """Test MessengerError is exported from bulletproof_green module."""
        from bulletproof_green import MessengerError

        assert MessengerError is not None
