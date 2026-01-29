"""Integration tests for arena mode end-to-end flow (STORY-024).

This module validates the acceptance criteria for STORY-024:
- Business risk detector: market, revenue, customers, sales, ROI, profit keywords
- Specificity detector: failure citations (dates, error codes, metrics), hypothesis-test-failure-iteration patterns
- Integrated into evaluator scoring pipeline
- Returns detection counts for diagnostics
- Modular detector architecture
- Pattern weight configuration

Tests verify that:
1. Business risk patterns are detected and penalized in evaluation
2. Specificity patterns (metrics, dates, error codes) are detected and rewarded
3. Detectors are properly integrated into the evaluation pipeline
4. Arena mode uses these detectors for iterative refinement
5. Detection counts are included in evaluation diagnostics
"""

from __future__ import annotations

from bulletproof_green.evals.evaluator import RuleBasedEvaluator


class TestBusinessRiskDetector:
    """Test business risk detector integration into evaluator."""

    def test_detects_market_keywords(self):
        """Test detector identifies market-related business risk keywords."""
        evaluator = RuleBasedEvaluator()
        narrative = "Our project aimed to increase market share and competitive positioning."

        result = evaluator.evaluate(narrative)

        # Should detect business risk patterns
        assert result.business_keywords_detected > 0
        assert result.component_scores["business_risk_penalty"] > 0

        # Should have business risk issues in redline
        business_issues = [
            issue for issue in result.redline.issues
            if issue.category == "business_risk"
        ]
        assert len(business_issues) > 0

    def test_detects_revenue_keywords(self):
        """Test detector identifies revenue-related business risk keywords."""
        evaluator = RuleBasedEvaluator()
        narrative = "This development was critical for revenue growth and profit maximization."

        result = evaluator.evaluate(narrative)

        # Should detect business keywords (revenue, profit)
        assert result.business_keywords_detected >= 2
        assert result.component_scores["business_risk_penalty"] > 0

    def test_detects_customer_keywords(self):
        """Test detector identifies customer satisfaction business risk."""
        evaluator = RuleBasedEvaluator()
        narrative = "We focused on improving customer satisfaction and sales targets."

        result = evaluator.evaluate(narrative)

        # Should detect business keywords
        assert result.business_keywords_detected > 0
        assert result.component_scores["business_risk_penalty"] > 0

    def test_detects_sales_keywords(self):
        """Test detector identifies sales-related business risk keywords."""
        evaluator = RuleBasedEvaluator()
        narrative = "The project targeted sales growth and market segments expansion."

        result = evaluator.evaluate(narrative)

        # Should detect business keywords
        assert result.business_keywords_detected > 0

    def test_detects_roi_and_profit_keywords(self):
        """Test detector identifies ROI and profit business risk keywords."""
        evaluator = RuleBasedEvaluator()
        narrative = "We aimed to maximize profitability and ensure strong ROI."

        result = evaluator.evaluate(narrative)

        # Should detect business keywords
        assert result.business_keywords_detected > 0


class TestSpecificityDetector:
    """Test specificity detector integration into evaluator."""

    def test_detects_failure_citations_with_dates(self):
        """Test detector identifies specific failure citations with dates."""
        evaluator = RuleBasedEvaluator()
        narrative = """Our hypothesis was that caching would reduce latency below 50ms.
        We tested this on 2024-01-15 but the experiment failed with 120ms latency.
        After 3 iterations, we discovered the issue was network overhead."""

        result = evaluator.evaluate(narrative)

        # Should detect specificity (dates, metrics)
        assert result.specificity_score > 0
        # Should have low specificity penalty due to metrics
        assert result.component_scores["specificity_penalty"] < 10

    def test_detects_error_codes_and_metrics(self):
        """Test detector identifies error codes and specific metrics."""
        evaluator = RuleBasedEvaluator()
        narrative = """We encountered ERROR-401 during authentication testing.
        Memory usage was 2.5GB, exceeding our 1GB target by 150%.
        Response time was 450ms instead of the required 100ms."""

        result = evaluator.evaluate(narrative)

        # Should detect multiple metrics (GB, %, ms)
        assert result.specificity_score > 0.5
        # Should have minimal or no specificity penalty
        assert result.component_scores["specificity_penalty"] <= 3

    def test_detects_hypothesis_test_failure_iteration_pattern(self):
        """Test detector rewards hypothesis-test-failure-iteration scientific method."""
        evaluator = RuleBasedEvaluator()
        narrative = """We hypothesized that algorithm X would improve throughput by 40%.
        Our experiments showed only 10% improvement. This failure led us to test
        alternative approaches. After 5 iterations, we discovered uncertain behavior
        in edge cases that required novel solutions."""

        result = evaluator.evaluate(narrative)

        # Should detect experimentation evidence
        assert result.experimentation_evidence_score > 0.5
        # Should have low experimentation penalty
        assert result.component_scores["experimentation_penalty"] <= 5

    def test_rewards_specific_metrics_over_vague_language(self):
        """Test detector rewards specific metrics and penalizes vague language."""
        evaluator = RuleBasedEvaluator()

        # Vague narrative
        vague_narrative = "We made significant improvements and achieved better performance."
        vague_result = evaluator.evaluate(vague_narrative)

        # Specific narrative
        specific_narrative = """We reduced latency from 200ms to 45ms (77.5% improvement).
        Memory usage decreased from 1.2GB to 800MB. Error rate dropped from 5% to 0.2%."""
        specific_result = evaluator.evaluate(specific_narrative)

        # Specific narrative should have better specificity score
        assert specific_result.specificity_score > vague_result.specificity_score
        # Specific narrative should have lower specificity penalty
        assert specific_result.component_scores["specificity_penalty"] < vague_result.component_scores["specificity_penalty"]


class TestDetectorIntegration:
    """Test detectors are properly integrated into evaluation pipeline."""

    def test_evaluation_includes_detection_counts(self):
        """Test evaluation result includes diagnostic detection counts."""
        evaluator = RuleBasedEvaluator()
        narrative = """Our project targeted market share while reducing revenue risk.
        We hypothesized latency under 50ms was achievable. Testing on 2024-01-15
        showed 120ms latency. After 3 iterations and multiple failures, we
        discovered uncertain network behavior requiring novel solutions."""

        result = evaluator.evaluate(narrative)

        # Should include all diagnostic counts
        assert hasattr(result, "routine_patterns_detected")
        assert hasattr(result, "vague_phrases_detected")
        assert hasattr(result, "business_keywords_detected")
        assert hasattr(result, "experimentation_evidence_score")
        assert hasattr(result, "specificity_score")

        # Should detect business keywords
        assert result.business_keywords_detected > 0
        # Should detect experimentation patterns
        assert result.experimentation_evidence_score > 0
        # Should detect specificity
        assert result.specificity_score > 0

    def test_component_scores_include_all_detectors(self):
        """Test component scores include penalties from all detectors."""
        evaluator = RuleBasedEvaluator()
        narrative = "Test narrative with routine maintenance and market focus."

        result = evaluator.evaluate(narrative)

        # Should include all component scores
        assert "routine_engineering_penalty" in result.component_scores
        assert "business_risk_penalty" in result.component_scores
        assert "vagueness_penalty" in result.component_scores
        assert "experimentation_penalty" in result.component_scores
        assert "specificity_penalty" in result.component_scores

    def test_redline_issues_categorized_by_detector(self):
        """Test redline issues are properly categorized by detector type."""
        evaluator = RuleBasedEvaluator()
        narrative = """We did routine maintenance to improve market share.
        The work was greatly enhanced with significant improvements to revenue."""

        result = evaluator.evaluate(narrative)

        # Should have issues from multiple detectors
        categories = {issue.category for issue in result.redline.issues}
        assert "routine_engineering" in categories
        assert "business_risk" in categories
        assert "vagueness" in categories

    def test_risk_score_aggregates_all_detector_penalties(self):
        """Test risk score properly aggregates penalties from all detectors."""
        evaluator = RuleBasedEvaluator()

        # Narrative that triggers multiple detectors
        bad_narrative = """We did routine debugging to boost market share and revenue.
        Things worked much better with great success and significant improvements."""

        # Narrative with few issues
        good_narrative = """We hypothesized that algorithm optimization would reduce
        latency below 50ms. Testing on 2024-01-15 showed failure at 120ms latency.
        After 5 iterations of experimentation, we discovered uncertain behavior
        requiring a novel caching approach. Final result: 42ms latency (16% improvement)."""

        bad_result = evaluator.evaluate(bad_narrative)
        good_result = evaluator.evaluate(good_narrative)

        # Bad narrative should have higher risk score
        assert bad_result.risk_score > good_result.risk_score
        # Good narrative should be qualifying
        assert good_result.classification == "QUALIFYING"
        assert good_result.risk_score < 20


class TestModularDetectorArchitecture:
    """Test detector architecture is modular and maintainable."""

    def test_detector_patterns_are_configurable(self):
        """Test detector patterns can be accessed and potentially configured."""
        evaluator = RuleBasedEvaluator()

        # Verify pattern attributes exist and are accessible
        assert hasattr(evaluator, "ROUTINE_PATTERNS")
        assert hasattr(evaluator, "BUSINESS_PATTERNS")
        assert hasattr(evaluator, "VAGUE_PATTERNS")
        assert hasattr(evaluator, "EXPERIMENTATION_PATTERNS")
        assert hasattr(evaluator, "SPECIFICITY_PATTERN")

        # Verify patterns are lists/compiled patterns
        assert isinstance(evaluator.ROUTINE_PATTERNS, list)
        assert isinstance(evaluator.BUSINESS_PATTERNS, list)
        assert isinstance(evaluator.VAGUE_PATTERNS, list)
        assert isinstance(evaluator.EXPERIMENTATION_PATTERNS, list)

        # Verify patterns have expected structure (pattern, description)
        if len(evaluator.BUSINESS_PATTERNS) > 0:
            pattern, description = evaluator.BUSINESS_PATTERNS[0]
            assert isinstance(pattern, str)
            assert isinstance(description, str)

    def test_detector_methods_are_isolated(self):
        """Test detector methods are isolated and can be called independently."""
        evaluator = RuleBasedEvaluator()
        text = "market revenue customers sales profit"
        issues: list = []

        # Each detector method should be callable independently
        routine_penalty, routine_count = evaluator._detect_routine_engineering(text, issues)
        assert isinstance(routine_penalty, int)
        assert isinstance(routine_count, int)

        business_penalty, business_count = evaluator._detect_business_risk(text, issues)
        assert isinstance(business_penalty, int)
        assert isinstance(business_count, int)
        assert business_count > 0  # Should detect keywords in test text

        vague_penalty, vague_count = evaluator._detect_vagueness(text, issues)
        assert isinstance(vague_penalty, int)
        assert isinstance(vague_count, int)

    def test_pattern_weights_are_configurable_via_penalties(self):
        """Test pattern weights are implemented via configurable penalties."""
        evaluator = RuleBasedEvaluator()

        # Test that different patterns have different penalty weights
        routine_text = "routine maintenance and debugging"
        business_text = "market share and revenue growth"

        routine_issues: list = []
        business_issues: list = []

        routine_penalty, _ = evaluator._detect_routine_engineering(routine_text, routine_issues)
        business_penalty, _ = evaluator._detect_business_risk(business_text, business_issues)

        # Both should apply penalties
        assert routine_penalty > 0
        assert business_penalty > 0

        # Penalties should be capped at documented maximums
        max_routine = 30  # Per evaluator.py documentation
        max_business = 20  # Per evaluator.py documentation

        # Test with text that triggers many patterns
        many_routine = " ".join(["routine maintenance debugging patches migration"] * 10)
        many_business = " ".join(["market revenue profit customers sales"] * 10)

        routine_issues_many: list = []
        business_issues_many: list = []

        routine_penalty_many, _ = evaluator._detect_routine_engineering(many_routine, routine_issues_many)
        business_penalty_many, _ = evaluator._detect_business_risk(many_business, business_issues_many)

        # Penalties should be capped
        assert routine_penalty_many <= max_routine
        assert business_penalty_many <= max_business


class TestArenaModeIntegration:
    """Test arena mode uses detectors for iterative refinement (integration with server)."""

    def test_arena_mode_evaluation_includes_detector_diagnostics(self):
        """Test arena mode evaluation includes all detector diagnostic information."""
        # This is a basic test that verifies the evaluation used by arena mode
        # includes all detector outputs. Full arena mode integration is tested
        # in test_arena_mode_server.py and test_arena_executor.py
        evaluator = RuleBasedEvaluator()

        narrative = """Market-focused project with revenue targets.
        We did routine debugging with significant improvements."""

        result = evaluator.evaluate(narrative)

        # Arena mode relies on these diagnostics for critique generation
        assert result.business_keywords_detected > 0
        assert result.routine_patterns_detected > 0
        assert result.vague_phrases_detected > 0

        # Redline issues are used for critique feedback
        assert len(result.redline.issues) > 0

        # Risk score is used for termination criteria
        assert result.risk_score > 0

    def test_evaluation_output_suitable_for_arena_critique(self):
        """Test evaluation output provides sufficient detail for arena critique."""
        evaluator = RuleBasedEvaluator()
        narrative = "We improved market share with routine maintenance."

        result = evaluator.evaluate(narrative)

        # Should provide detailed issues for critique generation
        assert len(result.redline.issues) > 0

        # Each issue should have suggestion for improvement
        for issue in result.redline.issues:
            assert hasattr(issue, "suggestion")
            assert len(issue.suggestion) > 0
            assert hasattr(issue, "category")
            assert hasattr(issue, "severity")

        # Should provide component breakdown for targeted feedback
        assert len(result.component_scores) == 5
