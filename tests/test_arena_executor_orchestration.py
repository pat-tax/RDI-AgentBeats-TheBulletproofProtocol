"""Tests for Arena Mode orchestration (STORY-015).

Validates core behavior:
- Loop terminates when risk_score < target OR max_iterations reached
- Calls Purple agent via A2A, sends critique on subsequent iterations
- Returns ArenaResult with full iteration history
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest


class TestArenaExecutorRun:
    """Test ArenaExecutor run method - core loop behavior."""

    @pytest.mark.asyncio
    async def test_run_stops_when_target_reached(self):
        """Test run stops when risk_score < target_risk_score."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=5, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = ("Qualifying narrative", 15, {})

            result = await executor.run(initial_context="Generate a narrative")

            assert result.success is True
            assert result.total_iterations == 1
            assert result.termination_reason == "target_reached"

    @pytest.mark.asyncio
    async def test_run_stops_at_max_iterations(self):
        """Test run stops when max_iterations reached."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=3, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = ("Non-qualifying narrative", 50, {})

            result = await executor.run(initial_context="Generate a narrative")

            assert result.success is False
            assert result.total_iterations == 3
            assert result.termination_reason == "max_iterations_reached"

    @pytest.mark.asyncio
    async def test_run_iterates_until_success(self):
        """Test run iterates until target is reached."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=5, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        call_count = 0

        async def mock_iteration(*args: Any, **kwargs: Any) -> tuple[str, int, dict[str, Any]]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return ("Non-qualifying", 50, {})
            return ("Qualifying", 15, {})

        with patch.object(executor, "_run_iteration", side_effect=mock_iteration):
            result = await executor.run(initial_context="Generate a narrative")

            assert result.success is True
            assert result.total_iterations == 3

    @pytest.mark.asyncio
    async def test_run_records_all_iterations(self):
        """Test run records all iteration history."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=3, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        call_count = 0

        async def mock_iteration(*args: Any, **kwargs: Any) -> tuple[str, int, dict[str, Any]]:
            nonlocal call_count
            call_count += 1
            return (f"Narrative {call_count}", 50 - (call_count * 15), {})

        with patch.object(executor, "_run_iteration", side_effect=mock_iteration):
            result = await executor.run(initial_context="Generate a narrative")

            assert len(result.iterations) == result.total_iterations
            for i, iteration in enumerate(result.iterations):
                assert iteration.iteration_number == i + 1


class TestArenaExecutorA2AIntegration:
    """Test ArenaExecutor A2A integration with Purple Agent."""

    @pytest.mark.asyncio
    async def test_sends_critique_on_subsequent_iterations(self):
        """Test executor sends critique to Purple agent on subsequent iterations."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=3, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        call_count = 0
        calls_with_critique: list[bool] = []

        async def mock_purple(context: str, critique: str | None = None) -> str:
            nonlocal call_count
            call_count += 1
            calls_with_critique.append(critique is not None)
            return f"Narrative {call_count}"

        with patch.object(executor, "_call_purple_agent", side_effect=mock_purple):
            with patch.object(executor, "_evaluate_narrative") as mock_eval:
                mock_eval.side_effect = [
                    (50, {"issues": ["vagueness"]}),
                    (35, {"issues": ["specificity"]}),
                    (15, {}),
                ]

                await executor.run(initial_context="Generate a narrative")

                # First call should not have critique, subsequent calls should
                assert calls_with_critique[0] is False
                assert all(calls_with_critique[1:])


class TestArenaExecutorCritiqueGeneration:
    """Test critique generation from evaluation results."""

    def test_generates_critique_from_evaluation(self):
        """Test executor generates actionable critique from evaluation."""
        from bulletproof_green.arena_executor import ArenaExecutor

        executor = ArenaExecutor(purple_agent_url="http://localhost:8001")

        eval_result = {
            "classification": "NON_QUALIFYING",
            "risk_score": 50,
            "redline": {
                "issues": [
                    {"category": "vagueness", "suggestion": "Add specific metrics"},
                ]
            },
        }

        critique = executor._generate_critique(eval_result)

        assert critique is not None
        assert len(critique) > 0
