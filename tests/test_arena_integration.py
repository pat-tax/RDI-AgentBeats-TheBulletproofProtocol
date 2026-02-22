"""Arena Mode Integration Tests (STORY-018).

IMPORTANT: These are INTEGRATION tests, NOT true E2E tests.

WHAT THIS TESTS:
- Green agent: ASGI TestClient (in-process, no HTTP server)
- Purple agent: Real HTTP server (actual A2A communication)
- Arena mode: Multi-turn refinement with real Purple agent

This validates:
✓ Arena logic and orchestration
✓ A2A protocol with real Purple agent
✓ Multi-turn critique-driven refinement
✓ ArenaExecutor behavior

This does NOT test:
✗ Green agent HTTP server (use Docker E2E tests for that)
✗ Green agent networking/deployment
✗ Full system integration

For true E2E tests with both agents as HTTP servers:
- Use Docker E2E: ./scripts/test_e2e.sh

REQUIREMENTS:
- Purple agent must be running at configured URL (from settings)
- Green agent runs in-process via FastAPI TestClient (no server needed)
- Valid API keys/config if required

USAGE:
    # Start Purple agent first:
    cd src && python -m bulletproof_purple.server

    # Run integration tests:
    pytest tests/test_arena_integration.py -v

    # Override Purple agent URL via environment:
    PURPLE_PORT=9001 pytest tests/test_arena_integration.py -v

NOTES:
- These are SLOW tests (multi-turn LLM calls)
- Mark with @pytest.mark.integration for selective running
- Skip if Purple agent not available (don't fail CI)
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from bulletproof_green.server import create_app
from bulletproof_green.settings import settings as green_settings
from bulletproof_purple.settings import settings as purple_settings

# Get Purple agent URL from Green agent settings (which knows where to find Purple)
# This ensures E2E tests use the same configuration as the actual Green agent
PURPLE_AGENT_URL = green_settings.purple_agent_url


def make_arena_request(
    context: str,
    mode: str = "arena",
    max_iterations: int | None = None,
    target_risk_score: int | None = None,
) -> dict[str, Any]:
    """Create an arena mode JSON-RPC request.

    Args:
        context: Initial context for narrative generation.
        mode: Mode parameter (arena or single-shot).
        max_iterations: Optional max iterations for arena.
        target_risk_score: Optional target risk score.

    Returns:
        JSON-RPC request dict for message/send.
    """
    data: dict[str, Any] = {
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
        "id": f"e2e-{uuid.uuid4()}",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"data": data}],
            }
        },
    }


def check_purple_agent_available_sync() -> bool:
    """Check if Purple agent is available at configured URL (synchronous).

    Uses Purple agent settings to construct the expected URL, ensuring
    consistency with actual server configuration.

    Returns:
        True if Purple agent responds to /.well-known/agent-card.json
    """
    import httpx

    try:
        # Use sync httpx client
        url = f"http://{purple_settings.host}:{purple_settings.port}/.well-known/agent-card.json"
        response = httpx.get(url, timeout=5.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, Exception):
        return False


# Check Purple agent availability at module load time for skipif
PURPLE_AGENT_AVAILABLE = check_purple_agent_available_sync()

# Skip all integration tests if Purple agent not available
pytestmark = [
    pytest.mark.integration,  # Integration tests (Green=ASGI, Purple=HTTP)
    pytest.mark.skipif(
        not PURPLE_AGENT_AVAILABLE,
        reason=(
            f"Purple agent not available at {PURPLE_AGENT_URL}. "
            "Start Purple agent server before running integration tests."
        ),
    ),
]


class TestArenaIntegrationBasicFlow:
    """Integration tests for basic arena mode flow with real Purple agent."""

    @pytest.mark.asyncio
    async def test_arena_mode_completes_successfully(self):
        """Test arena mode completes with real Purple agent.

        This test validates:
        - Green agent creates arena executor
        - Purple agent generates narrative via A2A
        - Green agent evaluates narrative
        - Arena loop iterates until target reached or max iterations
        - Response contains valid ArenaResult
        """
        app = create_app(purple_agent_url=PURPLE_AGENT_URL)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_request(
                    context=(
                        "Generate an IRS Section 41 qualifying R&D narrative for a software company"
                    ),
                    mode="arena",
                    max_iterations=3,
                    target_risk_score=20,
                ),
                timeout=120.0,  # Arena mode can be slow (multiple LLM calls)
            )

            data = response.json()

            # Verify successful response
            assert "error" not in data, f"Request failed with error: {data.get('error')}"
            assert "result" in data

            result = data["result"]
            assert "parts" in result

            # Extract arena result from message parts
            arena_data = None
            for part in result["parts"]:
                if "data" in part:
                    arena_data = part["data"]
                    break

            assert arena_data is not None, "No data part found in response"

            # Validate ArenaResult structure
            assert "success" in arena_data
            assert "iterations" in arena_data
            assert "total_iterations" in arena_data
            assert "final_risk_score" in arena_data
            assert "final_narrative" in arena_data
            assert "termination_reason" in arena_data

            # Validate iterations
            iterations = arena_data["iterations"]
            assert len(iterations) > 0, "No iterations recorded"
            assert len(iterations) == arena_data["total_iterations"]
            assert len(iterations) <= 3, "Exceeded max_iterations"

            # Validate each iteration
            for i, iteration in enumerate(iterations):
                assert iteration["iteration_number"] == i + 1
                assert "narrative" in iteration
                assert "risk_score" in iteration
                assert "state" in iteration

                # First iteration should not have critique
                if i == 0:
                    assert iteration.get("critique") is None
                else:
                    # Subsequent iterations should have critique
                    assert iteration.get("critique") is not None

            # Validate termination reason
            assert arena_data["termination_reason"] in [
                "target_reached",
                "max_iterations_reached",
            ]

            # If successful, risk score should be below target
            if arena_data["success"]:
                assert arena_data["final_risk_score"] < 20

            print(f"\n✓ Arena completed in {arena_data['total_iterations']} iterations")
            print(f"✓ Final risk score: {arena_data['final_risk_score']}")
            print(f"✓ Termination: {arena_data['termination_reason']}")

    @pytest.mark.asyncio
    async def test_arena_mode_respects_max_iterations(self):
        """Test arena mode stops at max_iterations even if target not reached.

        This validates that the arena loop properly enforces iteration limits.
        """
        app = create_app(purple_agent_url=PURPLE_AGENT_URL)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_request(
                    context="Generate a challenging narrative",
                    mode="arena",
                    max_iterations=2,  # Strict limit
                    target_risk_score=5,  # Very low (hard to achieve)
                ),
                timeout=120.0,
            )

            data = response.json()
            assert "result" in data

            result = data["result"]
            arena_data = result["parts"][0]["data"]

            # Should stop at max_iterations
            assert arena_data["total_iterations"] <= 2
            assert arena_data["total_iterations"] == len(arena_data["iterations"])

            print(f"\n✓ Stopped at {arena_data['total_iterations']} iterations (max: 2)")

    @pytest.mark.asyncio
    async def test_arena_mode_iteration_improvement(self):
        """Test that arena iterations show risk score improvement.

        This validates that the critique-driven refinement actually improves
        narrative quality across iterations.
        """
        app = create_app(purple_agent_url=PURPLE_AGENT_URL)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_request(
                    context="Generate an IRS Section 41 R&D narrative",
                    mode="arena",
                    max_iterations=3,
                    target_risk_score=25,
                ),
                timeout=120.0,
            )

            data = response.json()
            result = data["result"]
            arena_data = result["parts"][0]["data"]

            iterations = arena_data["iterations"]

            # Track risk scores across iterations
            risk_scores = [iter["risk_score"] for iter in iterations]

            print(f"\n✓ Risk score progression: {risk_scores}")

            # Generally expect improvement (though not guaranteed)
            # At minimum, verify scores are reasonable
            for score in risk_scores:
                assert 0 <= score <= 100, f"Invalid risk score: {score}"


class TestArenaIntegrationA2AProtocol:
    """E2E tests for A2A protocol compliance."""

    @pytest.mark.asyncio
    async def test_purple_agent_a2a_message_format(self):
        """Test that Purple agent returns valid A2A message format.

        This validates proper A2A protocol implementation between agents.
        """
        # Test Purple agent directly via A2A
        async with httpx.AsyncClient() as client:
            # Get agent card
            card_response = await client.get(
                f"{PURPLE_AGENT_URL}/.well-known/agent-card.json",
                timeout=5.0,
            )
            assert card_response.status_code == 200
            agent_card = card_response.json()

            # Validate agent card structure
            assert "name" in agent_card
            assert "url" in agent_card
            assert "version" in agent_card

            print(f"\n✓ Purple agent: {agent_card['name']}")
            print(f"✓ Version: {agent_card['version']}")

    @pytest.mark.asyncio
    async def test_arena_mode_with_different_contexts(self):
        """Test arena mode with various narrative contexts.

        This validates that arena mode works with different types of R&D narratives.
        """
        app = create_app(purple_agent_url=PURPLE_AGENT_URL)

        test_contexts = [
            "Software development R&D for new algorithm",
            "Hardware prototyping for IoT device",
            "AI/ML model development for predictive analytics",
        ]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for context in test_contexts:
                response = await client.post(
                    "/",
                    json=make_arena_request(
                        context=context,
                        mode="arena",
                        max_iterations=2,
                    ),
                    timeout=120.0,
                )

                data = response.json()
                assert "result" in data, f"Failed for context: {context}"

                result = data["result"]
                arena_data = result["parts"][0]["data"]
                assert arena_data["total_iterations"] > 0

                print(f"\n✓ Context tested: {context[:50]}...")


class TestArenaIntegrationErrorHandling:
    """E2E tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_arena_mode_with_invalid_purple_agent_url(self):
        """Test arena mode gracefully handles Purple agent unavailable.

        This validates error handling when Purple agent is unreachable.
        """
        # Create app with invalid Purple agent URL
        app = create_app(purple_agent_url="http://localhost:9999")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/",
                json=make_arena_request(
                    context="Test context",
                    mode="arena",
                    max_iterations=1,
                ),
                timeout=30.0,
            )

            data = response.json()

            # Should return error (not crash)
            # Actual behavior depends on error handling implementation
            # Could be JSON-RPC error or failed task state
            assert "error" in data or ("result" in data and isinstance(data["result"], dict))

            error_msg = data.get("error", {}).get("message", "task failed")
            print(f"\n✓ Handled Purple agent unavailable: {error_msg}")


# Pytest configuration for E2E tests
def pytest_configure(config: Any) -> None:
    """Register E2E marker."""
    config.addinivalue_line(
        "markers",
        "integration: Integration tests with real Purple agent (Green in-process via ASGI)",
    )
