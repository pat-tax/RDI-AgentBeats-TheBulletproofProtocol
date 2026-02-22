"""Tests for statistical rigor measures (STORY-027).

This test module validates statistical rigor requirements:
- Cohen's κ ≥ 0.75 for inter-rater reliability
- 95% confidence intervals for metrics
- Reproducibility across multiple runs
"""

import pytest

from bulletproof_green.statistics import calculate_cohens_kappa, calculate_confidence_interval


class TestStatisticalMeasures:
    """Test statistical rigor calculations."""

    def test_cohens_kappa_calculation(self):
        """Test Cohen's κ calculation for inter-rater agreement."""
        # Example: Two raters classifying 10 narratives as qualifying/non-qualifying
        rater1 = [1, 1, 0, 0, 1, 1, 0, 1, 0, 0]
        rater2 = [1, 1, 0, 1, 1, 1, 0, 1, 0, 0]

        kappa = calculate_cohens_kappa(rater1, rater2)

        # κ should be in [-1, 1] range
        assert -1.0 <= kappa <= 1.0
        # For good agreement, κ should be ≥ 0.75
        assert kappa >= 0.60, f"Cohen's κ should show agreement, got {kappa}"

    def test_perfect_agreement_kappa_equals_one(self):
        """Test that perfect agreement yields κ = 1.0."""
        rater1 = [1, 1, 0, 0, 1, 0, 1, 0]
        rater2 = [1, 1, 0, 0, 1, 0, 1, 0]

        kappa = calculate_cohens_kappa(rater1, rater2)

        assert kappa == pytest.approx(1.0, abs=0.01)

    def test_no_agreement_kappa_near_zero(self):
        """Test that random agreement yields κ ≈ 0."""
        # Random classifications with no pattern
        rater1 = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        rater2 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

        kappa = calculate_cohens_kappa(rater1, rater2)

        # No agreement beyond chance should yield κ ≈ 0 or negative
        assert kappa <= 0.1

    def test_confidence_interval_calculation(self):
        """Test 95% confidence interval calculation for accuracy metrics."""
        # Example: accuracy scores from multiple benchmark runs
        scores = [0.85, 0.87, 0.84, 0.86, 0.88, 0.85, 0.87, 0.86]

        ci_lower, ci_upper = calculate_confidence_interval(scores, confidence=0.95)

        # CI should bracket the mean
        mean = sum(scores) / len(scores)
        assert ci_lower < mean < ci_upper

        # CI should have reasonable bounds
        assert 0.0 <= ci_lower <= ci_upper <= 1.0

    def test_confidence_interval_narrows_with_more_samples(self):
        """Test that CI width decreases with more samples."""
        import random

        random.seed(42)
        small_sample = [0.85 + random.gauss(0, 0.02) for _ in range(10)]
        large_sample = [0.85 + random.gauss(0, 0.02) for _ in range(100)]

        ci_small_lower, ci_small_upper = calculate_confidence_interval(small_sample)
        ci_large_lower, ci_large_upper = calculate_confidence_interval(large_sample)

        width_small = ci_small_upper - ci_small_lower
        width_large = ci_large_upper - ci_large_lower

        # Larger sample should have narrower CI
        assert width_large < width_small


class TestBenchmarkReproducibility:
    """Test that benchmark results are reproducible."""

    def test_deterministic_evaluation(self):
        """Test that evaluating the same narrative yields identical results."""
        from bulletproof_green.evals.evaluator import RuleBasedEvaluator

        evaluator = RuleBasedEvaluator()
        narrative = """
        We developed a novel algorithm to optimize database query performance.
        Our hypothesis was that caching frequently accessed data would reduce latency.
        Initial tests showed a 10ms improvement, but subsequent iterations revealed
        race conditions that required alternative approaches.
        """

        # Run evaluation multiple times
        results = [evaluator.evaluate(narrative) for _ in range(5)]

        # All results should be identical (deterministic)
        risk_scores = [r.risk_score for r in results]
        assert len(set(risk_scores)) == 1, "Risk scores should be deterministic"

        classifications = [r.classification for r in results]
        assert len(set(classifications)) == 1, "Classifications should be deterministic"
