"""Tests for Green Agent scorer (STORY-004).

This test module validates the acceptance criteria for STORY-004:
- Computes overall_score = (100 - risk_score) / 100
- Computes component scores: correctness, safety, specificity, experimentation
- Returns scores in 0.0-1.0 scale
- Integrates with evaluator output
- Handles edge cases (division by zero, invalid inputs)
"""

import pytest

from bulletproof_green.evaluator import RuleBasedEvaluator
from bulletproof_green.models import EvaluationResult, ScoreResult
from bulletproof_green.scorer import AgentBeatsScorer


class TestOverallScoreCalculation:
    """Test overall_score = (100 - risk_score) / 100."""

    def test_overall_score_formula(self):
        """Test that overall_score follows the formula (100 - risk_score) / 100."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(risk_score=65)

        score_result = scorer.score(eval_result)

        # (100 - 65) / 100 = 0.35
        assert score_result.overall_score == 0.35

    def test_overall_score_zero_risk(self):
        """Test overall_score when risk_score is 0."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(risk_score=0)

        score_result = scorer.score(eval_result)

        # (100 - 0) / 100 = 1.0
        assert score_result.overall_score == 1.0

    def test_overall_score_max_risk(self):
        """Test overall_score when risk_score is 100."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(risk_score=100)

        score_result = scorer.score(eval_result)

        # (100 - 100) / 100 = 0.0
        assert score_result.overall_score == 0.0

    def test_overall_score_qualifying_threshold(self):
        """Test overall_score at qualifying threshold (risk_score = 20)."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(risk_score=20)

        score_result = scorer.score(eval_result)

        # (100 - 20) / 100 = 0.80
        assert score_result.overall_score == 0.80


class TestComponentScoreCorrectness:
    """Test correctness component score: (30 - routine_engineering_penalty) / 30."""

    def test_correctness_no_penalty(self):
        """Test correctness when routine_engineering_penalty is 0."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"routine_engineering_penalty": 0})

        score_result = scorer.score(eval_result)

        # (30 - 0) / 30 = 1.0
        assert score_result.correctness == 1.0

    def test_correctness_max_penalty(self):
        """Test correctness when routine_engineering_penalty is 30."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"routine_engineering_penalty": 30})

        score_result = scorer.score(eval_result)

        # (30 - 30) / 30 = 0.0
        assert score_result.correctness == 0.0

    def test_correctness_partial_penalty(self):
        """Test correctness with partial penalty."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"routine_engineering_penalty": 15})

        score_result = scorer.score(eval_result)

        # (30 - 15) / 30 = 0.5
        assert score_result.correctness == 0.5


class TestComponentScoreSafety:
    """Test safety component score: (20 - business_risk_penalty) / 20."""

    def test_safety_no_penalty(self):
        """Test safety when business_risk_penalty is 0."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"business_risk_penalty": 0})

        score_result = scorer.score(eval_result)

        # (20 - 0) / 20 = 1.0
        assert score_result.safety == 1.0

    def test_safety_max_penalty(self):
        """Test safety when business_risk_penalty is 20."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"business_risk_penalty": 20})

        score_result = scorer.score(eval_result)

        # (20 - 20) / 20 = 0.0
        assert score_result.safety == 0.0

    def test_safety_partial_penalty(self):
        """Test safety with partial penalty."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"business_risk_penalty": 10})

        score_result = scorer.score(eval_result)

        # (20 - 10) / 20 = 0.5
        assert score_result.safety == 0.5


class TestComponentScoreSpecificity:
    """Test specificity component score: (25 - vagueness_penalty) / 25."""

    def test_specificity_no_penalty(self):
        """Test specificity when vagueness_penalty is 0."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"vagueness_penalty": 0})

        score_result = scorer.score(eval_result)

        # (25 - 0) / 25 = 1.0
        assert score_result.specificity == 1.0

    def test_specificity_max_penalty(self):
        """Test specificity when vagueness_penalty is 25."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"vagueness_penalty": 25})

        score_result = scorer.score(eval_result)

        # (25 - 25) / 25 = 0.0
        assert score_result.specificity == 0.0

    def test_specificity_partial_penalty(self):
        """Test specificity with partial penalty."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"vagueness_penalty": 12})

        score_result = scorer.score(eval_result)

        # (25 - 12) / 25 = 0.52
        assert score_result.specificity == pytest.approx(0.52, rel=0.01)


class TestComponentScoreExperimentation:
    """Test experimentation component score: (15 - experimentation_penalty) / 15."""

    def test_experimentation_no_penalty(self):
        """Test experimentation when experimentation_penalty is 0."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"experimentation_penalty": 0})

        score_result = scorer.score(eval_result)

        # (15 - 0) / 15 = 1.0
        assert score_result.experimentation == 1.0

    def test_experimentation_max_penalty(self):
        """Test experimentation when experimentation_penalty is 15."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"experimentation_penalty": 15})

        score_result = scorer.score(eval_result)

        # (15 - 15) / 15 = 0.0
        assert score_result.experimentation == 0.0

    def test_experimentation_partial_penalty(self):
        """Test experimentation with partial penalty."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(component_scores={"experimentation_penalty": 5})

        score_result = scorer.score(eval_result)

        # (15 - 5) / 15 = 0.6667
        assert score_result.experimentation == pytest.approx(0.6667, rel=0.01)


class TestScoreRange:
    """Test that all scores are in 0.0-1.0 scale."""

    def test_all_scores_in_valid_range(self):
        """Test that all scores fall within 0.0-1.0."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(
            risk_score=50,
            component_scores={
                "routine_engineering_penalty": 10,
                "business_risk_penalty": 5,
                "vagueness_penalty": 12,
                "experimentation_penalty": 8,
                "specificity_penalty": 5,
            },
        )

        score_result = scorer.score(eval_result)

        assert 0.0 <= score_result.overall_score <= 1.0
        assert 0.0 <= score_result.correctness <= 1.0
        assert 0.0 <= score_result.safety <= 1.0
        assert 0.0 <= score_result.specificity <= 1.0
        assert 0.0 <= score_result.experimentation <= 1.0

    def test_scores_never_negative(self):
        """Test that scores cannot be negative even with extreme penalties."""
        scorer = AgentBeatsScorer()
        # Penalties exceeding maximums (should be clamped)
        eval_result = EvaluationResult(
            risk_score=100,
            component_scores={
                "routine_engineering_penalty": 50,  # Exceeds max 30
                "business_risk_penalty": 50,  # Exceeds max 20
                "vagueness_penalty": 50,  # Exceeds max 25
                "experimentation_penalty": 50,  # Exceeds max 15
            },
        )

        score_result = scorer.score(eval_result)

        assert score_result.overall_score >= 0.0
        assert score_result.correctness >= 0.0
        assert score_result.safety >= 0.0
        assert score_result.specificity >= 0.0
        assert score_result.experimentation >= 0.0

    def test_scores_never_exceed_one(self):
        """Test that scores cannot exceed 1.0 even with negative penalties."""
        scorer = AgentBeatsScorer()
        # Negative penalties (invalid but should be handled)
        eval_result = EvaluationResult(
            risk_score=-10,  # Invalid but should be handled
            component_scores={
                "routine_engineering_penalty": -10,
                "business_risk_penalty": -10,
                "vagueness_penalty": -10,
                "experimentation_penalty": -10,
            },
        )

        score_result = scorer.score(eval_result)

        assert score_result.overall_score <= 1.0
        assert score_result.correctness <= 1.0
        assert score_result.safety <= 1.0
        assert score_result.specificity <= 1.0
        assert score_result.experimentation <= 1.0


class TestEvaluatorIntegration:
    """Test integration with evaluator output."""

    def test_score_from_evaluator_result(self):
        """Test scoring a real evaluator result."""
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()

        narrative = """
        The team performed routine maintenance on the database.
        We improved market share through better performance.
        The results were significantly improved.
        """

        eval_result = evaluator.evaluate(narrative)
        score_result = scorer.score(eval_result)

        # Should have valid scores
        assert 0.0 <= score_result.overall_score <= 1.0
        assert score_result.overall_score == (100 - eval_result.risk_score) / 100

    def test_score_from_qualifying_narrative(self):
        """Test scoring a qualifying narrative produces high overall_score."""
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()

        narrative = """
        The project faced significant technical uncertainty regarding distributed
        system performance at scale. Our hypothesis was that a novel caching
        architecture could resolve the latency issues. Initial experiments with
        the LRU cache failed with 500ms response times under 10,000 concurrent
        requests. After multiple iterations testing different eviction strategies,
        the probabilistic cache achieved 45ms latency. The systematic experimentation
        process documented alternative approaches and measured specific performance
        metrics including throughput (50,000 req/s), memory usage (1.2GB), and
        error rates (0.01%).
        """

        eval_result = evaluator.evaluate(narrative)
        score_result = scorer.score(eval_result)

        # Qualifying (risk < 20) means overall_score > 0.80
        assert score_result.overall_score > 0.80

    def test_score_from_non_qualifying_narrative(self):
        """Test scoring a non-qualifying narrative produces low overall_score."""
        evaluator = RuleBasedEvaluator()
        scorer = AgentBeatsScorer()

        narrative = """
        The team performed routine maintenance to improve market share.
        We enhanced the product with standard features for better sales.
        The initiative was very successful with great improvements.
        """

        eval_result = evaluator.evaluate(narrative)
        score_result = scorer.score(eval_result)

        # Non-qualifying (risk > 40) means overall_score < 0.60
        assert score_result.overall_score < 0.60


class TestEdgeCases:
    """Test edge cases including invalid inputs."""

    def test_missing_component_scores(self):
        """Test handling of missing component scores."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(
            risk_score=50,
            component_scores={},  # Empty component scores
        )

        score_result = scorer.score(eval_result)

        # Should handle gracefully (default to max penalty or 0 score)
        assert 0.0 <= score_result.overall_score <= 1.0
        assert 0.0 <= score_result.correctness <= 1.0
        assert 0.0 <= score_result.safety <= 1.0
        assert 0.0 <= score_result.specificity <= 1.0
        assert 0.0 <= score_result.experimentation <= 1.0

    def test_partial_component_scores(self):
        """Test handling of partial component scores."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(
            risk_score=30,
            component_scores={
                "routine_engineering_penalty": 10,
                # Missing other penalties
            },
        )

        score_result = scorer.score(eval_result)

        # Should handle gracefully
        assert score_result.correctness == pytest.approx((30 - 10) / 30, rel=0.01)
        assert 0.0 <= score_result.safety <= 1.0

    def test_none_risk_score(self):
        """Test handling of None risk_score."""
        scorer = AgentBeatsScorer()

        # Create result with default values (risk_score defaults to 100)
        eval_result = EvaluationResult()

        score_result = scorer.score(eval_result)

        # Should use default risk_score of 100
        assert score_result.overall_score == 0.0

    def test_boundary_risk_score_values(self):
        """Test boundary values for risk_score."""
        scorer = AgentBeatsScorer()

        # Test at exact boundaries
        for risk_score in [0, 1, 19, 20, 21, 99, 100]:
            eval_result = EvaluationResult(risk_score=risk_score)
            score_result = scorer.score(eval_result)
            expected = (100 - risk_score) / 100
            assert score_result.overall_score == pytest.approx(expected, rel=0.01)


class TestScoreResultStructure:
    """Test ScoreResult dataclass structure."""

    def test_score_result_has_required_fields(self):
        """Test that ScoreResult has all required fields."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(
            risk_score=50,
            component_scores={
                "routine_engineering_penalty": 10,
                "business_risk_penalty": 5,
                "vagueness_penalty": 12,
                "experimentation_penalty": 8,
            },
        )

        score_result = scorer.score(eval_result)

        assert hasattr(score_result, "overall_score")
        assert hasattr(score_result, "correctness")
        assert hasattr(score_result, "safety")
        assert hasattr(score_result, "specificity")
        assert hasattr(score_result, "experimentation")

    def test_score_result_is_dataclass(self):
        """Test that ScoreResult is a proper Pydantic model."""
        from pydantic import BaseModel

        assert issubclass(ScoreResult, BaseModel)

    def test_score_result_repr(self):
        """Test that ScoreResult has a meaningful repr."""
        scorer = AgentBeatsScorer()
        eval_result = EvaluationResult(risk_score=50)

        score_result = scorer.score(eval_result)

        # Should have a string representation
        assert "ScoreResult" in repr(score_result) or "overall_score" in repr(score_result)
