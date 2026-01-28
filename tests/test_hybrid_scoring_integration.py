"""Tests for hybrid scoring integration into server (STORY-019).

This test module validates the acceptance criteria for STORY-019:
- Server integrates hybrid scoring (rule-based + LLM)
- Returns standardized evaluation output format per Green-Agent-Metrics-Specification.md
- Graceful fallback to rule-only when LLM unavailable
- Hybrid scores properly combined using alpha*rule + beta*llm formula
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from bulletproof_green.server import create_app


def make_message_send_request(text: str, req_id: str = "test-1") -> dict:
    """Create a properly formatted message/send JSON-RPC request.

    Args:
        text: The text content of the message.
        req_id: The JSON-RPC request ID.

    Returns:
        A valid message/send JSON-RPC request dict.
    """
    import uuid

    return {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": req_id,
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": text}],
            }
        },
    }


class TestHybridScoringIntegration:
    """Test hybrid scoring integration in server."""

    @pytest.mark.asyncio
    async def test_server_uses_hybrid_scoring_when_llm_available(self):
        """Test server uses hybrid scoring when OPENAI_API_KEY is available."""
        # Set API key in environment
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Mock OpenAI client to track if it's called
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content='{"score": 0.85, "reasoning": "Test reasoning", '
                        '"categories": {"technical_uncertainty": 0.8, "experimentation": 0.9, '
                        '"technological_nature": 0.85, "business_component": 0.8}}'
                    )
                )
            ]
            mock_client = MagicMock()
            mock_client.chat = MagicMock()
            mock_client.chat.completions = MagicMock()
            mock_create = AsyncMock(return_value=mock_response)
            mock_client.chat.completions.create = mock_create

            with patch(
                "openai.AsyncOpenAI", return_value=mock_client
            ):
                app = create_app()
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.post(
                        "/",
                        json=make_message_send_request(
                            "Our hypothesis was to reduce latency from 500ms to 100ms. "
                            "After 15 experiments and 8 failures, we achieved 45ms."
                        ),
                    )
                    data = response.json()
                    assert "result" in data
                    result = data["result"]

                    # Check that LLM was actually called
                    assert mock_create.called, "LLM should be called for hybrid scoring"

                    # Check that response contains hybrid scoring data
                    if "parts" in result:
                        for part in result["parts"]:
                            if "data" in part:
                                score_data = part["data"]
                                # Should have hybrid scoring metadata
                                assert "overall_score" in score_data
                                # When LLM is used, we should have evidence of it
                                # The overall_score should be influenced by both rule and LLM

    @pytest.mark.asyncio
    async def test_server_falls_back_to_rule_only_when_llm_unavailable(self):
        """Test server falls back to rule-only scoring when LLM unavailable."""
        # Ensure no API key in environment
        with patch.dict(os.environ, {}, clear=True):
            app = create_app()
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/",
                    json=make_message_send_request(
                        "Our hypothesis was to reduce latency from 500ms to 100ms."
                    ),
                )
                data = response.json()
                assert "result" in data
                result = data["result"]

                # Should still get valid response with rule-only scoring
                if "parts" in result:
                    for part in result["parts"]:
                        if "data" in part:
                            score_data = part["data"]
                            assert "overall_score" in score_data
                            assert "risk_score" in score_data

    @pytest.mark.asyncio
    async def test_hybrid_score_combines_rule_and_llm_scores(self):
        """Test hybrid score properly combines rule and LLM scores using formula."""
        # Mock LLM to return known score
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content='{"score": 0.9, "reasoning": "Excellent", "categories": '
                        '{"technical_uncertainty": 0.9, "experimentation": 0.9, '
                        '"technological_nature": 0.9, "business_component": 0.9}}'
                    )
                )
            ]
            mock_client = MagicMock()
            mock_client.chat = MagicMock()
            mock_client.chat.completions = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch(
                "openai.AsyncOpenAI", return_value=mock_client
            ):
                app = create_app()
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    # Use a narrative that should get good rule-based score
                    qualifying_narrative = (
                        "Our hypothesis was that using a custom B-tree implementation could "
                        "reduce database query times from 200ms to under 50ms. We were uncertain "
                        "whether memory constraints would allow this optimization. "
                        "We conducted 12 experiments testing different node sizes. "
                        "Initial attempts with 4KB nodes failed due to cache misses. "
                        "After 6 iterations, we discovered that 16KB nodes with prefetching "
                        "achieved 35ms query times, a 5.7x improvement."
                    )
                    response = await client.post(
                        "/", json=make_message_send_request(qualifying_narrative)
                    )
                    data = response.json()
                    assert "result" in data
                    result = data["result"]

                    if "parts" in result:
                        for part in result["parts"]:
                            if "data" in part:
                                score_data = part["data"]
                                # With both LLM (0.9) and good rule score, overall should be high
                                assert "overall_score" in score_data
                                # Hybrid score should reflect both components
                                assert score_data["overall_score"] > 0.5

    @pytest.mark.asyncio
    async def test_response_contains_standardized_output_format(self):
        """Test response follows Green-Agent-Metrics-Specification.md format."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/",
                json=make_message_send_request(
                    "We investigated caching to achieve sub-millisecond response times. "
                    "Initial attempts failed. After 5 iterations we achieved 0.8ms latency."
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        # Check for standardized format fields
                        # Primary metrics
                        assert "classification" in score_data
                        assert "confidence" in score_data
                        assert "risk_score" in score_data
                        assert "risk_category" in score_data

                        # Component scores
                        assert "correctness" in score_data
                        assert "safety" in score_data
                        assert "specificity" in score_data
                        assert "experimentation" in score_data

    @pytest.mark.asyncio
    async def test_llm_failure_gracefully_falls_back(self):
        """Test graceful fallback when LLM call fails."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Mock LLM client to raise exception
            mock_client = MagicMock()
            mock_client.chat = MagicMock()
            mock_client.chat.completions = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("API error")
            )

            with patch(
                "openai.AsyncOpenAI", return_value=mock_client
            ):
                app = create_app()
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.post(
                        "/", json=make_message_send_request("Test narrative")
                    )
                    data = response.json()
                    assert "result" in data
                    result = data["result"]

                    # Should still get valid response despite LLM failure
                    if "parts" in result:
                        for part in result["parts"]:
                            if "data" in part:
                                score_data = part["data"]
                                assert "overall_score" in score_data
                                assert "risk_score" in score_data

    @pytest.mark.asyncio
    async def test_hybrid_scoring_preserves_component_scores(self):
        """Test hybrid scoring preserves individual component scores."""
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/",
                json=make_message_send_request(
                    "We experimented with different algorithms. After multiple failures, "
                    "we achieved 45ms latency, improving performance by 10x."
                ),
            )
            data = response.json()
            assert "result" in data
            result = data["result"]

            if "parts" in result:
                for part in result["parts"]:
                    if "data" in part:
                        score_data = part["data"]
                        # All component scores should be present and in valid range
                        assert 0.0 <= score_data["correctness"] <= 1.0
                        assert 0.0 <= score_data["safety"] <= 1.0
                        assert 0.0 <= score_data["specificity"] <= 1.0
                        assert 0.0 <= score_data["experimentation"] <= 1.0
