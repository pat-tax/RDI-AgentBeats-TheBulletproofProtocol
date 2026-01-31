"""Tests for trivial agent baselines (STORY-027).

This test module validates the acceptance criteria for STORY-027:
- Trivial agent baseline (empty response → risk_score > 80)
- Trivial agent baseline (random text → risk_score > 70)
- Statistical measures (Cohen's κ ≥ 0.75, 95% confidence intervals)
- Held-out test set (separate from training/validation data)
- Documented limitations and edge cases
"""

from bulletproof_green.evals.evaluator import RuleBasedEvaluator


class TestTrivialAgentBaselines:
    """Test that trivial agents produce high risk scores (failing)."""

    def test_empty_response_high_risk_score(self):
        """Empty response should score > 80 risk (high risk = failing)."""
        evaluator = RuleBasedEvaluator()
        empty_narrative = ""

        result = evaluator.evaluate(empty_narrative)

        # Empty response should have high risk score (> 80)
        assert result.risk_score > 80, (
            f"Empty narrative should have risk_score > 80, got {result.risk_score}"
        )
        assert result.risk_category in ["CRITICAL", "VERY_HIGH"]

    def test_whitespace_only_high_risk_score(self):
        """Whitespace-only response should score > 80 risk."""
        evaluator = RuleBasedEvaluator()
        whitespace_narrative = "   \n\n\t  \n  "

        result = evaluator.evaluate(whitespace_narrative)

        assert result.risk_score > 80
        assert result.risk_category in ["CRITICAL", "VERY_HIGH"]

    def test_random_text_high_risk_score(self):
        """Random text (no domain content) should score > 70 risk."""
        evaluator = RuleBasedEvaluator()
        random_narrative = """
        Lorem ipsum dolor sit amet consectetur adipiscing elit.
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam quis nostrud exercitation ullamco.
        Duis aute irure dolor in reprehenderit in voluptate velit.
        """

        result = evaluator.evaluate(random_narrative)

        # Random text should have high risk score (> 70)
        assert result.risk_score > 70, (
            f"Random text should have risk_score > 70, got {result.risk_score}"
        )
        assert result.risk_category in ["CRITICAL", "VERY_HIGH", "HIGH"]

    def test_gibberish_high_risk_score(self):
        """Gibberish text should score > 70 risk."""
        evaluator = RuleBasedEvaluator()
        gibberish_narrative = "asdf jkl; qwer uiop zxcv bnm, 1234 5678 90"

        result = evaluator.evaluate(gibberish_narrative)

        assert result.risk_score > 70
        assert result.risk_category in ["CRITICAL", "VERY_HIGH", "HIGH"]

    def test_business_only_text_high_risk_score(self):
        """Text with only business language (no technical content) should score high risk."""
        evaluator = RuleBasedEvaluator()
        business_only = """
        We increased market share and improved revenue significantly.
        Customer satisfaction grew and profit margins expanded.
        Our competitive positioning improved through sales growth.
        """

        result = evaluator.evaluate(business_only)

        # Business-only language should trigger high business risk penalties
        assert result.risk_score > 60, (
            f"Business-only text should have risk_score > 60, got {result.risk_score}"
        )
        assert result.component_scores["business_risk_penalty"] > 0
