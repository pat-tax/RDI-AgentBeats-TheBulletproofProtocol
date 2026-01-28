"""Tests for Arena Mode server integration (STORY-018).

This test module validates the acceptance criteria for STORY-018:
- Server accepts mode=arena parameter in message/send requests
- Routes to ArenaExecutor instead of single-shot evaluation
- Returns ArenaResult with iteration history in response
- Maintains backward compatibility with non-arena mode
"""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from bulletproof_green.server import create_app


def make_arena_mode_request(
    context: str,
    mode: str = "arena",
    req_id: str = "test-arena-1",
    max_iterations: int | None = None,
    target_risk_score: int | None = None,
) -> dict:
    """Create a message/send request with mode=arena parameter.

    Args:
        context: The initial context for narrative generation.
        mode: The mode parameter (arena or single-shot).
        req_id: The JSON-RPC request ID.
        max_iterations: Optional max iterations for arena mode.
        target_risk_score: Optional target risk score for arena mode.

    Returns:
        A valid message/send JSON-RPC request dict with mode parameter.
    """
    data = {
        "mode": mode,
        "context": context,
    }

    if max_iterations is not None:
        data["max_iterations"] = max_iterations

    if target_risk_score is not None:
        data["target_risk_score"] = target_risk_score

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


class TestArenaModeParameter:
    """Test server accepts mode=arena parameter."""

    @pytest.mark.asyncio
    async def test_server_accepts_mode_arena_parameter(self):
        """Test server accepts mode=arena in DataPart without error."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                ),
            )
            data = response.json()
            # Should not return error for valid mode parameter
            assert "error" not in data or data.get("error", {}).get("code") != -32602

    @pytest.mark.asyncio
    async def test_server_routes_to_arena_executor_for_arena_mode(self):
        """Test server routes to ArenaExecutor when mode=arena."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                ),
            )
            data = response.json()
            # Should have result (not error)
            assert "result" in data

    @pytest.mark.asyncio
    async def test_server_accepts_max_iterations_parameter(self):
        """Test server accepts max_iterations parameter for arena mode."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                    max_iterations=3,
                ),
            )
            data = response.json()
            # Should not return parameter error
            assert "error" not in data or data.get("error", {}).get("code") != -32602

    @pytest.mark.asyncio
    async def test_server_accepts_target_risk_score_parameter(self):
        """Test server accepts target_risk_score parameter for arena mode."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                    target_risk_score=15,
                ),
            )
            data = response.json()
            # Should not return parameter error
            assert "error" not in data or data.get("error", {}).get("code") != -32602


class TestArenaResultResponse:
    """Test arena mode returns ArenaResult in response."""

    @pytest.mark.asyncio
    async def test_arena_mode_returns_arena_result_structure(self):
        """Test arena mode response contains ArenaResult fields."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            # Should have message parts with arena result data
            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        arena_data = part["data"]
                        # ArenaResult fields
                        assert "success" in arena_data
                        assert "iterations" in arena_data
                        assert "total_iterations" in arena_data
                        assert "final_risk_score" in arena_data

    @pytest.mark.asyncio
    async def test_arena_result_contains_iteration_history(self):
        """Test arena result contains full iteration history."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                    max_iterations=2,
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        arena_data = part["data"]
                        iterations = arena_data.get("iterations", [])
                        # Should have at least one iteration
                        assert len(iterations) > 0
                        # Each iteration should have required fields
                        for iteration in iterations:
                            assert "iteration_number" in iteration
                            assert "narrative" in iteration
                            assert "risk_score" in iteration
                            assert "state" in iteration

    @pytest.mark.asyncio
    async def test_arena_result_contains_termination_reason(self):
        """Test arena result includes termination_reason."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                    max_iterations=1,
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        arena_data = part["data"]
                        # Should have termination reason
                        assert "termination_reason" in arena_data
                        assert arena_data["termination_reason"] in [
                            "target_reached",
                            "max_iterations_reached",
                        ]


class TestBackwardCompatibility:
    """Test backward compatibility with non-arena mode."""

    @pytest.mark.asyncio
    async def test_server_handles_requests_without_mode_parameter(self):
        """Test server works with requests that don't have mode parameter (single-shot)."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Traditional request without mode parameter
            response = await client.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "id": "test-1",
                    "params": {
                        "message": {
                            "messageId": str(uuid.uuid4()),
                            "role": "user",
                            "parts": [{"text": "Evaluate this narrative"}],
                        }
                    },
                },
            )
            data = response.json()
            # Should work in single-shot mode
            assert "result" in data

    @pytest.mark.asyncio
    async def test_single_shot_mode_returns_traditional_response(self):
        """Test single-shot mode (no mode param) returns traditional evaluation response."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "id": "test-1",
                    "params": {
                        "message": {
                            "messageId": str(uuid.uuid4()),
                            "role": "user",
                            "parts": [{"text": "Test narrative"}],
                        }
                    },
                },
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            # Should have traditional evaluation fields (not ArenaResult)
            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        eval_data = part["data"]
                        # Should have traditional evaluation fields
                        assert "overall_score" in eval_data or "score" in eval_data
                        # Should NOT have arena-specific fields
                        assert "iterations" not in eval_data


class TestArenaConfiguration:
    """Test arena mode configuration parameters."""

    @pytest.mark.asyncio
    async def test_arena_mode_respects_max_iterations(self):
        """Test arena mode respects max_iterations configuration."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                    max_iterations=2,
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        arena_data = part["data"]
                        total_iterations = arena_data.get("total_iterations", 0)
                        # Should not exceed max_iterations
                        assert total_iterations <= 2

    @pytest.mark.asyncio
    async def test_arena_mode_uses_default_config_when_not_specified(self):
        """Test arena mode uses default configuration when parameters not specified."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_mode_request(
                    context="Generate a qualifying R&D narrative",
                    mode="arena",
                    # No max_iterations or target_risk_score specified
                ),
            )
            data = response.json()
            # Should work with defaults (not raise error)
            assert "result" in data
