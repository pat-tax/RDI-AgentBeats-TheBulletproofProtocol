"""Tests for experimentation checker (STORY-008).

This test module validates the acceptance criteria for STORY-008:
- Checks for uncertainty indicators: unknown, uncertain, unclear, hypothesis, experiment
- Verifies alternatives were evaluated: tried, tested, compared, alternative
- Confirms failures documented: failed, didn't work, unsuccessful, issue
- Returns component score (0-15) based on experimentation evidence
- Passes test: narrative with all 4 elements scores <5, narrative missing elements scores >10
"""

import pytest

from bulletproof_green.rules.experimentation_checker import ExperimentationChecker


class TestUncertaintyIndicators:
    """Test detection of uncertainty indicators."""

    def test_detects_unknown_keyword(self):
        """Test detection of 'unknown' keyword."""
        checker = ExperimentationChecker()
        narrative = "We faced unknown challenges in the implementation."

        result = checker.analyze(narrative)

        assert "uncertainty_found" in result
        assert result["uncertainty_found"] is True

    def test_detects_uncertain_keyword(self):
        """Test detection of 'uncertain' keyword."""
        checker = ExperimentationChecker()
        narrative = "The outcome was uncertain at the project start."

        result = checker.analyze(narrative)

        assert result["uncertainty_found"] is True

    def test_detects_unclear_keyword(self):
        """Test detection of 'unclear' keyword."""
        checker = ExperimentationChecker()
        narrative = "It was unclear which approach would work best."

        result = checker.analyze(narrative)

        assert result["uncertainty_found"] is True

    def test_detects_hypothesis_keyword(self):
        """Test detection of 'hypothesis' keyword."""
        checker = ExperimentationChecker()
        narrative = "We formed a hypothesis about the optimal algorithm."

        result = checker.analyze(narrative)

        assert result["uncertainty_found"] is True

    def test_detects_experiment_keyword(self):
        """Test detection of 'experiment' keyword."""
        checker = ExperimentationChecker()
        narrative = "We ran experiments to validate our approach."

        result = checker.analyze(narrative)

        assert result["uncertainty_found"] is True


class TestAlternativesEvaluated:
    """Test detection of alternatives evaluation."""

    def test_detects_tried_keyword(self):
        """Test detection of 'tried' keyword."""
        checker = ExperimentationChecker()
        narrative = "We tried multiple approaches to solve the problem."

        result = checker.analyze(narrative)

        assert "alternatives_found" in result
        assert result["alternatives_found"] is True

    def test_detects_tested_keyword(self):
        """Test detection of 'tested' keyword."""
        checker = ExperimentationChecker()
        narrative = "We tested several different algorithms."

        result = checker.analyze(narrative)

        assert result["alternatives_found"] is True

    def test_detects_compared_keyword(self):
        """Test detection of 'compared' keyword."""
        checker = ExperimentationChecker()
        narrative = "We compared various implementation strategies."

        result = checker.analyze(narrative)

        assert result["alternatives_found"] is True

    def test_detects_alternative_keyword(self):
        """Test detection of 'alternative' keyword."""
        checker = ExperimentationChecker()
        narrative = "We explored alternative solutions to the challenge."

        result = checker.analyze(narrative)

        assert result["alternatives_found"] is True


class TestFailuresDocumented:
    """Test detection of documented failures."""

    def test_detects_failed_keyword(self):
        """Test detection of 'failed' keyword."""
        checker = ExperimentationChecker()
        narrative = "Our first approach failed to meet performance targets."

        result = checker.analyze(narrative)

        assert "failures_found" in result
        assert result["failures_found"] is True

    def test_detects_didnt_work_phrase(self):
        """Test detection of 'didn't work' phrase."""
        checker = ExperimentationChecker()
        narrative = "The initial strategy didn't work as expected."

        result = checker.analyze(narrative)

        assert result["failures_found"] is True

    def test_detects_unsuccessful_keyword(self):
        """Test detection of 'unsuccessful' keyword."""
        checker = ExperimentationChecker()
        narrative = "Several attempts were unsuccessful before we succeeded."

        result = checker.analyze(narrative)

        assert result["failures_found"] is True

    def test_detects_issue_keyword(self):
        """Test detection of 'issue' keyword."""
        checker = ExperimentationChecker()
        narrative = "We encountered issues with the initial implementation."

        result = checker.analyze(narrative)

        assert result["failures_found"] is True


class TestComponentScore:
    """Test component score calculation (0-15 range)."""

    def test_returns_score_in_range_0_to_15(self):
        """Test that component score is between 0 and 15."""
        checker = ExperimentationChecker()
        narrative = "We had some unknown factors and tried different approaches."

        result = checker.analyze(narrative)

        assert 0 <= result["score"] <= 15

    def test_score_decreases_with_more_experimentation_evidence(self):
        """Test that score decreases with more experimentation elements."""
        checker = ExperimentationChecker()

        # Narrative with no experimentation evidence
        narrative_no_exp = "We implemented the feature using standard patterns."
        result_no_exp = checker.analyze(narrative_no_exp)

        # Narrative with strong experimentation evidence
        narrative_strong_exp = """
        We faced uncertain outcomes and unclear requirements. Our hypothesis was
        that a novel algorithm would work, so we experimented with different approaches.
        We tried multiple strategies, tested various implementations, and compared results.
        Several attempts failed, some solutions didn't work, and we had unsuccessful trials,
        but we documented all issues encountered.
        """
        result_strong_exp = checker.analyze(narrative_strong_exp)

        # More experimentation evidence should result in lower score (less risk)
        assert result_strong_exp["score"] < result_no_exp["score"]


class TestAcceptanceCriteria:
    """Test the specific acceptance criteria from STORY-008."""

    def test_narrative_with_all_elements_scores_below_5(self):
        """Test that narrative with all 4 elements scores <5."""
        checker = ExperimentationChecker()

        # Narrative with uncertainty, alternatives, failures, and experimentation
        narrative = """
        At the start, it was unclear which approach would work, and we faced
        uncertain outcomes with unknown technical challenges. We formed a hypothesis
        and ran experiments to test it. We tried multiple solutions, tested various
        algorithms, compared different approaches, and explored alternatives.
        Some attempts failed, several strategies didn't work, we had unsuccessful
        trials, and we documented all issues encountered along the way.
        """

        result = checker.analyze(narrative)

        assert result["score"] < 5

    def test_narrative_missing_elements_scores_above_10(self):
        """Test that narrative missing experimentation elements scores >10."""
        checker = ExperimentationChecker()

        # Narrative without experimentation elements
        narrative = """
        We implemented the new authentication system using industry best practices.
        The team followed the standard development process and delivered the feature
        on schedule. The solution works as expected and meets all requirements.
        """

        result = checker.analyze(narrative)

        assert result["score"] > 10


class TestRejectionReasons:
    """Test that missing elements are identified."""

    def test_identifies_missing_uncertainty(self):
        """Test that missing uncertainty indicators are flagged."""
        checker = ExperimentationChecker()
        narrative = "We implemented the feature successfully."

        result = checker.analyze(narrative)

        assert "uncertainty_found" in result
        if not result["uncertainty_found"]:
            assert result["score"] > 0

    def test_identifies_missing_alternatives(self):
        """Test that missing alternatives evaluation is flagged."""
        checker = ExperimentationChecker()
        narrative = "We implemented the feature successfully."

        result = checker.analyze(narrative)

        assert "alternatives_found" in result
        if not result["alternatives_found"]:
            assert result["score"] > 0

    def test_identifies_missing_failures(self):
        """Test that missing failure documentation is flagged."""
        checker = ExperimentationChecker()
        narrative = "We implemented the feature successfully."

        result = checker.analyze(narrative)

        assert "failures_found" in result
        if not result["failures_found"]:
            assert result["score"] > 0


class TestResultStructure:
    """Test the structure of the returned result."""

    def test_result_contains_score_field(self):
        """Test that result contains 'score' field."""
        checker = ExperimentationChecker()
        narrative = "We experimented with different approaches."

        result = checker.analyze(narrative)

        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_result_contains_experimentation_indicators(self):
        """Test that result contains experimentation indicators."""
        checker = ExperimentationChecker()
        narrative = "We had uncertain requirements and tried various solutions."

        result = checker.analyze(narrative)

        assert "uncertainty_found" in result
        assert "alternatives_found" in result
        assert "failures_found" in result
        assert isinstance(result["uncertainty_found"], bool)
        assert isinstance(result["alternatives_found"], bool)
        assert isinstance(result["failures_found"], bool)
