"""Tests for specificity detector (STORY-032: LLM reward hacking tests).

Tests that the specificity detector can:
1. Detect specific metrics (timestamps, error codes, measurements)
2. Resist gaming attempts (metric stuffing, superficial metrics)
3. Return proper (penalty, score) tuple following detector interface
"""

import pytest

from bulletproof_green.rules.specificity_detector import SpecificityDetector


class TestSpecificityDetector:
    """Test cases for SpecificityDetector."""

    @pytest.fixture
    def detector(self):
        """Create detector instance for tests."""
        return SpecificityDetector()

    # ============================================================================
    # POSITIVE CASES: Good narratives with specific metrics
    # ============================================================================

    def test_detect_timestamp_metrics(self, detector):
        """Should detect timestamp/date specificity (e.g., '2024-01-15')."""
        text = "On 2024-01-15, we observed 45ms latency reduction."
        penalty, score = detector.detect(text)
        assert penalty == 0
        assert score >= 0.5  # Good specificity

    def test_detect_error_code_specificity(self, detector):
        """Should detect error codes as specificity (e.g., 'ERROR-503')."""
        text = "Experiment failed with ERROR-503, retry logic implemented."
        penalty, score = detector.detect(text)
        assert penalty == 0
        assert score >= 0.3

    def test_detect_quantitative_metrics(self, detector):
        """Should detect quantitative metrics (latency, throughput, percentages)."""
        text = "Reduced latency from 120ms to 45ms, achieving 95% success rate."
        penalty, score = detector.detect(text)
        assert penalty == 0
        assert score >= 0.6  # Multiple metrics

    def test_detect_failure_citations(self, detector):
        """Should detect specific failure citations with dates/metrics."""
        text = "Initial hypothesis failed on 2024-02-01 with 78% error rate."
        penalty, score = detector.detect(text)
        assert penalty == 0
        assert score >= 0.5

    def test_multiple_specific_metrics(self, detector):
        """Should reward narratives with multiple specific metrics."""
        text = (
            "Iteration 1 (2024-01-10): 120ms latency, 65% accuracy. "
            "Iteration 2 (2024-01-17): 85ms latency, 82% accuracy. "
            "Final (2024-01-24): 45ms latency, 95% accuracy."
        )
        penalty, score = detector.detect(text)
        assert penalty == 0
        assert score >= 0.9  # Very high specificity

    # ============================================================================
    # NEGATIVE CASES: Vague narratives lacking specificity
    # ============================================================================

    def test_zero_metrics_high_penalty(self, detector):
        """Should penalize narratives with zero specific metrics."""
        text = "We improved performance significantly through better algorithms."
        penalty, score = detector.detect(text)
        assert penalty >= 10  # High penalty for zero specificity
        assert score < 0.3

    def test_single_metric_moderate_penalty(self, detector):
        """Should give moderate penalty for single metric."""
        text = "Performance improved to 95% success rate."
        penalty, score = detector.detect(text)
        assert 0 < penalty <= 5
        assert 0.3 <= score < 0.6

    def test_vague_improvement_claims(self, detector):
        """Should penalize vague improvement claims without metrics."""
        text = "The system runs much faster now with great success."
        penalty, score = detector.detect(text)
        assert penalty >= 8
        assert score < 0.2

    # ============================================================================
    # ADVERSARIAL CASES: LLM reward hacking / gaming detection (STORY-032)
    # ============================================================================

    def test_metric_stuffing_without_context(self, detector):
        """Should detect metric stuffing (ADV005, ADV006 from adversarial_narratives.json)."""
        # Superficial metric listing without technical narrative
        text = (
            "100% improvement, 99.9% reliability, 95% accuracy, "
            "87% efficiency, 73% performance, 50ms latency, "
            "2.3 microseconds, 1000 req/s throughput."
        )
        penalty, score = detector.detect(text)
        # Should be penalized despite having many metrics (lacks context)
        assert penalty >= 15  # Detect gaming attempt
        assert score < 0.7  # Lower score for superficial metrics

    def test_metric_list_without_experimentation(self, detector):
        """Should detect metric lists lacking experimentation narrative."""
        text = (
            "Performance improved 95%. Speed increased 87%. "
            "Efficiency gained 73%. Latency 50ms. Throughput 1000 req/s. "
            "Success rate 99.9%."
        )
        penalty, score = detector.detect(text)
        assert penalty >= 10  # Penalize list-style metrics
        assert score < 0.7

    def test_single_repeated_metric(self, detector):
        """Should detect single metric repeated multiple times (gaming)."""
        text = "95% 95% 95% improvement improvement improvement success success success."
        penalty, score = detector.detect(text)
        # Should detect keyword stuffing pattern (gaming)
        assert penalty >= 10
        assert score < 0.5

    def test_metrics_in_template_structure(self, detector):
        """Should handle metrics appearing in template gaming context."""
        text = (
            "HYPOTHESIS: 95% improvement. EXPERIMENT: Tested 95% hypothesis. "
            "FAILURE: 0% success. ITERATION: 87% accuracy. RESULT: 99.9% reliability."
        )
        penalty, score = detector.detect(text)
        # Metrics present but in formulaic structure
        # Detector should recognize metrics but not over-reward templated content
        assert penalty <= 5  # Some metrics are present
        assert score >= 0.4  # Acknowledge metrics despite template

    # ============================================================================
    # EDGE CASES: Boundary conditions
    # ============================================================================

    def test_empty_string(self, detector):
        """Should handle empty string gracefully."""
        penalty, score = detector.detect("")
        assert penalty >= 10
        assert score == 0.0

    def test_whitespace_only(self, detector):
        """Should handle whitespace-only input."""
        penalty, score = detector.detect("   \n\t  ")
        assert penalty >= 10
        assert score == 0.0

    def test_no_technical_content(self, detector):
        """Should penalize non-technical content lacking metrics."""
        text = "The team worked hard and achieved great results for the company."
        penalty, score = detector.detect(text)
        assert penalty >= 8
        assert score < 0.2

    def test_numbers_without_units(self, detector):
        """Should detect numbers even without explicit units."""
        text = "Improved algorithm performance from 120 to 45, success rate at 95."
        penalty, score = detector.detect(text)
        # Should recognize numbers as some level of specificity
        assert penalty <= 5
        assert score >= 0.4

    # ============================================================================
    # INTERFACE CONFORMANCE
    # ============================================================================

    def test_return_type(self, detector):
        """Should return (int, float) tuple."""
        penalty, score = detector.detect("Test narrative with 95% accuracy.")
        assert isinstance(penalty, int)
        assert isinstance(score, float)

    def test_penalty_range(self, detector):
        """Should return penalty in valid range (0-10 based on evaluator max)."""
        penalty, score = detector.detect("Vague narrative")
        assert 0 <= penalty <= 10

    def test_score_range(self, detector):
        """Should return score in 0.0-1.0 range."""
        penalty, score = detector.detect("Some text with 95% accuracy.")
        assert 0.0 <= score <= 1.0
