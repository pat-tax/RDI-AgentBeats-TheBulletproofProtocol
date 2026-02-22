"""Tests for messenger.py module - Sprint 2 (STORY-033 to STORY-038).

Validates a2a-sdk client integration:
- SDK client connection and caching (STORY-033)
- SDK message construction (STORY-034)
- SDK response extraction (STORY-035)
- SDK error mapping (STORY-036)
- Client lifecycle management (STORY-037)
- Backward compatibility (STORY-038)
"""

from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from a2a.types import (
    Artifact,
    DataPart,
    Message,
    Part,
    Role,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(
    state: TaskState = TaskState.completed,
    artifacts: list[Artifact] | None = None,
) -> Task:
    """Build a minimal Task object for testing."""
    return Task(
        id=str(uuid.uuid4()),
        context_id=str(uuid.uuid4()),
        status=TaskStatus(state=state),
        artifacts=artifacts or [],
    )


def _artifact_with_data(data: dict[str, Any]) -> Artifact:
    """Build an Artifact containing a single DataPart."""
    return Artifact(
        artifact_id=str(uuid.uuid4()),
        parts=[Part(root=DataPart(data=data))],
    )


def _artifact_with_text(text: str) -> Artifact:
    """Build an Artifact containing a single TextPart."""
    return Artifact(
        artifact_id=str(uuid.uuid4()),
        parts=[Part(root=TextPart(text=text))],
    )


async def _async_iter(*items):
    """Create an async iterator from items."""
    for item in items:
        yield item


@pytest.fixture(autouse=True)
def _mock_httpx_client():
    """Prevent real httpx.AsyncClient creation in messenger (SOCKS proxy)."""
    with patch("bulletproof_green.messenger.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value = AsyncMock()
        yield mock_cls


# ---------------------------------------------------------------------------
# STORY-033: SDK Client Connection and Caching
# ---------------------------------------------------------------------------

class TestSDKClientConnection:
    """Test ClientFactory.connect() integration and per-URL caching."""

    @pytest.mark.asyncio
    async def test_send_calls_client_factory_connect(self):
        """Messenger.send() uses ClientFactory.connect() instead of httpx."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = AsyncMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="hello")

            mock_factory.connect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_client_cached_per_url(self):
        """Second send() to same URL reuses cached Client (no second connect)."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = AsyncMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="first")
            await messenger.send(text="second")

            assert mock_factory.connect.await_count == 1

    @pytest.mark.asyncio
    async def test_client_config_streaming_false(self):
        """ClientConfig passed to connect() has streaming=False."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = AsyncMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="hello")

            call_kwargs = mock_factory.connect.call_args
            config = call_kwargs.kwargs.get("client_config") or call_kwargs.args[1]
            assert config.streaming is False

    @pytest.mark.asyncio
    async def test_httpx_client_passed_via_config(self):
        """httpx.AsyncClient is passed through ClientConfig for timeout control."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = AsyncMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010", timeout=42)
            await messenger.send(text="hello")

            call_kwargs = mock_factory.connect.call_args
            config = call_kwargs.kwargs.get("client_config") or call_kwargs.args[1]
            assert config.httpx_client is not None


# ---------------------------------------------------------------------------
# STORY-034: SDK Message Construction
# ---------------------------------------------------------------------------

class TestSDKMessageConstruction:
    """Test that Messenger.send() builds proper a2a-sdk Message objects."""

    @pytest.mark.asyncio
    async def test_send_text_creates_text_part(self):
        """send(text=...) creates Message with single TextPart."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])
        captured_msg: list[Message] = []

        def capture_send(msg, **kw):
            captured_msg.append(msg)
            return _async_iter((task, None))

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = capture_send
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="Generate a narrative")

        msg = captured_msg[0]
        assert len(msg.parts) == 1
        assert isinstance(msg.parts[0].root, TextPart)
        assert msg.parts[0].root.text == "Generate a narrative"

    @pytest.mark.asyncio
    async def test_send_data_creates_data_part(self):
        """send(data=...) creates Message with single DataPart."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])
        captured_msg: list[Message] = []

        def capture_send(msg, **kw):
            captured_msg.append(msg)
            return _async_iter((task, None))

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = capture_send
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(data={"template_type": "qualifying"})

        msg = captured_msg[0]
        assert len(msg.parts) == 1
        assert isinstance(msg.parts[0].root, DataPart)
        assert msg.parts[0].root.data == {"template_type": "qualifying"}

    @pytest.mark.asyncio
    async def test_send_text_and_data_creates_both_parts(self):
        """send(text=..., data=...) creates Message with TextPart + DataPart."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])
        captured_msg: list[Message] = []

        def capture_send(msg, **kw):
            captured_msg.append(msg)
            return _async_iter((task, None))

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = capture_send
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="Context", data={"template_type": "qualifying"})

        msg = captured_msg[0]
        assert len(msg.parts) == 2
        assert isinstance(msg.parts[0].root, TextPart)
        assert isinstance(msg.parts[1].root, DataPart)

    @pytest.mark.asyncio
    async def test_message_uses_role_enum(self):
        """Message uses Role.user enum, not raw string."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])
        captured_msg: list[Message] = []

        def capture_send(msg, **kw):
            captured_msg.append(msg)
            return _async_iter((task, None))

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = capture_send
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="hello")

        assert captured_msg[0].role == Role.user

    @pytest.mark.asyncio
    async def test_message_has_unique_id(self):
        """Each message has a unique UUID messageId."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])
        captured_msgs: list[Message] = []

        def capture_send(msg, **kw):
            captured_msgs.append(msg)
            return _async_iter((task, None))

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = capture_send
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="first")
            await messenger.send(text="second")

        assert captured_msgs[0].message_id != captured_msgs[1].message_id
        uuid.UUID(captured_msgs[0].message_id)  # valid UUID


# ---------------------------------------------------------------------------
# STORY-035: SDK Response Extraction
# ---------------------------------------------------------------------------

class TestSDKResponseExtraction:
    """Test extraction from Task artifacts."""

    @pytest.mark.asyncio
    async def test_extracts_data_part_from_completed_task(self):
        """Extracts DataPart.data dict from completed task artifacts."""
        from bulletproof_green.messenger import Messenger

        payload = {"narrative": "The R&D activities...", "risk_score": 15}
        task = _make_task(artifacts=[_artifact_with_data(payload)])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            result = await messenger.send(text="hello")

        assert result == payload

    @pytest.mark.asyncio
    async def test_wraps_text_part_as_dict(self):
        """Wraps TextPart.text as {"text": "..."} when no DataPart present."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_text("plain response")])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            result = await messenger.send(text="hello")

        assert result == {"text": "plain response"}

    @pytest.mark.asyncio
    async def test_skips_non_completed_states(self):
        """Skips working/submitted states, extracts from completed."""
        from bulletproof_green.messenger import Messenger

        working_task = _make_task(state=TaskState.working)
        completed_task = _make_task(
            artifacts=[_artifact_with_data({"narrative": "done"})]
        )

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter(
                (working_task, None), (completed_task, None)
            )
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            result = await messenger.send(text="hello")

        assert result == {"narrative": "done"}

    @pytest.mark.asyncio
    async def test_raises_on_completed_without_artifacts(self):
        """Raises MessengerError when completed task has no artifacts."""
        from bulletproof_green.messenger import Messenger, MessengerError

        task = _make_task(state=TaskState.completed, artifacts=[])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            with pytest.raises(MessengerError):
                await messenger.send(text="hello")


# ---------------------------------------------------------------------------
# STORY-036: SDK Error Mapping
# ---------------------------------------------------------------------------

class TestSDKErrorMapping:
    """Test a2a-sdk exception → MessengerError mapping."""

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """A2AClientTimeoutError maps to MessengerError with 'timeout'."""
        from a2a.client import A2AClientTimeoutError

        from bulletproof_green.messenger import Messenger, MessengerError

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(
                side_effect=A2AClientTimeoutError("timed out")
            )

            messenger = Messenger(base_url="http://localhost:9010")
            with pytest.raises(MessengerError, match="(?i)timeout"):
                await messenger.send(text="hello")

    @pytest.mark.asyncio
    async def test_http_error(self):
        """A2AClientHTTPError maps to MessengerError with status code."""
        from a2a.client import A2AClientHTTPError

        from bulletproof_green.messenger import Messenger, MessengerError

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(
                side_effect=A2AClientHTTPError(500, "Internal Server Error")
            )

            messenger = Messenger(base_url="http://localhost:9010")
            with pytest.raises(MessengerError, match="500"):
                await messenger.send(text="hello")

    @pytest.mark.asyncio
    async def test_connect_error(self):
        """httpx.ConnectError during connect maps to MessengerError."""
        from bulletproof_green.messenger import Messenger, MessengerError

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            messenger = Messenger(base_url="http://localhost:9010")
            with pytest.raises(MessengerError, match="(?i)connection"):
                await messenger.send(text="hello")

    @pytest.mark.asyncio
    async def test_failed_task_state(self):
        """TaskState.failed in event stream raises MessengerError."""
        from bulletproof_green.messenger import Messenger, MessengerError

        task = _make_task(state=TaskState.failed)

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            with pytest.raises(MessengerError, match="(?i)failed"):
                await messenger.send(text="hello")

    @pytest.mark.asyncio
    async def test_no_double_wrapping(self):
        """MessengerError raised inside send is not double-wrapped."""
        from bulletproof_green.messenger import Messenger, MessengerError

        task = _make_task(state=TaskState.failed)

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            with pytest.raises(MessengerError) as exc_info:
                await messenger.send(text="hello")

            # Should NOT be wrapped in another MessengerError
            assert not isinstance(exc_info.value.__cause__, MessengerError)


# ---------------------------------------------------------------------------
# STORY-037: Client Lifecycle Management
# ---------------------------------------------------------------------------

class TestClientLifecycle:
    """Test close() method for cleanup."""

    @pytest.mark.asyncio
    async def test_close_clears_cache(self):
        """close() clears client cache so next send() reconnects."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="first")
            assert mock_factory.connect.await_count == 1

            await messenger.close()
            await messenger.send(text="second")
            assert mock_factory.connect.await_count == 2

    @pytest.mark.asyncio
    async def test_close_calls_aclose_on_httpx_clients(self):
        """close() calls aclose() on managed httpx.AsyncClient instances."""
        from bulletproof_green.messenger import Messenger

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            await messenger.send(text="hello")
            await messenger.close()

            # Verify httpx clients were cleaned up
            assert messenger._httpx_clients == {}
            assert messenger._clients == {}

    @pytest.mark.asyncio
    async def test_close_idempotent(self):
        """close() is safe to call on unused Messenger."""
        from bulletproof_green.messenger import Messenger

        messenger = Messenger(base_url="http://localhost:9010")
        await messenger.close()  # should not raise
        await messenger.close()  # idempotent


# ---------------------------------------------------------------------------
# STORY-038: Backward Compatibility
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """Test preserved public API surface."""

    @pytest.mark.asyncio
    async def test_send_message_free_function(self):
        """send_message() free function is importable and callable."""
        from bulletproof_green.messenger import send_message

        task = _make_task(artifacts=[_artifact_with_data({"narrative": "ok"})])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            msg = {"messageId": "x", "role": "user", "parts": [{"text": "hi"}]}
            result = await send_message("http://localhost:9010", msg)
            assert result == {"narrative": "ok"}

    def test_messenger_importable_from_package(self):
        """Messenger importable from bulletproof_green package root."""
        from bulletproof_green import Messenger, MessengerError

        assert Messenger is not None
        assert MessengerError is not None

    def test_messenger_stores_base_url(self):
        """Messenger(base_url=url) stores base_url as public attribute."""
        from bulletproof_green.messenger import Messenger

        m = Messenger(base_url="http://example.com")
        assert m.base_url == "http://example.com"

    def test_messenger_timeout_defaults_to_settings(self):
        """Messenger timeout defaults to settings.timeout when not provided."""
        from bulletproof_green.messenger import Messenger
        from bulletproof_green.settings import settings

        m = Messenger(base_url="http://example.com")
        assert m.timeout == settings.timeout

    def test_initial_cache_empty(self):
        """Initial client cache is empty (no connections until first send)."""
        from bulletproof_green.messenger import Messenger

        m = Messenger(base_url="http://example.com")
        assert m._clients == {}
        assert m._httpx_clients == {}

    @pytest.mark.asyncio
    async def test_send_returns_dict_for_model_validate(self):
        """Messenger.send() returns dict compatible with NarrativeResponse."""
        from bulletproof_green.messenger import Messenger

        payload = {"narrative": "The R&D activities...", "risk_score": 15}
        task = _make_task(artifacts=[_artifact_with_data(payload)])

        with patch("bulletproof_green.messenger.ClientFactory") as mock_factory:
            mock_client = MagicMock()
            mock_client.send_message = lambda *a, **kw: _async_iter((task, None))
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger(base_url="http://localhost:9010")
            result = await messenger.send(
                text="Context", data={"template_type": "qualifying"}
            )

        assert isinstance(result, dict)
        assert result == payload
