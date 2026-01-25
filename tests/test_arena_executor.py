"""Tests for Arena Mode orchestration (STORY-015).

This test module validates the acceptance criteria for STORY-015:
- Green agent accepts mode=arena parameter
- Calls Purple agent via A2A tasks/send for each iteration
- Purple agent receives critique and regenerates
- Loop terminates when risk_score < target OR max_iterations reached
- Returns ArenaResult with full iteration history
- Configurable: max_iterations (default: 5), target_risk_score (default: 20)
- Task state tracking per iteration
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest


class TestArenaExecutorImport:
    """Test ArenaExecutor module can be imported."""

    def test_arena_executor_module_exists(self):
        """Test arena_executor module can be imported."""
        from bulletproof_green import arena_executor

        assert arena_executor is not None

    def test_arena_executor_class_exists(self):
        """Test ArenaExecutor class exists."""
        from bulletproof_green.arena_executor import ArenaExecutor

        assert ArenaExecutor is not None

    def test_arena_result_class_exists(self):
        """Test ArenaResult dataclass exists."""
        from bulletproof_green.arena_executor import ArenaResult

        assert ArenaResult is not None

    def test_iteration_record_class_exists(self):
        """Test IterationRecord dataclass exists."""
        from bulletproof_green.arena_executor import IterationRecord

        assert IterationRecord is not None

    def test_arena_config_class_exists(self):
        """Test ArenaConfig dataclass exists."""
        from bulletproof_green.arena_executor import ArenaConfig

        assert ArenaConfig is not None


class TestArenaConfigDefaults:
    """Test ArenaConfig default values."""

    def test_default_max_iterations(self):
        """Test default max_iterations is 5."""
        from bulletproof_green.arena_executor import ArenaConfig

        config = ArenaConfig()
        assert config.max_iterations == 5

    def test_default_target_risk_score(self):
        """Test default target_risk_score is 20."""
        from bulletproof_green.arena_executor import ArenaConfig

        config = ArenaConfig()
        assert config.target_risk_score == 20

    def test_custom_max_iterations(self):
        """Test custom max_iterations can be set."""
        from bulletproof_green.arena_executor import ArenaConfig

        config = ArenaConfig(max_iterations=10)
        assert config.max_iterations == 10

    def test_custom_target_risk_score(self):
        """Test custom target_risk_score can be set."""
        from bulletproof_green.arena_executor import ArenaConfig

        config = ArenaConfig(target_risk_score=15)
        assert config.target_risk_score == 15


class TestArenaExecutorConstruction:
    """Test ArenaExecutor construction."""

    def test_executor_accepts_purple_url(self):
        """Test executor accepts Purple agent URL."""
        from bulletproof_green.arena_executor import ArenaExecutor

        executor = ArenaExecutor(purple_agent_url="http://localhost:8001")
        assert executor.purple_agent_url == "http://localhost:8001"

    def test_executor_accepts_config(self):
        """Test executor accepts ArenaConfig."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=3, target_risk_score=10)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )
        assert executor.config.max_iterations == 3
        assert executor.config.target_risk_score == 10

    def test_executor_has_default_config(self):
        """Test executor uses default config if not provided."""
        from bulletproof_green.arena_executor import ArenaExecutor

        executor = ArenaExecutor(purple_agent_url="http://localhost:8001")
        assert executor.config.max_iterations == 5
        assert executor.config.target_risk_score == 20


class TestIterationRecord:
    """Test IterationRecord dataclass."""

    def test_iteration_record_has_iteration_number(self):
        """Test IterationRecord has iteration_number field."""
        from bulletproof_green.arena_executor import IterationRecord

        record = IterationRecord(
            iteration_number=1,
            narrative="Test narrative",
            risk_score=50,
            state="completed",
        )
        assert record.iteration_number == 1

    def test_iteration_record_has_narrative(self):
        """Test IterationRecord has narrative field."""
        from bulletproof_green.arena_executor import IterationRecord

        record = IterationRecord(
            iteration_number=1,
            narrative="Test narrative",
            risk_score=50,
            state="completed",
        )
        assert record.narrative == "Test narrative"

    def test_iteration_record_has_risk_score(self):
        """Test IterationRecord has risk_score field."""
        from bulletproof_green.arena_executor import IterationRecord

        record = IterationRecord(
            iteration_number=1,
            narrative="Test narrative",
            risk_score=50,
            state="completed",
        )
        assert record.risk_score == 50

    def test_iteration_record_has_state(self):
        """Test IterationRecord has state field for task tracking."""
        from bulletproof_green.arena_executor import IterationRecord

        record = IterationRecord(
            iteration_number=1,
            narrative="Test narrative",
            risk_score=50,
            state="completed",
        )
        assert record.state == "completed"

    def test_iteration_record_has_optional_critique(self):
        """Test IterationRecord has optional critique field."""
        from bulletproof_green.arena_executor import IterationRecord

        record = IterationRecord(
            iteration_number=1,
            narrative="Test narrative",
            risk_score=50,
            state="completed",
            critique="Improve specificity",
        )
        assert record.critique == "Improve specificity"

    def test_iteration_record_has_optional_evaluation(self):
        """Test IterationRecord has optional evaluation result."""
        from bulletproof_green.arena_executor import IterationRecord

        eval_data = {"classification": "NON_QUALIFYING", "risk_category": "HIGH"}
        record = IterationRecord(
            iteration_number=1,
            narrative="Test narrative",
            risk_score=50,
            state="completed",
            evaluation=eval_data,
        )
        assert record.evaluation == eval_data


class TestArenaResult:
    """Test ArenaResult dataclass."""

    def test_arena_result_has_success_flag(self):
        """Test ArenaResult has success field."""
        from bulletproof_green.arena_executor import ArenaResult

        result = ArenaResult(
            success=True,
            iterations=[],
            total_iterations=1,
            final_risk_score=15,
        )
        assert result.success is True

    def test_arena_result_has_iterations_list(self):
        """Test ArenaResult has iterations list."""
        from bulletproof_green.arena_executor import ArenaResult, IterationRecord

        iter_record = IterationRecord(
            iteration_number=1,
            narrative="Test",
            risk_score=15,
            state="completed",
        )
        result = ArenaResult(
            success=True,
            iterations=[iter_record],
            total_iterations=1,
            final_risk_score=15,
        )
        assert len(result.iterations) == 1
        assert result.iterations[0].iteration_number == 1

    def test_arena_result_has_total_iterations(self):
        """Test ArenaResult has total_iterations count."""
        from bulletproof_green.arena_executor import ArenaResult

        result = ArenaResult(
            success=True,
            iterations=[],
            total_iterations=3,
            final_risk_score=15,
        )
        assert result.total_iterations == 3

    def test_arena_result_has_final_risk_score(self):
        """Test ArenaResult has final_risk_score."""
        from bulletproof_green.arena_executor import ArenaResult

        result = ArenaResult(
            success=True,
            iterations=[],
            total_iterations=1,
            final_risk_score=15,
        )
        assert result.final_risk_score == 15

    def test_arena_result_has_optional_final_narrative(self):
        """Test ArenaResult has optional final_narrative."""
        from bulletproof_green.arena_executor import ArenaResult

        result = ArenaResult(
            success=True,
            iterations=[],
            total_iterations=1,
            final_risk_score=15,
            final_narrative="Final qualifying narrative",
        )
        assert result.final_narrative == "Final qualifying narrative"

    def test_arena_result_has_optional_termination_reason(self):
        """Test ArenaResult has optional termination_reason."""
        from bulletproof_green.arena_executor import ArenaResult

        result = ArenaResult(
            success=True,
            iterations=[],
            total_iterations=1,
            final_risk_score=15,
            termination_reason="target_reached",
        )
        assert result.termination_reason == "target_reached"


class TestArenaExecutorRun:
    """Test ArenaExecutor run method."""

    @pytest.mark.asyncio
    async def test_run_returns_arena_result(self):
        """Test run method returns ArenaResult."""
        from bulletproof_green.arena_executor import ArenaExecutor, ArenaResult

        executor = ArenaExecutor(purple_agent_url="http://localhost:8001")

        # Mock the A2A client and evaluator
        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = (
                "Qualifying narrative with technical uncertainty and 45ms latency",
                15,  # risk_score below target
                {},
            )

            result = await executor.run(initial_context="Generate a narrative")

            assert isinstance(result, ArenaResult)

    @pytest.mark.asyncio
    async def test_run_stops_when_target_reached(self):
        """Test run stops when risk_score < target_risk_score."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=5, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        # First iteration returns qualifying narrative
        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = ("Qualifying narrative", 15, {})

            result = await executor.run(initial_context="Generate a narrative")

            # Should stop after first iteration since risk_score < target
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

        # All iterations return non-qualifying narratives
        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = ("Non-qualifying narrative", 50, {})

            result = await executor.run(initial_context="Generate a narrative")

            # Should stop after max_iterations
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

        # First two iterations fail, third succeeds
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

            # All iterations should be recorded
            assert len(result.iterations) == result.total_iterations
            # Verify iteration numbers
            for i, iteration in enumerate(result.iterations):
                assert iteration.iteration_number == i + 1


class TestArenaExecutorA2AIntegration:
    """Test ArenaExecutor A2A integration with Purple Agent."""

    @pytest.mark.asyncio
    async def test_calls_purple_agent_via_a2a(self):
        """Test executor calls Purple agent via A2A tasks/send."""
        from bulletproof_green.arena_executor import ArenaExecutor

        executor = ArenaExecutor(purple_agent_url="http://localhost:8001")

        with patch.object(executor, "_call_purple_agent", new_callable=AsyncMock) as mock_purple:
            mock_purple.return_value = "Generated narrative"

            with patch.object(executor, "_evaluate_narrative") as mock_eval:
                mock_eval.return_value = (15, {})  # Qualifying score

                await executor.run(initial_context="Generate a narrative")

                # Should have called Purple agent
                mock_purple.assert_called()

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
                # First two iterations fail, third succeeds
                mock_eval.side_effect = [
                    (50, {"issues": ["vagueness"]}),
                    (35, {"issues": ["specificity"]}),
                    (15, {}),
                ]

                await executor.run(initial_context="Generate a narrative")

                # First call should not have critique
                assert calls_with_critique[0] is False
                # Subsequent calls should have critique
                assert all(calls_with_critique[1:])


class TestArenaExecutorTaskStateTracking:
    """Test task state tracking per iteration."""

    @pytest.mark.asyncio
    async def test_iteration_states_tracked(self):
        """Test each iteration has proper state tracking."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=2, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = ("Narrative", 50, {})

            result = await executor.run(initial_context="Generate a narrative")

            # All iterations should have state
            for iteration in result.iterations:
                assert iteration.state in ["pending", "running", "completed", "failed"]

    @pytest.mark.asyncio
    async def test_completed_iterations_have_completed_state(self):
        """Test completed iterations have 'completed' state."""
        from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

        config = ArenaConfig(max_iterations=1, target_risk_score=20)
        executor = ArenaExecutor(
            purple_agent_url="http://localhost:8001",
            config=config,
        )

        with patch.object(executor, "_run_iteration", new_callable=AsyncMock) as mock_iter:
            mock_iter.return_value = ("Narrative", 15, {})

            result = await executor.run(initial_context="Generate a narrative")

            assert result.iterations[0].state == "completed"


class TestArenaExecutorCritiqueGeneration:
    """Test critique generation from evaluation results."""

    @pytest.mark.asyncio
    async def test_generates_critique_from_evaluation(self):
        """Test executor generates actionable critique from evaluation."""
        from bulletproof_green.arena_executor import ArenaExecutor

        executor = ArenaExecutor(purple_agent_url="http://localhost:8001")

        eval_result = {
            "classification": "NON_QUALIFYING",
            "risk_score": 50,
            "redline": {
                "issues": [
                    {"category": "vagueness", "suggestion": "Add specific metrics"},
                    {"category": "experimentation", "suggestion": "Document failures"},
                ]
            },
        }

        critique = executor._generate_critique(eval_result)

        assert critique is not None
        assert len(critique) > 0


class TestArenaExecutorExports:
    """Test ArenaExecutor is properly exported from module."""

    def test_arena_executor_exported_from_green_module(self):
        """Test ArenaExecutor is exported from bulletproof_green module."""
        from bulletproof_green import ArenaExecutor

        assert ArenaExecutor is not None

    def test_arena_result_exported(self):
        """Test ArenaResult is exported from bulletproof_green module."""
        from bulletproof_green import ArenaResult

        assert ArenaResult is not None

    def test_arena_config_exported(self):
        """Test ArenaConfig is exported from bulletproof_green module."""
        from bulletproof_green import ArenaConfig

        assert ArenaConfig is not None

    def test_iteration_record_exported(self):
        """Test IterationRecord is exported from bulletproof_green module."""
        from bulletproof_green import IterationRecord

        assert IterationRecord is not None
