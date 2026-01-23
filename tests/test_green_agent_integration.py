"""Integration tests for NarrativeEvaluator with detectors (STORY-010).

This test module validates the acceptance criteria for STORY-010:
- NarrativeEvaluator imports and instantiates RoutineEngineeringDetector, VaguenessDetector,
  ExperimentationChecker, and RiskScorer
- evaluate() method calls each detector's analyze() method with the narrative
- Component scores from detectors are aggregated using RiskScorer.calculate_risk()
- Returns structured dict (not string) with risk_score, classification, component_scores, redline
- component_scores dict contains all 5 components: routine_engineering, vagueness,
  business_risk, experimentation, specificity
- redline dict contains detection details from each detector for transparency
- Integration tests verify purple agent narrative → green agent evaluation returns proper weighted scores
- Evaluator no longer uses simple keyword heuristics from STORY-005 placeholder implementation
"""

import pytest

from bulletproof_green.evaluator import NarrativeEvaluator


class TestNarrativeEvaluatorDetectorIntegration:
    """Test that NarrativeEvaluator integrates all detectors correctly."""

    def test_evaluator_returns_structured_dict_not_string(self):
        """Test that evaluate() returns a dict, not a string."""
        evaluator = NarrativeEvaluator()
        narrative = "We developed a novel machine learning algorithm."

        result = evaluator.evaluate(narrative)

        # Must return dict, not string
        assert isinstance(result, dict)
        assert not isinstance(result, str)

    def test_evaluator_returns_risk_score(self):
        """Test that result includes risk_score as integer 0-100."""
        evaluator = NarrativeEvaluator()
        narrative = "We conducted experiments to solve technical uncertainty."

        result = evaluator.evaluate(narrative)

        assert "risk_score" in result
        assert isinstance(result["risk_score"], int)
        assert 0 <= result["risk_score"] <= 100

    def test_evaluator_returns_classification(self):
        """Test that result includes classification (QUALIFYING or NON_QUALIFYING)."""
        evaluator = NarrativeEvaluator()
        narrative = "We researched novel algorithms for data processing."

        result = evaluator.evaluate(narrative)

        assert "classification" in result
        assert result["classification"] in ["QUALIFYING", "NON_QUALIFYING"]

    def test_evaluator_returns_component_scores_dict(self):
        """Test that result includes component_scores as dict."""
        evaluator = NarrativeEvaluator()
        narrative = "We developed novel machine learning techniques."

        result = evaluator.evaluate(narrative)

        assert "component_scores" in result
        assert isinstance(result["component_scores"], dict)

    def test_component_scores_contains_all_five_components(self):
        """Test that component_scores dict has all 5 required components."""
        evaluator = NarrativeEvaluator()
        narrative = "Research into novel technical solutions."

        result = evaluator.evaluate(narrative)

        component_scores = result["component_scores"]
        assert "routine_engineering" in component_scores
        assert "vagueness" in component_scores
        assert "business_risk" in component_scores
        assert "experimentation" in component_scores
        assert "specificity" in component_scores

    def test_evaluator_returns_redline_dict(self):
        """Test that result includes redline dict with detection details."""
        evaluator = NarrativeEvaluator()
        narrative = "We fixed bugs in the production system."

        result = evaluator.evaluate(narrative)

        assert "redline" in result
        assert isinstance(result["redline"], dict)

    def test_redline_contains_detector_results(self):
        """Test that redline dict contains details from each detector."""
        evaluator = NarrativeEvaluator()
        narrative = "We debugged and fixed production issues with routine maintenance."

        result = evaluator.evaluate(narrative)

        redline = result["redline"]
        # Should have entries for at least some detectors
        assert isinstance(redline, dict)
        # Redline should not be empty for narrative with detected issues
        assert len(redline) > 0


class TestRoutineEngineeringDetectorIntegration:
    """Test that RoutineEngineeringDetector is properly integrated."""

    def test_routine_engineering_score_increases_with_routine_keywords(self):
        """Test that routine engineering keywords increase component score."""
        evaluator = NarrativeEvaluator()

        # Narrative with NO routine keywords
        clean_narrative = "We researched novel algorithms using experimentation."
        clean_result = evaluator.evaluate(clean_narrative)

        # Narrative WITH routine keywords
        routine_narrative = "We debugged bugs and performed maintenance on production issues."
        routine_result = evaluator.evaluate(routine_narrative)

        # Routine narrative should have higher routine_engineering score
        assert (
            routine_result["component_scores"]["routine_engineering"]
            > clean_result["component_scores"]["routine_engineering"]
        )

    def test_routine_narrative_increases_overall_risk_score(self):
        """Test that routine engineering patterns increase overall risk_score."""
        evaluator = NarrativeEvaluator()

        clean_narrative = "We conducted experiments on novel algorithms."
        clean_result = evaluator.evaluate(clean_narrative)

        routine_narrative = "We fixed bugs, debugged production issues, and performed routine maintenance."
        routine_result = evaluator.evaluate(routine_narrative)

        # Routine narrative should have higher overall risk
        assert routine_result["risk_score"] > clean_result["risk_score"]


class TestVaguenessDetectorIntegration:
    """Test that VaguenessDetector is properly integrated."""

    def test_vagueness_score_increases_with_vague_phrases(self):
        """Test that vague phrases without substantiation increase component score."""
        evaluator = NarrativeEvaluator()

        # Narrative with specific metrics
        specific_narrative = "We reduced latency by 40ms and increased throughput by 25%."
        specific_result = evaluator.evaluate(specific_narrative)

        # Narrative with vague phrases, no metrics
        vague_narrative = "We improved performance and enhanced user experience significantly."
        vague_result = evaluator.evaluate(vague_narrative)

        # Vague narrative should have higher vagueness score
        assert vague_result["component_scores"]["vagueness"] > specific_result["component_scores"]["vagueness"]

    def test_vague_narrative_increases_overall_risk_score(self):
        """Test that vague language increases overall risk_score."""
        evaluator = NarrativeEvaluator()

        specific_narrative = "We reduced response time from 100ms to 60ms."
        specific_result = evaluator.evaluate(specific_narrative)

        vague_narrative = "We improved performance and made it faster and better."
        vague_result = evaluator.evaluate(vague_narrative)

        # Vague narrative should have higher overall risk
        assert vague_result["risk_score"] > specific_result["risk_score"]


class TestExperimentationCheckerIntegration:
    """Test that ExperimentationChecker is properly integrated."""

    def test_experimentation_score_decreases_with_experimentation_evidence(self):
        """Test that experimentation evidence decreases component score (lower risk)."""
        evaluator = NarrativeEvaluator()

        # Narrative WITHOUT experimentation evidence
        no_exp_narrative = "We built a new system."
        no_exp_result = evaluator.evaluate(no_exp_narrative)

        # Narrative WITH experimentation evidence
        exp_narrative = (
            "We faced uncertainty in our approach. We tested multiple alternatives, "
            "tried different solutions, and documented failures when approaches didn't work."
        )
        exp_result = evaluator.evaluate(exp_narrative)

        # Experimentation narrative should have LOWER experimentation score (less risk)
        assert exp_result["component_scores"]["experimentation"] < no_exp_result["component_scores"]["experimentation"]

    def test_experimentation_evidence_decreases_overall_risk_score(self):
        """Test that experimentation evidence decreases overall risk_score."""
        evaluator = NarrativeEvaluator()

        no_exp_narrative = "We built a system."
        no_exp_result = evaluator.evaluate(no_exp_narrative)

        exp_narrative = (
            "We explored uncertain technical challenges through hypothesis testing. "
            "We tried multiple alternatives, compared different approaches, and documented failed attempts."
        )
        exp_result = evaluator.evaluate(exp_narrative)

        # Experimentation should lower overall risk
        assert exp_result["risk_score"] < no_exp_result["risk_score"]


class TestRiskScorerIntegration:
    """Test that RiskScorer is properly integrated for aggregation."""

    def test_risk_scorer_aggregates_component_scores(self):
        """Test that RiskScorer combines all component scores correctly."""
        evaluator = NarrativeEvaluator()

        # Narrative with multiple risk factors
        narrative = (
            "We debugged production issues and performed routine maintenance. "
            "We improved performance and enhanced user experience. "
            "We built a new system without testing alternatives."
        )

        result = evaluator.evaluate(narrative)

        # Risk score should be sum of component scores
        component_sum = sum(result["component_scores"].values())
        assert result["risk_score"] == component_sum

    def test_classification_follows_threshold_logic(self):
        """Test that classification is QUALIFYING when risk < 20, else NON_QUALIFYING."""
        evaluator = NarrativeEvaluator()

        # Low-risk qualifying narrative
        qualifying_narrative = (
            "We researched novel algorithms facing technical uncertainty. "
            "We reduced latency from 100ms to 60ms through systematic experimentation. "
            "We tested multiple alternatives and documented failed approaches."
        )
        qualifying_result = evaluator.evaluate(qualifying_narrative)

        if qualifying_result["risk_score"] < 20:
            assert qualifying_result["classification"] == "QUALIFYING"

        # High-risk non-qualifying narrative
        non_qualifying_narrative = (
            "We debugged bugs and fixed production issues through routine maintenance. "
            "We improved performance and made it faster and better. "
            "We upgraded the system and optimized code cleanup."
        )
        non_qualifying_result = evaluator.evaluate(non_qualifying_narrative)

        if non_qualifying_result["risk_score"] >= 20:
            assert non_qualifying_result["classification"] == "NON_QUALIFYING"


class TestWeightedScoringIntegration:
    """Test that weighted scoring (30%, 25%, 20%, 15%, 10%) is applied correctly."""

    def test_routine_engineering_has_highest_weight(self):
        """Test that routine_engineering has 30% weight (highest impact)."""
        evaluator = NarrativeEvaluator()

        # Narrative with ONLY routine engineering issues
        narrative = (
            "We debugged bugs, fixed production issues, performed maintenance, "
            "refactored code, upgraded systems, migrated data, optimized performance, "
            "performed performance tuning, and did code cleanup."
        )

        result = evaluator.evaluate(narrative)

        # Routine engineering should contribute significantly to risk score
        routine_score = result["component_scores"]["routine_engineering"]
        total_score = result["risk_score"]

        # Routine engineering should be a major portion of total risk
        assert routine_score >= 20  # Should be high
        assert routine_score / total_score >= 0.25  # Should be at least 25% of total


class TestPurpleAgentNarrativeIntegration:
    """Test integration with purple agent generated narratives (end-to-end)."""

    def test_qualifying_narrative_from_purple_agent(self):
        """Test evaluation of qualifying narrative (like purple agent would generate)."""
        evaluator = NarrativeEvaluator()

        # Simulated purple agent qualifying narrative
        narrative = """
        We faced significant technical uncertainty in developing a real-time anomaly detection
        system for high-frequency trading data. The uncertainty stemmed from the need to process
        1 million events per second while maintaining sub-5ms latency.

        We hypothesized that a novel sliding window algorithm with adaptive thresholds could
        solve this challenge. We tested three alternative approaches: fixed-window aggregation,
        streaming quantiles, and our proposed adaptive method.

        The fixed-window approach failed due to 200ms latency. The streaming quantile method
        was unsuccessful as it couldn't handle burst traffic patterns. Our adaptive approach
        reduced latency from 200ms to 3.2ms and increased throughput by 40x.

        We documented each failed attempt and measured performance at each stage.
        """

        result = evaluator.evaluate(narrative)

        # Should be classified as QUALIFYING (low risk)
        assert result["risk_score"] < 20
        assert result["classification"] == "QUALIFYING"
        assert result["component_scores"]["routine_engineering"] < 10
        assert result["component_scores"]["vagueness"] < 10
        assert result["component_scores"]["experimentation"] < 5

    def test_non_qualifying_narrative_from_purple_agent(self):
        """Test evaluation of non-qualifying narrative (like purple agent might generate for testing)."""
        evaluator = NarrativeEvaluator()

        # Simulated purple agent non-qualifying narrative
        narrative = """
        We fixed several bugs in the production system and performed routine maintenance.
        The team debugged issues and optimized performance to improve user experience.
        We upgraded the system and enhanced the codebase through refactoring and code cleanup.
        Overall, we made the system better and faster with significant improvements.
        """

        result = evaluator.evaluate(narrative)

        # Should be classified as NON_QUALIFYING (high risk)
        assert result["risk_score"] >= 20
        assert result["classification"] == "NON_QUALIFYING"
        assert result["component_scores"]["routine_engineering"] > 15
        assert result["component_scores"]["vagueness"] > 10


class TestNoLongerUsesSimpleHeuristics:
    """Test that evaluator no longer uses simple keyword heuristics from STORY-005."""

    def test_uses_detector_based_scoring_not_simple_keywords(self):
        """Test that evaluator uses detectors instead of simple keyword counting."""
        evaluator = NarrativeEvaluator()

        # A narrative that would score differently with simple heuristics vs detectors
        # This narrative has "experiment" keyword but lacks full experimentation evidence
        narrative = "We performed an experiment to improve the system."

        result = evaluator.evaluate(narrative)

        # With detectors, this should still have some experimentation risk
        # because it lacks alternatives and failures documentation
        # Simple heuristics would give it a free pass just for "experiment" keyword
        assert result["component_scores"]["experimentation"] > 0

        # Result should be a dict (detector-based) not string (old heuristic-based)
        assert isinstance(result, dict)
