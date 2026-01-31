"""Tests for adversarial narrative detection (STORY-031).

This test module validates the acceptance criteria for STORY-031:
- Adversarial test narratives (keyword stuffing, template gaming)
- LLM reward hacking detection
- Pattern variation resistance
- Robustness tests (capitalization, whitespace, paraphrasing)
- Adversarial test suite
- Gaming detection metrics
"""

import json
from pathlib import Path

import pytest

from bulletproof_green.evals.evaluator import RuleBasedEvaluator


class TestAdversarialNarratives:
    """Test that adversarial gaming attempts are detected and penalized."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance."""
        return RuleBasedEvaluator()

    @pytest.fixture
    def adversarial_dataset(self):
        """Load adversarial narratives dataset."""
        data_path = Path(__file__).parent.parent / "data" / "adversarial_narratives.json"
        with open(data_path) as f:
            return json.load(f)

    def test_adversarial_dataset_exists(self, adversarial_dataset):
        """Adversarial narratives dataset should exist and be valid."""
        assert isinstance(adversarial_dataset, list)
        assert len(adversarial_dataset) > 0

    def test_keyword_stuffing_detected(self, evaluator, adversarial_dataset):
        """Keyword stuffing should result in high risk score (> 60)."""
        # Find keyword stuffing examples from dataset
        keyword_stuffing_narratives = [
            item for item in adversarial_dataset if item["attack_type"] == "keyword_stuffing"
        ]

        assert len(keyword_stuffing_narratives) > 0, "Dataset must contain keyword stuffing examples"

        for item in keyword_stuffing_narratives:
            result = evaluator.evaluate(item["narrative"])

            # Keyword stuffing should be detected as gaming and receive high risk
            assert result.risk_score > 60, (
                f"Keyword stuffing narrative '{item['id']}' should have risk_score > 60, "
                f"got {result.risk_score}"
            )

    def test_template_gaming_detected(self, evaluator, adversarial_dataset):
        """Template gaming (formulaic structure) should be detected."""
        template_gaming_narratives = [
            item for item in adversarial_dataset if item["attack_type"] == "template_gaming"
        ]

        assert len(template_gaming_narratives) > 0, "Dataset must contain template gaming examples"

        for item in template_gaming_narratives:
            result = evaluator.evaluate(item["narrative"])

            # Template gaming should result in moderate to high risk
            assert result.risk_score > 50, (
                f"Template gaming narrative '{item['id']}' should have risk_score > 50, "
                f"got {result.risk_score}"
            )

    def test_capitalization_variation_resistance(self, evaluator):
        """Evaluator should be case-insensitive to pattern matching."""
        # Test with varying capitalization
        base_narrative = """
        Our research focused on technical uncertainty in distributed systems.
        We experimented with novel consensus algorithms. Initial hypothesis failed.
        After iteration we achieved 95% consistency.
        """

        uppercase_narrative = base_narrative.upper()
        lowercase_narrative = base_narrative.lower()
        mixed_narrative = base_narrative.title()

        result_base = evaluator.evaluate(base_narrative)
        result_upper = evaluator.evaluate(uppercase_narrative)
        result_lower = evaluator.evaluate(lowercase_narrative)
        result_mixed = evaluator.evaluate(mixed_narrative)

        # Risk scores should be similar regardless of capitalization (within 10 points)
        assert abs(result_base.risk_score - result_upper.risk_score) < 10
        assert abs(result_base.risk_score - result_lower.risk_score) < 10
        assert abs(result_base.risk_score - result_mixed.risk_score) < 10

    def test_whitespace_variation_resistance(self, evaluator):
        """Evaluator should handle extra whitespace consistently."""
        base_narrative = "Our team researched technical uncertainty. We experimented with algorithms."

        # Add extra whitespace
        whitespace_narrative = "Our  team   researched    technical     uncertainty.  We  experimented  with  algorithms."

        result_base = evaluator.evaluate(base_narrative)
        result_whitespace = evaluator.evaluate(whitespace_narrative)

        # Risk scores should be identical or very close
        assert abs(result_base.risk_score - result_whitespace.risk_score) < 5

    def test_superficial_metric_stuffing(self, evaluator, adversarial_dataset):
        """Superficial metric stuffing should not game the system."""
        metric_stuffing_narratives = [
            item
            for item in adversarial_dataset
            if item["attack_type"] == "superficial_metric_stuffing"
        ]

        assert len(metric_stuffing_narratives) > 0, "Dataset must contain metric stuffing examples"

        for item in metric_stuffing_narratives:
            result = evaluator.evaluate(item["narrative"])

            # Metrics without technical substance should still score high risk
            assert result.risk_score > 50, (
                f"Superficial metrics narrative '{item['id']}' should have risk_score > 50, "
                f"got {result.risk_score}"
            )

    def test_adversarial_dataset_schema(self, adversarial_dataset):
        """Adversarial dataset should follow expected schema."""
        required_fields = {"id", "narrative", "attack_type", "expected_detection", "description"}

        for item in adversarial_dataset:
            assert required_fields.issubset(
                item.keys()
            ), f"Item {item.get('id', 'unknown')} missing required fields"

            assert isinstance(item["id"], str)
            assert isinstance(item["narrative"], str)
            assert isinstance(item["attack_type"], str)
            assert isinstance(item["expected_detection"], bool)
            assert isinstance(item["description"], str)

            # Narrative should not be empty
            assert len(item["narrative"].strip()) > 0

    def test_overgeneralization_gaming(self, evaluator, adversarial_dataset):
        """Overgeneralization (vague technical terms) should be detected."""
        overgeneralization_narratives = [
            item
            for item in adversarial_dataset
            if item["attack_type"] == "overgeneralization"
        ]

        assert len(overgeneralization_narratives) > 0, "Dataset must contain overgeneralization examples"

        for item in overgeneralization_narratives:
            result = evaluator.evaluate(item["narrative"])

            # Overgeneralized narratives should trigger vagueness penalties
            assert result.component_scores["vagueness_penalty"] > 0, (
                f"Overgeneralization narrative '{item['id']}' should have vagueness penalty"
            )

    def test_irrelevant_content_gaming(self, evaluator, adversarial_dataset):
        """Irrelevant technical content should be detected."""
        irrelevant_narratives = [
            item for item in adversarial_dataset if item["attack_type"] == "irrelevant_content"
        ]

        assert len(irrelevant_narratives) > 0, "Dataset must contain irrelevant content examples"

        for item in irrelevant_narratives:
            result = evaluator.evaluate(item["narrative"])

            # Irrelevant content should still result in moderate to high risk
            assert result.risk_score > 40, (
                f"Irrelevant content narrative '{item['id']}' should have risk_score > 40, "
                f"got {result.risk_score}"
            )

    def test_paraphrasing_resistance(self, evaluator):
        """Evaluator should detect patterns even when paraphrased."""
        # Original with clear experimentation
        original = """
        We hypothesized a new caching algorithm could reduce latency.
        Our experiments failed initially due to cache coherency issues.
        After multiple iterations we achieved 87% hit rate improvement.
        """

        # Paraphrased version
        paraphrased = """
        We formed a theory that a novel caching approach might decrease response time.
        Our tests were unsuccessful at first because of synchronization problems.
        Following several refinements we reached an 87% performance boost in cache hits.
        """

        result_original = evaluator.evaluate(original)
        result_paraphrased = evaluator.evaluate(paraphrased)

        # Both should score similarly (within 15 points)
        # This tests pattern variation resistance
        assert abs(result_original.risk_score - result_paraphrased.risk_score) < 15

    def test_combined_gaming_strategies(self, evaluator, adversarial_dataset):
        """Combined gaming strategies should be detected."""
        combined_narratives = [
            item
            for item in adversarial_dataset
            if item["attack_type"] == "combined_gaming"
        ]

        if len(combined_narratives) > 0:
            for item in combined_narratives:
                result = evaluator.evaluate(item["narrative"])

                # Combined gaming should result in high risk
                assert result.risk_score > 55, (
                    f"Combined gaming narrative '{item['id']}' should have risk_score > 55, "
                    f"got {result.risk_score}"
                )

    def test_adversarial_vs_legitimate_differentiation(self, evaluator):
        """Evaluator should differentiate between adversarial and legitimate narratives."""
        # Legitimate narrative
        legitimate = """
        We investigated novel consensus mechanisms for distributed databases under
        network partition scenarios. The technical uncertainty centered on whether
        we could maintain linearizability while achieving sub-100ms latency. Our
        initial hypothesis involved hybrid vector clocks, but experiments revealed
        unexpected clock drift patterns. We tested five alternative approaches,
        including custom time-sync protocols. After discovering that network topology
        significantly impacted synchronization, we achieved 95% reliability with
        73ms average latency.
        """

        # Adversarial: keyword stuffed
        adversarial = """
        We experimented experimented experimented with hypothesis hypothesis
        uncertainty uncertainty failure failure iteration iteration technical
        technical algorithms algorithms. We tested tested tested and achieved
        95% 95% 95% improvement improvement improvement.
        """

        result_legitimate = evaluator.evaluate(legitimate)
        result_adversarial = evaluator.evaluate(adversarial)

        # Legitimate should score significantly lower risk than adversarial
        assert result_legitimate.risk_score < result_adversarial.risk_score - 20, (
            f"Legitimate narrative should score at least 20 points lower risk than "
            f"adversarial. Got legitimate={result_legitimate.risk_score}, "
            f"adversarial={result_adversarial.risk_score}"
        )
