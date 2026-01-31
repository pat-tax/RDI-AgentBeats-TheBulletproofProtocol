"""Integration tests for evaluator with modular detectors (STORY-033).

This test module validates the acceptance criteria for STORY-033:
- Evaluator imports and uses business_risk_detector
- Evaluator imports and uses specificity_detector
- Both detectors integrated into evaluation flow
- Integration tests verify detectors are called
"""

from bulletproof_green.evals.evaluator import RuleBasedEvaluator


class TestBusinessRiskDetectorIntegration:
    """Test that business_risk_detector is integrated into evaluator."""

    def test_evaluator_uses_business_risk_detector(self):
        """Test that evaluator uses business_risk_detector module."""
        evaluator = RuleBasedEvaluator()

        # Narrative with business risk language
        narrative = """
        The project aimed to increase market share and revenue growth.
        Our objective was improving customer satisfaction and competitive positioning.
        We sought to capture new market segments and stay competitive.
        """

        result = evaluator.evaluate(narrative)

        # Should detect business risk patterns via the detector
        assert result.component_scores["business_risk_penalty"] > 0
        assert result.business_keywords_detected > 0
        assert any(issue.category == "business_risk" for issue in result.redline.issues)

    def test_business_risk_detector_returns_correct_interface(self):
        """Test that business_risk_detector returns (penalty, count) tuple."""
        evaluator = RuleBasedEvaluator()

        # Business-heavy narrative
        narrative = "We focused on revenue and profit with sales growth targets."

        result = evaluator.evaluate(narrative)

        # Penalty should be int > 0
        assert isinstance(result.component_scores["business_risk_penalty"], (int, float))
        assert result.component_scores["business_risk_penalty"] > 0

        # Count should be int > 0
        assert isinstance(result.business_keywords_detected, int)
        assert result.business_keywords_detected > 0


class TestSpecificityDetectorIntegration:
    """Test that specificity_detector is integrated into evaluator."""

    def test_evaluator_uses_specificity_detector(self):
        """Test that evaluator uses specificity_detector module."""
        evaluator = RuleBasedEvaluator()

        # Narrative with specific metrics
        narrative = """
        We reduced latency from 120ms to 45ms through algorithm optimization.
        Error rate decreased from 5% to 1% after implementing retry logic.
        System throughput improved to 1000 req/s under load.
        """

        result = evaluator.evaluate(narrative)

        # Should detect specificity via the detector
        assert result.component_scores["specificity_penalty"] == 0  # High specificity
        assert result.specificity_score > 0.8  # Good score

    def test_evaluator_detects_lack_of_specificity(self):
        """Test that evaluator detects narratives lacking specificity."""
        evaluator = RuleBasedEvaluator()

        # Vague narrative without metrics
        narrative = """
        We improved the system significantly.
        Performance was greatly enhanced.
        Results were much better than before.
        """

        result = evaluator.evaluate(narrative)

        # Should apply specificity penalty
        assert result.component_scores["specificity_penalty"] > 0
        assert result.specificity_score < 0.5

    def test_specificity_detector_returns_correct_interface(self):
        """Test that specificity_detector returns (penalty, score) tuple."""
        evaluator = RuleBasedEvaluator()

        # Narrative with some metrics
        narrative = "Response time reduced to 50ms."

        result = evaluator.evaluate(narrative)

        # Penalty should be int >= 0
        assert isinstance(result.component_scores["specificity_penalty"], (int, float))
        assert result.component_scores["specificity_penalty"] >= 0

        # Score should be float 0.0-1.0
        assert isinstance(result.specificity_score, float)
        assert 0.0 <= result.specificity_score <= 1.0


class TestBothDetectorsIntegrated:
    """Test that both detectors work together in evaluation flow."""

    def test_evaluator_uses_both_detectors(self):
        """Test that evaluator calls both business_risk and specificity detectors."""
        evaluator = RuleBasedEvaluator()

        # Narrative with both business risk AND lack of specificity
        narrative = """
        Our goal was to increase revenue and profit margins.
        We achieved great success with much better performance.
        The system was significantly improved overall.
        """

        result = evaluator.evaluate(narrative)

        # Should detect both issues
        assert result.component_scores["business_risk_penalty"] > 0
        assert result.component_scores["specificity_penalty"] > 0
        assert result.business_keywords_detected > 0
        assert result.specificity_score < 0.5

    def test_evaluator_with_good_narrative(self):
        """Test evaluator with technical narrative that has specificity."""
        evaluator = RuleBasedEvaluator()

        # Good narrative: technical uncertainty + specific metrics
        narrative = """
        We hypothesized that caching could reduce latency from 120ms to under 50ms.
        The first experiment failed with only 10% improvement (108ms).
        After iterating on cache invalidation logic, we achieved 45ms response time.
        Error rate remained under 1% throughout testing.
        """

        result = evaluator.evaluate(narrative)

        # Should have low business risk
        assert result.component_scores["business_risk_penalty"] == 0

        # Should have low specificity penalty (high specificity)
        assert result.component_scores["specificity_penalty"] <= 3
        assert result.specificity_score >= 0.66

        # Should detect experimentation evidence
        assert result.experimentation_evidence_score >= 0.5
