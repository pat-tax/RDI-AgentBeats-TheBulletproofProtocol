"""Tests for LLM-as-Judge hybrid evaluation (STORY-016).

Validates core behavior:
- Hybrid scoring formula: final_score = α*rule_score + β*llm_score
- Fallback to rule-only when LLM unavailable
- OpenAI integration with temperature=0
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestLLMJudgeConstruction:
    """Test LLMJudge construction."""

    def test_judge_accepts_api_key(self):
        """Test judge accepts OpenAI API key."""
        from bulletproof_green.evals.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")
        assert judge._api_key == "test-key"

    def test_judge_reads_api_key_from_settings(self):
        """Test judge reads API key from settings."""
        from bulletproof_green.evals.llm_judge import LLMJudge

        with patch("bulletproof_green.settings.settings.llm.api_key", "settings-key"):
            judge = LLMJudge()
            assert judge._api_key == "settings-key"


class TestLLMJudgeHybridScore:
    """Test LLMJudge hybrid scoring formula."""

    @pytest.mark.asyncio
    async def test_hybrid_score_formula(self):
        """Test hybrid_score applies formula: final = α*rule + β*llm."""
        from bulletproof_green.evals.llm_judge import LLMJudge, LLMJudgeConfig

        config = LLMJudgeConfig(alpha=0.7, beta=0.3)
        judge = LLMJudge(config=config, api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {"score": 0.5, "reasoning": "", "categories": {}}

            result = await judge.hybrid_score(narrative="Test", rule_score=0.8)

            # 0.7 * 0.8 + 0.3 * 0.5 = 0.56 + 0.15 = 0.71
            expected = 0.7 * 0.8 + 0.3 * 0.5
            assert abs(result.final_score - expected) < 0.001
            assert result.rule_score == 0.8
            assert result.llm_score == 0.5
            assert result.fallback_used is False


class TestLLMJudgeFallback:
    """Test LLMJudge fallback behavior when LLM unavailable."""

    @pytest.mark.asyncio
    async def test_fallback_on_llm_error(self):
        """Test fallback to rule-only score when LLM fails."""
        from bulletproof_green.evals.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")

        with patch.object(judge, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM API error")

            result = await judge.hybrid_score(narrative="Test", rule_score=0.8)

            assert result.fallback_used is True
            assert result.final_score == 0.8
            assert result.llm_score is None

    @pytest.mark.asyncio
    async def test_fallback_on_missing_api_key(self):
        """Test fallback when no API key is configured."""
        from bulletproof_green.evals.llm_judge import LLMJudge

        with patch("bulletproof_green.settings.settings.llm.api_key", None):
            judge = LLMJudge()

            result = await judge.hybrid_score(narrative="Test", rule_score=0.8)

            assert result.fallback_used is True
            assert result.final_score == 0.8


class TestLLMJudgeOpenAIIntegration:
    """Test LLMJudge OpenAI integration."""

    def test_prompt_includes_evaluation_criteria(self):
        """Test LLM prompt includes IRS Section 41 evaluation criteria."""
        from bulletproof_green.evals.llm_judge import LLMJudge

        judge = LLMJudge(api_key="test-key")
        system_prompt = judge._get_system_prompt()

        assert "IRS" in system_prompt or "Section 41" in system_prompt
        assert "technical uncertainty" in system_prompt.lower()


class TestRuleBasedRemainsUnchanged:
    """Test rule-based evaluation remains deterministic."""

    def test_rule_evaluator_deterministic(self):
        """Test RuleBasedEvaluator produces deterministic results."""
        from bulletproof_green.evals.evaluator import RuleBasedEvaluator

        evaluator = RuleBasedEvaluator()
        narrative = "The team performed routine maintenance."

        result1 = evaluator.evaluate(narrative)
        result2 = evaluator.evaluate(narrative)

        assert result1.risk_score == result2.risk_score
        assert result1.classification == result2.classification
