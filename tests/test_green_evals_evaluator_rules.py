"""Tests for Green Agent rule-based evaluator (STORY-003).

This test module validates the acceptance criteria for STORY-003:
- Detects "Routine Engineering" patterns
- Applies "Business Component" test
- Flags vague language without specific metrics
- Requires citation of specific failure events
- Outputs Risk Score (0-100) and Redline Markup
- Rejects claims until Risk Score < 20
- Deterministic rule-based scoring
- Returns structured evaluation per Green-Agent-Metrics-Specification.md
"""

from bulletproof_green.evals.evaluator import RuleBasedEvaluator
from bulletproof_green.evals.models import EvaluationResult, Issue


class TestRoutineEngineeringDetection:
    """Test detection of Routine Engineering patterns."""

    def test_detects_maintenance_activities(self):
        """Test that evaluator flags routine maintenance work."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The team performed routine maintenance on the database system.
        We fixed bugs and updated configurations following standard procedures.
        The work involved debugging existing code and applying patches.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["routine_engineering_penalty"] > 0
        assert any(issue.category == "routine_engineering" for issue in result.redline.issues)

    def test_detects_adaptation_of_existing_solutions(self):
        """Test that evaluator flags adaptation of existing commercial solutions."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        We implemented the solution using off-the-shelf components.
        The project involved adapting vendor software to our environment.
        Standard integration patterns were applied with minor customization.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["routine_engineering_penalty"] > 0

    def test_detects_porting_activities(self):
        """Test that evaluator flags porting/migration work."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The project migrated the application from one platform to another.
        We ported the existing codebase to a new framework.
        The migration followed documented procedures with predictable outcomes.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["routine_engineering_penalty"] > 0


class TestBusinessComponentTest:
    """Test Business Component / Business Risk detection."""

    def test_detects_business_risk_language(self):
        """Test that evaluator flags business risk vs technical risk."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The project was designed to increase market share and revenue.
        Our goal was improving customer satisfaction and competitive positioning.
        The initiative aimed to capture new market segments and drive sales growth.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["business_risk_penalty"] > 0
        assert any(issue.category == "business_risk" for issue in result.redline.issues)

    def test_allows_technical_uncertainty(self):
        """Test that evaluator accepts technical uncertainty language."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The team faced significant technical uncertainty regarding algorithm performance.
        Multiple hypotheses were tested to resolve the unknown behavior of the system.
        Experimentation revealed unexpected performance characteristics requiring investigation.
        """
        result = evaluator.evaluate(narrative)

        # Technical language should not trigger business risk penalty
        assert result.component_scores["business_risk_penalty"] < 10


class TestVagueLanguageDetection:
    """Test detection of vague language without specific metrics."""

    def test_detects_vague_claims(self):
        """Test that evaluator flags vague unsubstantiated claims."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        We made significant improvements to the system.
        The solution was greatly enhanced with better performance.
        Our approach achieved substantial gains in efficiency.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["vagueness_penalty"] > 0
        assert any(issue.category == "vagueness" for issue in result.redline.issues)

    def test_accepts_specific_metrics(self):
        """Test that evaluator accepts narratives with specific metrics."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        Latency improved from 250ms to 45ms after implementing the new algorithm.
        Memory consumption decreased by 35% from 2.4GB to 1.56GB.
        The system handled 10,000 concurrent connections versus the previous 2,500.
        """
        result = evaluator.evaluate(narrative)

        # Specific metrics should result in lower vagueness penalty
        assert result.component_scores["vagueness_penalty"] < 10


class TestExperimentationEvidence:
    """Test requirement for specific failure event citations."""

    def test_requires_failure_documentation(self):
        """Test that evaluator flags missing failure documentation."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The project was successful from the start.
        Our initial approach worked as expected without issues.
        Development proceeded smoothly with no setbacks.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["experimentation_penalty"] > 0

    def test_accepts_documented_failures(self):
        """Test that evaluator accepts narratives with documented failures."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        Initial implementation failed to meet performance requirements.
        The first approach resulted in memory leaks under load conditions.
        After three iterations, we identified the root cause of the bottleneck.
        Alternative algorithms were tested and compared against benchmarks.
        """
        result = evaluator.evaluate(narrative)

        # Documented failures should result in lower experimentation penalty
        assert result.component_scores["experimentation_penalty"] < 10


class TestRiskScoreOutput:
    """Test Risk Score calculation (0-100 scale)."""

    def test_risk_score_in_valid_range(self):
        """Test that risk score is between 0 and 100."""
        evaluator = RuleBasedEvaluator()
        narrative = "Sample narrative for testing risk score range."
        result = evaluator.evaluate(narrative)

        assert 0 <= result.risk_score <= 100

    def test_high_risk_for_non_qualifying_narrative(self):
        """Test that non-qualifying narrative gets high risk score."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The team performed routine maintenance to improve market share.
        We enhanced the product with standard features for better sales.
        The initiative was very successful with great improvements.
        """
        result = evaluator.evaluate(narrative)

        # Should be HIGH or higher risk (>40)
        assert result.risk_score > 40

    def test_low_risk_for_qualifying_narrative(self):
        """Test that qualifying narrative gets low risk score."""
        evaluator = RuleBasedEvaluator()
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
        result = evaluator.evaluate(narrative)

        # Should be LOW risk (<20)
        assert result.risk_score < 20


class TestRedlineMarkup:
    """Test Redline Markup output."""

    def test_redline_contains_issues(self):
        """Test that redline markup contains detected issues."""
        evaluator = RuleBasedEvaluator()
        narrative = "The team made great improvements to increase revenue."
        result = evaluator.evaluate(narrative)

        assert result.redline is not None
        assert result.redline.total_issues >= 0
        assert isinstance(result.redline.issues, list)

    def test_issues_have_required_fields(self):
        """Test that each issue has required fields."""
        evaluator = RuleBasedEvaluator()
        narrative = "We improved market share through routine maintenance."
        result = evaluator.evaluate(narrative)

        for issue in result.redline.issues:
            assert hasattr(issue, "category")
            assert hasattr(issue, "severity")
            assert hasattr(issue, "text")
            assert hasattr(issue, "suggestion")

    def test_issue_severity_levels(self):
        """Test that issues have valid severity levels."""
        evaluator = RuleBasedEvaluator()
        narrative = "Standard maintenance was performed successfully."
        result = evaluator.evaluate(narrative)

        valid_severities = {"critical", "high", "medium", "low"}
        for issue in result.redline.issues:
            assert issue.severity in valid_severities


class TestComplianceClassification:
    """Test binary compliance classification."""

    def test_qualifying_classification(self):
        """Test that low-risk narrative is classified as QUALIFYING."""
        evaluator = RuleBasedEvaluator()
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
        result = evaluator.evaluate(narrative)

        assert result.classification == "QUALIFYING"

    def test_non_qualifying_classification(self):
        """Test that high-risk narrative is classified as NON_QUALIFYING."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The team performed routine maintenance to improve market share.
        We enhanced the product with standard features for better sales.
        The initiative was very successful with great improvements.
        """
        result = evaluator.evaluate(narrative)

        assert result.classification == "NON_QUALIFYING"

    def test_classification_threshold(self):
        """Test that risk score < 20 results in QUALIFYING."""
        evaluator = RuleBasedEvaluator()

        # A narrative designed to get exactly borderline score
        # Test that the evaluator uses 20 as the threshold
        low_risk_narrative = """
        The project faced significant technical uncertainty. Experiments failed
        initially with 500ms latency. After iterations, achieved 45ms. Metrics:
        throughput 50,000 req/s, memory 1.2GB.
        """
        result = evaluator.evaluate(low_risk_narrative)

        # Verify threshold: risk_score < 20 = QUALIFYING
        if result.risk_score < 20:
            assert result.classification == "QUALIFYING"
        else:
            assert result.classification == "NON_QUALIFYING"


class TestDeterministicScoring:
    """Test that scoring is deterministic."""

    def test_same_input_same_output(self):
        """Test that same narrative produces identical results."""
        evaluator = RuleBasedEvaluator()
        narrative = "The team performed routine maintenance with great success."

        result1 = evaluator.evaluate(narrative)
        result2 = evaluator.evaluate(narrative)

        assert result1.risk_score == result2.risk_score
        assert result1.classification == result2.classification
        assert len(result1.redline.issues) == len(result2.redline.issues)

    def test_deterministic_across_multiple_runs(self):
        """Test determinism over 10 evaluations."""
        evaluator = RuleBasedEvaluator()
        narrative = "Standard engineering work with business improvements."

        scores = [evaluator.evaluate(narrative).risk_score for _ in range(10)]
        assert all(score == scores[0] for score in scores)


class TestStructuredEvaluationOutput:
    """Test structured evaluation output per Green-Agent-Metrics-Specification.md."""

    def test_returns_evaluation_result(self):
        """Test that evaluator returns EvaluationResult dataclass."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        assert isinstance(result, EvaluationResult)

    def test_contains_primary_metrics(self):
        """Test that result contains primary metrics."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        assert hasattr(result, "classification")
        assert hasattr(result, "confidence")
        assert hasattr(result, "risk_score")
        assert hasattr(result, "risk_category")

    def test_contains_component_scores(self):
        """Test that result contains component scores."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        assert hasattr(result, "component_scores")
        assert "routine_engineering_penalty" in result.component_scores
        assert "vagueness_penalty" in result.component_scores
        assert "business_risk_penalty" in result.component_scores
        assert "experimentation_penalty" in result.component_scores

    def test_risk_category_based_on_score(self):
        """Test that risk category matches risk score."""
        evaluator = RuleBasedEvaluator()

        # Low risk narrative
        low_risk_narrative = """
        The project faced significant technical uncertainty. Experiments failed
        initially with 500ms latency. After iterations, achieved 45ms. Metrics:
        throughput 50,000 req/s, memory 1.2GB.
        """
        low_result = evaluator.evaluate(low_risk_narrative)
        if low_result.risk_score <= 20:
            assert low_result.risk_category == "LOW"

        # High risk narrative
        high_risk_narrative = "Routine maintenance improved market share greatly."
        high_result = evaluator.evaluate(high_risk_narrative)
        if high_result.risk_score > 60:
            assert high_result.risk_category in ("HIGH", "VERY_HIGH", "CRITICAL")

    def test_confidence_in_valid_range(self):
        """Test that confidence is between 0 and 1."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        assert 0 <= result.confidence <= 1


class TestSpecificityDetection:
    """Test specificity penalty component."""

    def test_detects_lack_of_metrics(self):
        """Test that evaluator penalizes lack of specific metrics."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        The system was improved. Performance got better.
        Things work faster now.
        """
        result = evaluator.evaluate(narrative)

        assert result.component_scores["specificity_penalty"] > 0

    def test_rewards_specific_numbers(self):
        """Test that specific numbers reduce specificity penalty."""
        evaluator = RuleBasedEvaluator()
        narrative = """
        Response time improved from 250ms to 45ms.
        Memory usage decreased from 2.4GB to 1.56GB.
        Throughput increased from 1000 to 5000 requests per second.
        """
        result = evaluator.evaluate(narrative)

        # Specific metrics should lower penalty
        assert result.component_scores["specificity_penalty"] < 5


class TestIssueDataclass:
    """Test Issue dataclass structure."""

    def test_issue_creation(self):
        """Test Issue dataclass can be created with required fields."""
        issue = Issue(
            category="routine_engineering",
            severity="high",
            text="debugging existing code",
            suggestion="Document the technical uncertainty being addressed",
        )

        assert issue.category == "routine_engineering"
        assert issue.severity == "high"
        assert issue.text == "debugging existing code"
        assert issue.suggestion == "Document the technical uncertainty being addressed"
