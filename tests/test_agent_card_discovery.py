"""Tests for AgentCard discovery module (STORY-007).

This test module validates the acceptance criteria for STORY-007:
- Both agents expose /.well-known/agent-card.json
- AgentCard contains capabilities, endpoints, name
- Green Agent discovers Purple Agent AgentCard
- JSON schema validation
- Caching for performance
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest


class TestPurpleAgentCardModule:
    """Test Purple Agent agent_card module exists and exports required components."""

    def test_purple_agent_card_module_exists(self):
        """Test agent_card module can be imported from bulletproof_purple."""
        from bulletproof_purple import agent_card

        assert agent_card is not None

    def test_purple_create_agent_card_exists(self):
        """Test create_agent_card function exists."""
        from bulletproof_purple.agent_card import create_agent_card

        assert create_agent_card is not None

    def test_purple_validate_agent_card_exists(self):
        """Test validate_agent_card function exists."""
        from bulletproof_purple.agent_card import validate_agent_card

        assert validate_agent_card is not None

    def test_purple_agent_card_schema_exists(self):
        """Test AGENT_CARD_SCHEMA constant exists."""
        from bulletproof_purple.agent_card import AGENT_CARD_SCHEMA

        assert AGENT_CARD_SCHEMA is not None
        assert isinstance(AGENT_CARD_SCHEMA, dict)


class TestGreenAgentCardModule:
    """Test Green Agent agent_card module exists and exports required components."""

    def test_green_agent_card_module_exists(self):
        """Test agent_card module can be imported from bulletproof_green."""
        from bulletproof_green import agent_card

        assert agent_card is not None

    def test_green_create_agent_card_exists(self):
        """Test create_agent_card function exists."""
        from bulletproof_green.agent_card import create_agent_card

        assert create_agent_card is not None

    def test_green_validate_agent_card_exists(self):
        """Test validate_agent_card function exists."""
        from bulletproof_green.agent_card import validate_agent_card

        assert validate_agent_card is not None

    def test_green_discover_agent_exists(self):
        """Test discover_agent function exists for Green Agent."""
        from bulletproof_green.agent_card import discover_agent

        assert discover_agent is not None

    def test_green_agent_card_cache_exists(self):
        """Test AgentCardCache class exists for caching."""
        from bulletproof_green.agent_card import AgentCardCache

        assert AgentCardCache is not None


class TestPurpleAgentCardCreation:
    """Test Purple Agent AgentCard creation."""

    def test_create_agent_card_returns_dict(self):
        """Test create_agent_card returns a dictionary."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        assert isinstance(card, dict)

    def test_agent_card_has_name(self):
        """Test AgentCard contains name field."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        assert "name" in card
        assert card["name"] == "Bulletproof Purple Agent"

    def test_agent_card_has_description(self):
        """Test AgentCard contains description field."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        assert "description" in card
        assert "IRS Section 41" in card["description"]

    def test_agent_card_has_url(self):
        """Test AgentCard contains url field."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card(base_url="http://localhost:8001")
        assert "url" in card
        assert card["url"] == "http://localhost:8001"

    def test_agent_card_has_version(self):
        """Test AgentCard contains version field."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        assert "version" in card
        assert card["version"] == "1.0.0"

    def test_agent_card_has_capabilities(self):
        """Test AgentCard contains capabilities field."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        assert "capabilities" in card
        assert isinstance(card["capabilities"], dict)

    def test_agent_card_has_skills(self):
        """Test AgentCard contains skills field."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        assert "skills" in card
        assert isinstance(card["skills"], list)
        assert len(card["skills"]) > 0

    def test_agent_card_skill_has_required_fields(self):
        """Test each skill has required fields: id, name, description."""
        from bulletproof_purple.agent_card import create_agent_card

        card = create_agent_card()
        for skill in card["skills"]:
            assert "id" in skill
            assert "name" in skill
            assert "description" in skill


class TestGreenAgentCardCreation:
    """Test Green Agent AgentCard creation."""

    def test_create_agent_card_returns_dict(self):
        """Test create_agent_card returns a dictionary."""
        from bulletproof_green.agent_card import create_agent_card

        card = create_agent_card()
        assert isinstance(card, dict)

    def test_agent_card_has_name(self):
        """Test AgentCard contains name field."""
        from bulletproof_green.agent_card import create_agent_card

        card = create_agent_card()
        assert "name" in card
        assert card["name"] == "Bulletproof Green Agent"

    def test_agent_card_has_evaluation_skill(self):
        """Test Green AgentCard has evaluation skill."""
        from bulletproof_green.agent_card import create_agent_card

        card = create_agent_card()
        skill_ids = [s["id"] for s in card["skills"]]
        assert "evaluate_narrative" in skill_ids


class TestAgentCardSchemaValidation:
    """Test JSON schema validation for AgentCard."""

    def test_valid_agent_card_passes_validation(self):
        """Test valid AgentCard passes schema validation."""
        from bulletproof_purple.agent_card import create_agent_card, validate_agent_card

        card = create_agent_card()
        # Should not raise
        result = validate_agent_card(card)
        assert result is True

    def test_missing_name_fails_validation(self):
        """Test AgentCard without name fails validation."""
        from bulletproof_purple.agent_card import validate_agent_card

        invalid_card = {
            "description": "Test",
            "url": "http://localhost",
            "version": "1.0.0",
        }
        result = validate_agent_card(invalid_card)
        assert result is False

    def test_missing_url_fails_validation(self):
        """Test AgentCard without url fails validation."""
        from bulletproof_purple.agent_card import validate_agent_card

        invalid_card = {
            "name": "Test Agent",
            "description": "Test",
            "version": "1.0.0",
        }
        result = validate_agent_card(invalid_card)
        assert result is False

    def test_invalid_capabilities_type_fails_validation(self):
        """Test AgentCard with invalid capabilities type fails validation."""
        from bulletproof_purple.agent_card import validate_agent_card

        invalid_card = {
            "name": "Test Agent",
            "description": "Test",
            "url": "http://localhost",
            "version": "1.0.0",
            "capabilities": "not_a_dict",  # Should be dict
        }
        result = validate_agent_card(invalid_card)
        assert result is False

    def test_invalid_skills_type_fails_validation(self):
        """Test AgentCard with invalid skills type fails validation."""
        from bulletproof_purple.agent_card import validate_agent_card

        invalid_card = {
            "name": "Test Agent",
            "description": "Test",
            "url": "http://localhost",
            "version": "1.0.0",
            "skills": "not_a_list",  # Should be list
        }
        result = validate_agent_card(invalid_card)
        assert result is False


class TestAgentCardDiscovery:
    """Test Green Agent discovering Purple Agent via AgentCard."""

    @pytest.mark.asyncio
    async def test_discover_agent_returns_agent_card(self):
        """Test discover_agent returns AgentCard dict."""
        from unittest.mock import MagicMock
        from bulletproof_green.agent_card import discover_agent

        mock_card = {
            "name": "Bulletproof Purple Agent",
            "url": "http://localhost:8001",
            "version": "1.0.0",
        }

        with patch("bulletproof_green.agent_card.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()  # httpx.Response methods are not async
            mock_response.status_code = 200
            mock_response.json.return_value = mock_card
            mock_client.get.return_value = mock_response

            card = await discover_agent("http://localhost:8001")

            assert card is not None
            assert card["name"] == "Bulletproof Purple Agent"

    @pytest.mark.asyncio
    async def test_discover_agent_fetches_well_known_endpoint(self):
        """Test discover_agent fetches from /.well-known/agent-card.json."""
        from unittest.mock import MagicMock
        from bulletproof_green.agent_card import discover_agent

        # Must include required fields for validation to pass
        mock_card = {"name": "Test", "url": "http://localhost:8001", "version": "1.0.0"}

        with patch("bulletproof_green.agent_card.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()  # httpx.Response methods are not async
            mock_response.status_code = 200
            mock_response.json.return_value = mock_card
            mock_client.get.return_value = mock_response

            await discover_agent("http://localhost:8001")

            mock_client.get.assert_called_once()
            call_url = mock_client.get.call_args[0][0]
            assert call_url == "http://localhost:8001/.well-known/agent-card.json"

    @pytest.mark.asyncio
    async def test_discover_agent_validates_response(self):
        """Test discover_agent validates the returned AgentCard."""
        from unittest.mock import MagicMock
        from bulletproof_green.agent_card import discover_agent, AgentCardValidationError

        invalid_card = {"description": "Missing name and url"}

        with patch("bulletproof_green.agent_card.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()  # httpx.Response methods are not async
            mock_response.status_code = 200
            mock_response.json.return_value = invalid_card
            mock_client.get.return_value = mock_response

            with pytest.raises(AgentCardValidationError):
                await discover_agent("http://localhost:8001")

    @pytest.mark.asyncio
    async def test_discover_agent_handles_connection_error(self):
        """Test discover_agent handles connection errors gracefully."""
        from bulletproof_green.agent_card import discover_agent, AgentCardDiscoveryError
        import httpx

        with patch("bulletproof_green.agent_card.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(AgentCardDiscoveryError) as exc_info:
                await discover_agent("http://localhost:9999")
            assert "connection" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_discover_agent_handles_timeout(self):
        """Test discover_agent handles timeout errors."""
        from bulletproof_green.agent_card import discover_agent, AgentCardDiscoveryError
        import httpx

        with patch("bulletproof_green.agent_card.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(AgentCardDiscoveryError) as exc_info:
                await discover_agent("http://localhost:8001", timeout=1)
            assert "timeout" in str(exc_info.value).lower()


class TestAgentCardCache:
    """Test AgentCard caching for performance."""

    def test_cache_initialization(self):
        """Test AgentCardCache can be initialized."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache()
        assert cache is not None

    def test_cache_with_custom_ttl(self):
        """Test AgentCardCache accepts custom TTL."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache(ttl_seconds=60)
        assert cache.ttl_seconds == 60

    def test_cache_default_ttl(self):
        """Test AgentCardCache has reasonable default TTL."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache()
        assert cache.ttl_seconds == 300  # 5 minutes default

    def test_cache_set_and_get(self):
        """Test cache can store and retrieve AgentCard."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache()
        card = {"name": "Test Agent", "url": "http://localhost"}

        cache.set("http://localhost:8001", card)
        result = cache.get("http://localhost:8001")

        assert result is not None
        assert result["name"] == "Test Agent"

    def test_cache_returns_none_for_missing_key(self):
        """Test cache returns None for non-existent key."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache()
        result = cache.get("http://nonexistent:8001")
        assert result is None

    def test_cache_invalidate(self):
        """Test cache can invalidate entries."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache()
        card = {"name": "Test Agent", "url": "http://localhost"}

        cache.set("http://localhost:8001", card)
        cache.invalidate("http://localhost:8001")
        result = cache.get("http://localhost:8001")

        assert result is None

    def test_cache_clear_all(self):
        """Test cache can clear all entries."""
        from bulletproof_green.agent_card import AgentCardCache

        cache = AgentCardCache()
        cache.set("http://localhost:8001", {"name": "Agent1"})
        cache.set("http://localhost:8002", {"name": "Agent2"})

        cache.clear()

        assert cache.get("http://localhost:8001") is None
        assert cache.get("http://localhost:8002") is None

    @pytest.mark.asyncio
    async def test_discover_agent_uses_cache(self):
        """Test discover_agent uses cache for repeated calls."""
        from unittest.mock import MagicMock
        from bulletproof_green.agent_card import discover_agent, AgentCardCache

        mock_card = {
            "name": "Bulletproof Purple Agent",
            "url": "http://localhost:8001",
            "version": "1.0.0",
        }

        cache = AgentCardCache()

        with patch("bulletproof_green.agent_card.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()  # httpx.Response methods are not async
            mock_response.status_code = 200
            mock_response.json.return_value = mock_card
            mock_client.get.return_value = mock_response

            # First call - fetches from network
            card1 = await discover_agent("http://localhost:8001", cache=cache)
            # Second call - should use cache
            card2 = await discover_agent("http://localhost:8001", cache=cache)

            # HTTP should only be called once
            assert mock_client.get.call_count == 1
            assert card1 == card2


class TestAgentCardExceptions:
    """Test custom exceptions for AgentCard module."""

    def test_agent_card_discovery_error_exists(self):
        """Test AgentCardDiscoveryError exception exists."""
        from bulletproof_green.agent_card import AgentCardDiscoveryError

        assert AgentCardDiscoveryError is not None
        assert issubclass(AgentCardDiscoveryError, Exception)

    def test_agent_card_validation_error_exists(self):
        """Test AgentCardValidationError exception exists."""
        from bulletproof_green.agent_card import AgentCardValidationError

        assert AgentCardValidationError is not None
        assert issubclass(AgentCardValidationError, Exception)


class TestAgentCardExport:
    """Test AgentCard components are properly exported."""

    def test_purple_create_agent_card_exported(self):
        """Test create_agent_card exported from bulletproof_purple."""
        from bulletproof_purple import create_agent_card

        assert create_agent_card is not None

    def test_green_create_agent_card_exported(self):
        """Test create_agent_card exported from bulletproof_green."""
        from bulletproof_green import create_agent_card

        assert create_agent_card is not None

    def test_green_discover_agent_exported(self):
        """Test discover_agent exported from bulletproof_green."""
        from bulletproof_green import discover_agent

        assert discover_agent is not None

    def test_green_agent_card_cache_exported(self):
        """Test AgentCardCache exported from bulletproof_green."""
        from bulletproof_green import AgentCardCache

        assert AgentCardCache is not None
