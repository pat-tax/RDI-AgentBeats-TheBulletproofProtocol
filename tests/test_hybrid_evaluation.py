"""Tests for hybrid evaluation (rule-based + LLM scoring integration).

Tests STORY-026: Integration of LLM judge with rule-based scoring.

Acceptance criteria:
- Evaluator uses both rule-based and LLM scoring
- Scorer combines rule-based and LLM scores
- Weighted combination or fallback strategy implemented
- Integration tests verify hybrid approach
"""

import pytest

from bulletproof_green.evals.evaluator import RuleBasedEvaluator
from bulletproof_green.evals.llm_judge import LLMJudge
from bulletproof_green.evals.scorer import AgentBeatsScorer
from bulletproof_green.models import LLMJudgeConfig


@pytest.fixture
def sample_narrative():
    """Sample qualifying narrative for testing."""
    return """
    We hypothesized that a novel parallel processing algorithm could reduce latency
    from 150ms to under 50ms for real-time data processing. Initial experiments using
    a lock-free queue design failed with 200ms latency due to cache coherency issues.
    We iterated through 3 alternative approaches: work-stealing, SPMC channels, and
    atomic ring buffers. The ring buffer approach achieved 45ms latency after
    5 iterations of optimization.
    """


@pytest.fixture
def sample_non_qualifying_narrative():
    """Sample non-qualifying narrative for testing."""
    return """
    We implemented routine debugging procedures to fix bugs in the existing system.
    The market demanded better performance to increase revenue and profit margins.
    We made significant improvements and things work much better now. The solution
    was adapted from standard procedures and vendor software.
    """


class TestHybridEvaluatorIntegration:
    """Test that evaluator supports hybrid evaluation mode."""

    def test_evaluator_accepts_llm_judge(self, sample_narrative):
        """Test that evaluator can accept optional LLM judge for hybrid mode."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        llm_judge = LLMJudge(config=LLMJudgeConfig(alpha=0.7, beta=0.3), api_key=None)

        # Act & Assert
        # Evaluator should accept llm_judge parameter
        result = evaluator.evaluate(sample_narrative, llm_judge=llm_judge)

        # Should return EvaluationResult with hybrid flag
        assert hasattr(result, "hybrid_used")
        assert result.hybrid_used is False  # No API key, so fallback

    @pytest.mark.asyncio
    async def test_evaluator_runs_hybrid_evaluation_when_llm_available(
        self, sample_narrative, monkeypatch
    ):
        """Test that evaluator uses LLM when available."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        llm_judge = LLMJudge(
            config=LLMJudgeConfig(alpha=0.7, beta=0.3),
            api_key="test-key",
        )

        # Mock LLM response
        async def mock_evaluate(narrative):
            from bulletproof_green.models import LLMScoreResult
            return LLMScoreResult(
                score=0.85,
                reasoning="Strong evidence of technical uncertainty and experimentation",
                categories={
                    "technical_uncertainty": 0.9,
                    "experimentation": 0.8,
                    "technological_nature": 0.85,
                    "business_component": 0.85,
                },
            )

        monkeypatch.setattr(llm_judge, "evaluate", mock_evaluate)

        # Act
        result = await evaluator.evaluate_async(sample_narrative, llm_judge=llm_judge)

        # Assert
        assert result.hybrid_used is True
        assert hasattr(result, "llm_score")
        assert result.llm_score is not None

    def test_evaluator_falls_back_to_rules_only_when_llm_unavailable(
        self, sample_narrative
    ):
        """Test graceful fallback when LLM is unavailable."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        llm_judge = LLMJudge(config=LLMJudgeConfig(), api_key=None)  # No API key

        # Act
        result = evaluator.evaluate(sample_narrative, llm_judge=llm_judge)

        # Assert
        assert result.hybrid_used is False
        assert result.llm_score is None


class TestHybridScorerIntegration:
    """Test that scorer combines rule-based and LLM scores."""

    @pytest.mark.asyncio
    async def test_scorer_combines_rule_and_llm_scores(
        self, sample_narrative, monkeypatch
    ):
        """Test weighted combination of rule and LLM scores."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()
        llm_judge = LLMJudge(
            config=LLMJudgeConfig(alpha=0.6, beta=0.4),
            api_key="test-key",
        )

        # Mock LLM response
        async def mock_evaluate(narrative):
            from bulletproof_green.models import LLMScoreResult
            return LLMScoreResult(
                score=0.8,
                reasoning="Good compliance",
                categories={},
            )

        monkeypatch.setattr(llm_judge, "evaluate", mock_evaluate)

        # Act
        eval_result = await evaluator.evaluate_async(sample_narrative, llm_judge=llm_judge)
        score_result = scorer.score(eval_result)

        # Assert
        # Scorer should use hybrid score when available
        assert hasattr(score_result, "hybrid_score")
        assert score_result.hybrid_score is not None

        # Verify weighted combination: final = α*rule + β*llm
        # With α=0.6, β=0.4, rule_score and llm_score=0.8
        # final should be between the two values
        assert 0.0 <= score_result.hybrid_score <= 1.0

    def test_scorer_uses_rule_only_when_no_llm_score(self, sample_narrative):
        """Test scorer uses rule-only score when LLM unavailable."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()
        llm_judge = LLMJudge(config=LLMJudgeConfig(), api_key=None)

        # Act
        eval_result = evaluator.evaluate(sample_narrative, llm_judge=llm_judge)
        score_result = scorer.score(eval_result)

        # Assert
        # When no LLM score, hybrid_score should equal overall_score
        assert score_result.hybrid_score == score_result.overall_score


class TestHybridEvaluationEndToEnd:
    """End-to-end tests for hybrid evaluation workflow."""

    @pytest.mark.asyncio
    async def test_qualifying_narrative_hybrid_evaluation(
        self, sample_narrative, monkeypatch
    ):
        """Test hybrid evaluation on qualifying narrative."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()
        llm_judge = LLMJudge(
            config=LLMJudgeConfig(alpha=0.7, beta=0.3),
            api_key="test-key",
        )

        # Mock LLM to agree with rule-based (qualifying)
        async def mock_evaluate(narrative):
            from bulletproof_green.models import LLMScoreResult
            return LLMScoreResult(
                score=0.9,
                reasoning="Strong evidence of qualified research",
                categories={},
            )

        monkeypatch.setattr(llm_judge, "evaluate", mock_evaluate)

        # Act
        eval_result = await evaluator.evaluate_async(sample_narrative, llm_judge=llm_judge)
        score_result = scorer.score(eval_result)

        # Assert
        assert eval_result.classification == "QUALIFYING"
        assert eval_result.risk_score < 20
        assert eval_result.hybrid_used is True
        assert score_result.hybrid_score > 0.7  # Should be high

    @pytest.mark.asyncio
    async def test_non_qualifying_narrative_hybrid_evaluation(
        self, sample_non_qualifying_narrative, monkeypatch
    ):
        """Test hybrid evaluation on non-qualifying narrative."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()
        llm_judge = LLMJudge(
            config=LLMJudgeConfig(alpha=0.7, beta=0.3),
            api_key="test-key",
        )

        # Mock LLM to agree with rule-based (non-qualifying)
        async def mock_evaluate(narrative):
            from bulletproof_green.models import LLMScoreResult
            return LLMScoreResult(
                score=0.2,
                reasoning="Routine work, business focus, vague claims",
                categories={},
            )

        monkeypatch.setattr(llm_judge, "evaluate", mock_evaluate)

        # Act
        eval_result = await evaluator.evaluate_async(
            sample_non_qualifying_narrative, llm_judge=llm_judge
        )
        score_result = scorer.score(eval_result)

        # Assert
        assert eval_result.classification == "NON_QUALIFYING"
        assert eval_result.risk_score >= 20
        assert eval_result.hybrid_used is True
        assert score_result.hybrid_score < 0.5  # Should be low

    @pytest.mark.asyncio
    async def test_llm_disagrees_with_rules_hybrid_balances(
        self, sample_narrative, monkeypatch
    ):
        """Test that hybrid score balances when LLM disagrees with rules."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()
        llm_judge = LLMJudge(
            config=LLMJudgeConfig(alpha=0.5, beta=0.5),  # Equal weight
            api_key="test-key",
        )

        # Mock LLM to give lower score than rules
        async def mock_evaluate(narrative):
            from bulletproof_green.models import LLMScoreResult
            return LLMScoreResult(
                score=0.5,  # LLM is more skeptical
                reasoning="Some uncertainty about qualification",
                categories={},
            )

        monkeypatch.setattr(llm_judge, "evaluate", mock_evaluate)

        # Act
        eval_result = await evaluator.evaluate_async(sample_narrative, llm_judge=llm_judge)
        score_result = scorer.score(eval_result)

        # Assert
        # Rules should give high score (qualifying narrative)
        assert score_result.overall_score > 0.7

        # Hybrid should be between rule score and LLM score (0.5)
        assert score_result.overall_score > score_result.hybrid_score > 0.5


class TestHybridFallbackBehavior:
    """Test fallback behavior when LLM fails."""

    @pytest.mark.asyncio
    async def test_fallback_when_llm_api_error(self, sample_narrative, monkeypatch):
        """Test fallback to rule-only when LLM API fails."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()
        llm_judge = LLMJudge(
            config=LLMJudgeConfig(),
            api_key="test-key",
        )

        # Mock LLM to raise exception
        async def mock_evaluate(narrative):
            raise RuntimeError("API error")

        monkeypatch.setattr(llm_judge, "evaluate", mock_evaluate)

        # Act
        eval_result = await evaluator.evaluate_async(sample_narrative, llm_judge=llm_judge)
        score_result = scorer.score(eval_result)

        # Assert
        assert eval_result.hybrid_used is False
        assert eval_result.llm_score is None
        assert score_result.hybrid_score == score_result.overall_score

    def test_fallback_when_no_llm_judge_provided(self, sample_narrative):
        """Test that evaluation works without LLM judge (backward compatibility)."""
        # Arrange
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()

        # Act
        eval_result = evaluator.evaluate(sample_narrative)  # No llm_judge parameter
        score_result = scorer.score(eval_result)

        # Assert
        assert not hasattr(eval_result, "hybrid_used") or eval_result.hybrid_used is False
        assert score_result.overall_score is not None
        assert score_result.hybrid_score == score_result.overall_score
