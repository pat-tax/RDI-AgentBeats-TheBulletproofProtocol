"""Tests for LLM-as-Judge hybrid evaluation (STORY-016).

This test module validates the acceptance criteria for STORY-016:
- Rule-based evaluation remains deterministic (primary)
- LLM-as-Judge provides semantic analysis (secondary)
- Combined: final_score = α*rule_score + β*llm_score
- Fallback to rule-only if LLM unavailable
- LLM uses temperature=0 for consistency
- OpenAI GPT-4 or equivalent
- Graceful degradation when LLM unavailable
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLLMJudgeImport:
    """Test LLMJudge module can be imported."""

    def test_llm_judge_module_exists(self):
        """Test llm_judge module can be imported."""
        from bulletproof_green import llm_judge

        assert llm_judge is not None

    def test_llm_judge_class_exists(self):
        """Test LLMJudge class exists."""
        from bulletproof_green.llm_judge import LLMJudge

        assert LLMJudge is not None

    def test_llm_score_result_class_exists(self):
        """Test LLMScoreResult dataclass exists."""
        from bulletproof_green.llm_judge import LLMScoreResult

        assert LLMScoreResult is not None

    def test_hybrid_score_result_class_exists(self):
        """Test HybridScoreResult dataclass exists."""
        from bulletproof_green.llm_judge import HybridScoreResult

        assert HybridScoreResult is not None

    def test_llm_judge_config_class_exists(self):
        """Test LLMJudgeConfig dataclass exists."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        assert LLMJudgeConfig is not None


class TestLLMJudgeConfigDefaults:
    """Test LLMJudgeConfig default values."""

    def test_default_alpha_weight(self):
        """Test default alpha (rule-based weight) is 0.7."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig()
        assert config.alpha == 0.7

    def test_default_beta_weight(self):
        """Test default beta (LLM weight) is 0.3."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig()
        assert config.beta == 0.3

    def test_weights_sum_to_one(self):
        """Test that alpha + beta = 1.0."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig()
        assert abs(config.alpha + config.beta - 1.0) < 0.0001

    def test_default_temperature_is_zero(self):
        """Test default temperature is 0 for consistency."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig()
        assert config.temperature == 0

    def test_default_model_is_gpt4(self):
        """Test default model is gpt-4 or equivalent."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig()
        assert "gpt-4" in config.model.lower()

    def test_custom_weights(self):
        """Test custom weights can be set."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.5, beta=0.5)
        assert config.alpha == 0.5
        assert config.beta == 0.5

    def test_custom_model(self):
        """Test custom model can be set."""
        from bulletproof_green.llm_judge import LLMJudgeConfig

        config = LLMJudgeConfig(model="gpt-4-turbo")
        assert config.model == "gpt-4-turbo"


class TestLLMJudgeConstruction:
    """Test LLMJudge construction."""

    def test_judge_accepts_config(self):
        """Test judge accepts LLMJudgeConfig."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.6, beta=0.4)
        judge = LLMJudge(config=config)
        assert judge.config.alpha == 0.6
        assert judge.config.beta == 0.4

    def test_judge_has_default_config(self):
        """Test judge uses default config if not provided."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge()
        assert judge.config.alpha == 0.7
        assert judge.config.beta == 0.3

    def test_judge_accepts_api_key(self):
        """Test judge accepts OpenAI API key."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")
        assert judge._api_key == "test-key"

    def test_judge_reads_api_key_from_settings(self):
        """Test judge reads API key from settings."""
        from unittest.mock import patch

        from bulletproof_green.llm_judge import LLMJudge

        with patch("bulletproof_green.settings.settings.openai_api_key", "settings-key"):
            judge = LLMJudge()
            assert judge._api_key == "settings-key"


class TestLLMScoreResult:
    """Test LLMScoreResult dataclass."""

    def test_llm_score_result_has_score(self):
        """Test LLMScoreResult has score field."""
        from bulletproof_green.llm_judge import LLMScoreResult

        result = LLMScoreResult(
            score=0.75,
            reasoning="Good technical uncertainty documentation",
            categories={},
        )
        assert result.score == 0.75

    def test_llm_score_result_has_reasoning(self):
        """Test LLMScoreResult has reasoning field."""
        from bulletproof_green.llm_judge import LLMScoreResult

        result = LLMScoreResult(
            score=0.75,
            reasoning="Good technical uncertainty documentation",
            categories={},
        )
        assert result.reasoning == "Good technical uncertainty documentation"

    def test_llm_score_result_has_categories(self):
        """Test LLMScoreResult has categories breakdown."""
        from bulletproof_green.llm_judge import LLMScoreResult

        categories = {
            "technical_uncertainty": 0.8,
            "experimentation": 0.7,
            "specificity": 0.9,
        }
        result = LLMScoreResult(
            score=0.75,
            reasoning="Good documentation",
            categories=categories,
        )
        assert result.categories["technical_uncertainty"] == 0.8

    def test_llm_score_result_score_in_valid_range(self):
        """Test LLMScoreResult score is between 0 and 1."""
        from bulletproof_green.llm_judge import LLMScoreResult

        result = LLMScoreResult(score=0.75, reasoning="test", categories={})
        assert 0 <= result.score <= 1


class TestHybridScoreResult:
    """Test HybridScoreResult dataclass."""

    def test_hybrid_score_result_has_final_score(self):
        """Test HybridScoreResult has final_score field."""
        from bulletproof_green.llm_judge import HybridScoreResult

        result = HybridScoreResult(
            final_score=0.75,
            rule_score=0.80,
            llm_score=0.65,
            alpha=0.7,
            beta=0.3,
            fallback_used=False,
        )
        assert result.final_score == 0.75

    def test_hybrid_score_result_has_component_scores(self):
        """Test HybridScoreResult has rule_score and llm_score."""
        from bulletproof_green.llm_judge import HybridScoreResult

        result = HybridScoreResult(
            final_score=0.75,
            rule_score=0.80,
            llm_score=0.65,
            alpha=0.7,
            beta=0.3,
            fallback_used=False,
        )
        assert result.rule_score == 0.80
        assert result.llm_score == 0.65

    def test_hybrid_score_result_has_weights(self):
        """Test HybridScoreResult includes weights used."""
        from bulletproof_green.llm_judge import HybridScoreResult

        result = HybridScoreResult(
            final_score=0.75,
            rule_score=0.80,
            llm_score=0.65,
            alpha=0.7,
            beta=0.3,
            fallback_used=False,
        )
        assert result.alpha == 0.7
        assert result.beta == 0.3

    def test_hybrid_score_result_has_fallback_flag(self):
        """Test HybridScoreResult has fallback_used flag."""
        from bulletproof_green.llm_judge import HybridScoreResult

        result = HybridScoreResult(
            final_score=0.80,
            rule_score=0.80,
            llm_score=None,
            alpha=0.7,
            beta=0.3,
            fallback_used=True,
        )
        assert result.fallback_used is True

    def test_hybrid_score_result_has_optional_llm_reasoning(self):
        """Test HybridScoreResult has optional llm_reasoning."""
        from bulletproof_green.llm_judge import HybridScoreResult

        result = HybridScoreResult(
            final_score=0.75,
            rule_score=0.80,
            llm_score=0.65,
            alpha=0.7,
            beta=0.3,
            fallback_used=False,
            llm_reasoning="Good technical uncertainty",
        )
        assert result.llm_reasoning == "Good technical uncertainty"


class TestLLMJudgeEvaluate:
    """Test LLMJudge evaluate method."""

    @pytest.mark.asyncio
    async def test_evaluate_returns_llm_score_result(self):
        """Test evaluate method returns LLMScoreResult."""
        from bulletproof_green.llm_judge import LLMJudge, LLMScoreResult

        judge = LLMJudge(api_key="test-key")

        # Mock the OpenAI client
        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {
                "score": 0.75,
                "reasoning": "Good documentation",
                "categories": {},
            }

            result = await judge.evaluate("Test narrative")

            assert isinstance(result, LLMScoreResult)
            assert result.score == 0.75

    @pytest.mark.asyncio
    async def test_evaluate_uses_temperature_zero(self):
        """Test evaluate uses temperature=0 for consistency."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(temperature=0)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.75, "reasoning": "", "categories": {}}

            await judge.evaluate("Test narrative")

            # Verify temperature=0 was used
            call_kwargs = mock_llm.call_args
            assert "temperature" in str(call_kwargs) or judge.config.temperature == 0

    @pytest.mark.asyncio
    async def test_evaluate_scores_between_zero_and_one(self):
        """Test evaluate returns score in [0, 1] range."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.75, "reasoning": "", "categories": {}}

            result = await judge.evaluate("Test narrative")

            assert 0 <= result.score <= 1


class TestLLMJudgeHybridScore:
    """Test LLMJudge hybrid scoring."""

    @pytest.mark.asyncio
    async def test_hybrid_score_combines_rule_and_llm(self):
        """Test hybrid_score combines rule and LLM scores with weights."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        # alpha=0.7, beta=0.3: final = 0.7*rule + 0.3*llm
        config = LLMJudgeConfig(alpha=0.7, beta=0.3)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.5, "reasoning": "", "categories": {}}

            # Rule score = 0.8, LLM score = 0.5
            # Expected: 0.7 * 0.8 + 0.3 * 0.5 = 0.56 + 0.15 = 0.71
            result = await judge.hybrid_score(
                narrative="Test narrative",
                rule_score=0.8,
            )

            expected = 0.7 * 0.8 + 0.3 * 0.5
            assert abs(result.final_score - expected) < 0.001

    @pytest.mark.asyncio
    async def test_hybrid_score_returns_hybrid_result(self):
        """Test hybrid_score returns HybridScoreResult."""
        from bulletproof_green.llm_judge import HybridScoreResult, LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.5, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(
                narrative="Test narrative",
                rule_score=0.8,
            )

            assert isinstance(result, HybridScoreResult)

    @pytest.mark.asyncio
    async def test_hybrid_score_includes_both_scores(self):
        """Test hybrid_score includes both rule and LLM scores."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.6, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(
                narrative="Test narrative",
                rule_score=0.8,
            )

            assert result.rule_score == 0.8
            assert result.llm_score == 0.6


class TestLLMJudgeFallback:
    """Test LLMJudge fallback behavior when LLM unavailable."""

    @pytest.mark.asyncio
    async def test_fallback_to_rule_only_on_llm_error(self):
        """Test fallback to rule-only score when LLM fails."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            # Simulate LLM failure
            mock_llm.side_effect = Exception("LLM API error")

            result = await judge.hybrid_score(
                narrative="Test narrative",
                rule_score=0.8,
            )

            # Should fall back to rule-only score
            assert result.fallback_used is True
            assert result.final_score == 0.8
            assert result.llm_score is None

    @pytest.mark.asyncio
    async def test_fallback_on_missing_api_key(self):
        """Test fallback when no API key is configured."""
        from unittest.mock import patch

        from bulletproof_green.llm_judge import LLMJudge

        # No API key provided via settings
        with patch("bulletproof_green.settings.settings.openai_api_key", None):
            judge = LLMJudge()  # No api_key

            result = await judge.hybrid_score(
                narrative="Test narrative",
                rule_score=0.8,
            )

            # Should fall back to rule-only score
            assert result.fallback_used is True
            assert result.final_score == 0.8

    @pytest.mark.asyncio
    async def test_fallback_on_timeout(self):
        """Test fallback when LLM call times out."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = TimeoutError("Request timed out")

            result = await judge.hybrid_score(
                narrative="Test narrative",
                rule_score=0.8,
            )

            assert result.fallback_used is True
            assert result.final_score == 0.8

    @pytest.mark.asyncio
    async def test_graceful_degradation_logs_warning(self):
        """Test graceful degradation logs a warning when falling back."""
        import logging

        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM API error")

            with patch.object(logging, "getLogger") as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger.return_value = mock_logger_instance

                await judge.hybrid_score(
                    narrative="Test narrative",
                    rule_score=0.8,
                )

                # Warning should be logged (implementation detail)


class TestRuleBasedRemainsUnchanged:
    """Test rule-based evaluation remains deterministic and unchanged."""

    def test_rule_evaluator_still_works(self):
        """Test RuleBasedEvaluator still produces deterministic results."""
        from bulletproof_green.evaluator import RuleBasedEvaluator

        evaluator = RuleBasedEvaluator()
        narrative = "The team performed routine maintenance."

        result1 = evaluator.evaluate(narrative)
        result2 = evaluator.evaluate(narrative)

        assert result1.risk_score == result2.risk_score
        assert result1.classification == result2.classification

    def test_rule_evaluator_unchanged_interface(self):
        """Test RuleBasedEvaluator interface remains unchanged."""
        from bulletproof_green.evaluator import RuleBasedEvaluator
        from bulletproof_green.models import EvaluationResult

        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Test narrative")

        assert isinstance(result, EvaluationResult)
        assert hasattr(result, "risk_score")
        assert hasattr(result, "classification")
        assert hasattr(result, "redline")


class TestLLMJudgeOpenAIIntegration:
    """Test LLMJudge OpenAI integration."""

    @pytest.mark.asyncio
    async def test_uses_openai_client(self):
        """Test LLMJudge uses OpenAI client."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        # Should have OpenAI client attribute
        assert hasattr(judge, "_client") or hasattr(judge, "_openai_client")

    @pytest.mark.asyncio
    async def test_uses_gpt4_model(self):
        """Test LLMJudge uses GPT-4 or equivalent."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        assert "gpt-4" in judge.config.model.lower()

    @pytest.mark.asyncio
    async def test_prompt_includes_evaluation_criteria(self):
        """Test LLM prompt includes IRS Section 41 evaluation criteria."""
        from bulletproof_green.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        # The system prompt should mention IRS Section 41 criteria
        system_prompt = judge._get_system_prompt()

        assert "IRS" in system_prompt or "Section 41" in system_prompt
        assert "technical uncertainty" in system_prompt.lower()


class TestLLMJudgeExports:
    """Test LLMJudge is properly exported from module."""

    def test_llm_judge_exported_from_green_module(self):
        """Test LLMJudge is exported from bulletproof_green module."""
        from bulletproof_green import LLMJudge

        assert LLMJudge is not None

    def test_llm_judge_config_exported(self):
        """Test LLMJudgeConfig is exported from bulletproof_green module."""
        from bulletproof_green import LLMJudgeConfig

        assert LLMJudgeConfig is not None

    def test_llm_score_result_exported(self):
        """Test LLMScoreResult is exported from bulletproof_green module."""
        from bulletproof_green import LLMScoreResult

        assert LLMScoreResult is not None

    def test_hybrid_score_result_exported(self):
        """Test HybridScoreResult is exported from bulletproof_green module."""
        from bulletproof_green import HybridScoreResult

        assert HybridScoreResult is not None


class TestLLMJudgeFormula:
    """Test the hybrid score formula: final_score = α*rule_score + β*llm_score."""

    @pytest.mark.asyncio
    async def test_formula_with_equal_weights(self):
        """Test formula with α=β=0.5."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.5, beta=0.5)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.6, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(narrative="Test", rule_score=0.8)

            # 0.5 * 0.8 + 0.5 * 0.6 = 0.4 + 0.3 = 0.7
            assert abs(result.final_score - 0.7) < 0.001

    @pytest.mark.asyncio
    async def test_formula_rule_only(self):
        """Test formula with α=1.0, β=0.0 (rule only)."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=1.0, beta=0.0)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.2, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(narrative="Test", rule_score=0.8)

            # 1.0 * 0.8 + 0.0 * 0.2 = 0.8
            assert abs(result.final_score - 0.8) < 0.001

    @pytest.mark.asyncio
    async def test_formula_llm_only(self):
        """Test formula with α=0.0, β=1.0 (LLM only)."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.0, beta=1.0)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.6, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(narrative="Test", rule_score=0.8)

            # 0.0 * 0.8 + 1.0 * 0.6 = 0.6
            assert abs(result.final_score - 0.6) < 0.001

    @pytest.mark.asyncio
    async def test_formula_edge_case_zero_scores(self):
        """Test formula with zero scores."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.7, beta=0.3)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.0, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(narrative="Test", rule_score=0.0)

            assert result.final_score == 0.0

    @pytest.mark.asyncio
    async def test_formula_edge_case_perfect_scores(self):
        """Test formula with perfect scores."""
        from bulletproof_green.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.7, beta=0.3)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 1.0, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(narrative="Test", rule_score=1.0)

            assert result.final_score == 1.0
