"""Tests for risk scorer (STORY-009).

This test module validates the acceptance criteria for STORY-009:
- Combines routine_engineering (30%), vagueness (25%), business_risk (20%),
  experimentation (15%), specificity (10%)
- Returns risk_score: 0-100 integer
- Returns classification: QUALIFYING if risk_score < 20, else NON_QUALIFYING
- Returns component_scores breakdown for transparency
- Passes test: perfect narrative scores <10, problematic narrative scores >60
"""

import pytest

from bulletproof_green.scorer import RiskScorer


class TestRiskScoreCalculation:
    """Test risk score calculation and weighting."""

    def test_returns_risk_score_as_integer(self):
        """Test that risk_score is an integer."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 10,
            "vagueness": 5,
            "business_risk": 0,
            "experimentation": 5,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert "risk_score" in result
        assert isinstance(result["risk_score"], int)

    def test_risk_score_in_range_0_to_100(self):
        """Test that risk_score is between 0 and 100."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 30,
            "vagueness": 25,
            "business_risk": 20,
            "experimentation": 15,
            "specificity": 10,
        }

        result = scorer.calculate_risk(component_scores)

        assert 0 <= result["risk_score"] <= 100

    def test_applies_routine_engineering_weight_30_percent(self):
        """Test that routine_engineering has 30% weight."""
        scorer = RiskScorer()
        # Only routine_engineering has a score
        component_scores = {
            "routine_engineering": 30,  # Max score
            "vagueness": 0,
            "business_risk": 0,
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        # 30 out of 30 with 30% weight = 30% of 100 = 30
        assert result["risk_score"] == 30

    def test_applies_vagueness_weight_25_percent(self):
        """Test that vagueness has 25% weight."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 0,
            "vagueness": 25,  # Max score
            "business_risk": 0,
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        # 25 out of 25 with 25% weight = 25% of 100 = 25
        assert result["risk_score"] == 25

    def test_applies_business_risk_weight_20_percent(self):
        """Test that business_risk has 20% weight."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 0,
            "vagueness": 0,
            "business_risk": 20,  # Max score
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        # 20 out of 20 with 20% weight = 20% of 100 = 20
        assert result["risk_score"] == 20

    def test_applies_experimentation_weight_15_percent(self):
        """Test that experimentation has 15% weight."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 0,
            "vagueness": 0,
            "business_risk": 0,
            "experimentation": 15,  # Max score
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        # 15 out of 15 with 15% weight = 15% of 100 = 15
        assert result["risk_score"] == 15

    def test_applies_specificity_weight_10_percent(self):
        """Test that specificity has 10% weight."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 0,
            "vagueness": 0,
            "business_risk": 0,
            "experimentation": 0,
            "specificity": 10,  # Max score
        }

        result = scorer.calculate_risk(component_scores)

        # 10 out of 10 with 10% weight = 10% of 100 = 10
        assert result["risk_score"] == 10

    def test_combines_all_component_scores_correctly(self):
        """Test that all components are combined with correct weights."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 30,  # 30% weight = 30
            "vagueness": 25,  # 25% weight = 25
            "business_risk": 20,  # 20% weight = 20
            "experimentation": 15,  # 15% weight = 15
            "specificity": 10,  # 10% weight = 10
        }

        result = scorer.calculate_risk(component_scores)

        # Total = 30 + 25 + 20 + 15 + 10 = 100
        assert result["risk_score"] == 100


class TestClassification:
    """Test QUALIFYING vs NON_QUALIFYING classification."""

    def test_classifies_as_qualifying_when_risk_score_below_20(self):
        """Test classification as QUALIFYING when risk_score < 20."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 3,
            "vagueness": 0,
            "business_risk": 0,
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert "classification" in result
        assert result["risk_score"] < 20
        assert result["classification"] == "QUALIFYING"

    def test_classifies_as_non_qualifying_when_risk_score_equals_20(self):
        """Test classification as NON_QUALIFYING when risk_score = 20."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 0,
            "vagueness": 0,
            "business_risk": 20,  # Exactly 20
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert result["risk_score"] == 20
        assert result["classification"] == "NON_QUALIFYING"

    def test_classifies_as_non_qualifying_when_risk_score_above_20(self):
        """Test classification as NON_QUALIFYING when risk_score > 20."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 30,
            "vagueness": 25,
            "business_risk": 0,
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert result["risk_score"] > 20
        assert result["classification"] == "NON_QUALIFYING"


class TestComponentScoresTransparency:
    """Test component_scores breakdown for transparency."""

    def test_returns_component_scores_breakdown(self):
        """Test that result includes component_scores breakdown."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 15,
            "vagueness": 10,
            "business_risk": 5,
            "experimentation": 3,
            "specificity": 2,
        }

        result = scorer.calculate_risk(component_scores)

        assert "component_scores" in result
        assert isinstance(result["component_scores"], dict)

    def test_component_scores_contains_all_components(self):
        """Test that component_scores includes all 5 components."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 10,
            "vagueness": 5,
            "business_risk": 0,
            "experimentation": 5,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert "routine_engineering" in result["component_scores"]
        assert "vagueness" in result["component_scores"]
        assert "business_risk" in result["component_scores"]
        assert "experimentation" in result["component_scores"]
        assert "specificity" in result["component_scores"]

    def test_component_scores_preserves_original_values(self):
        """Test that component_scores preserves original input values."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 12,
            "vagueness": 8,
            "business_risk": 4,
            "experimentation": 6,
            "specificity": 3,
        }

        result = scorer.calculate_risk(component_scores)

        assert result["component_scores"]["routine_engineering"] == 12
        assert result["component_scores"]["vagueness"] == 8
        assert result["component_scores"]["business_risk"] == 4
        assert result["component_scores"]["experimentation"] == 6
        assert result["component_scores"]["specificity"] == 3


class TestAcceptanceCriteria:
    """Test the specific acceptance criteria from STORY-009."""

    def test_perfect_narrative_scores_below_10(self):
        """Test that perfect narrative scores <10."""
        scorer = RiskScorer()

        # Perfect narrative: no routine engineering, no vagueness, good experimentation
        component_scores = {
            "routine_engineering": 0,  # No routine patterns
            "vagueness": 0,  # Specific claims with numbers
            "business_risk": 0,  # No business risk
            "experimentation": 0,  # Strong experimentation evidence
            "specificity": 0,  # Highly specific
        }

        result = scorer.calculate_risk(component_scores)

        assert result["risk_score"] < 10

    def test_problematic_narrative_scores_above_60(self):
        """Test that problematic narrative scores >60."""
        scorer = RiskScorer()

        # Problematic narrative: high routine, high vagueness, no experimentation
        component_scores = {
            "routine_engineering": 30,  # Max routine patterns
            "vagueness": 25,  # Max vagueness
            "business_risk": 20,  # Max business risk
            "experimentation": 15,  # No experimentation evidence
            "specificity": 10,  # Not specific
        }

        result = scorer.calculate_risk(component_scores)

        assert result["risk_score"] > 60


class TestResultStructure:
    """Test the structure of the returned result."""

    def test_result_contains_all_required_fields(self):
        """Test that result contains all required fields."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 10,
            "vagueness": 5,
            "business_risk": 0,
            "experimentation": 5,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert "risk_score" in result
        assert "classification" in result
        assert "component_scores" in result

    def test_risk_score_is_integer_not_float(self):
        """Test that risk_score is integer, not float."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 15,
            "vagueness": 12,
            "business_risk": 8,
            "experimentation": 7,
            "specificity": 5,
        }

        result = scorer.calculate_risk(component_scores)

        assert isinstance(result["risk_score"], int)
        assert not isinstance(result["risk_score"], bool)  # bool is subclass of int


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_handles_zero_scores_for_all_components(self):
        """Test handling of all zeros."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 0,
            "vagueness": 0,
            "business_risk": 0,
            "experimentation": 0,
            "specificity": 0,
        }

        result = scorer.calculate_risk(component_scores)

        assert result["risk_score"] == 0
        assert result["classification"] == "QUALIFYING"

    def test_handles_maximum_scores_for_all_components(self):
        """Test handling of all max scores."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 30,
            "vagueness": 25,
            "business_risk": 20,
            "experimentation": 15,
            "specificity": 10,
        }

        result = scorer.calculate_risk(component_scores)

        assert result["risk_score"] == 100
        assert result["classification"] == "NON_QUALIFYING"

    def test_handles_partial_component_scores(self):
        """Test handling of partial scores."""
        scorer = RiskScorer()
        component_scores = {
            "routine_engineering": 15,  # Half of max
            "vagueness": 12,  # Roughly half
            "business_risk": 10,  # Half of max
            "experimentation": 7,  # Roughly half
            "specificity": 5,  # Half of max
        }

        result = scorer.calculate_risk(component_scores)

        # Should be roughly 50% risk
        assert 45 <= result["risk_score"] <= 55
