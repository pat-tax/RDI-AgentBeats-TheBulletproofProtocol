"""Tests for anti-gaming detection (STORY-036).

This test module validates the acceptance criteria for STORY-036:
- Create adversarial_narratives.json with gaming attempts
- Test rule-based anti-gaming detection
- Include keyword stuffing, overgeneralization, irrelevance tests
- Verify rule-based detectors catch gaming attempts
"""

import json
from pathlib import Path

import pytest

from bulletproof_green.evals.evaluator import RuleBasedEvaluator


class TestAntiGaming:
    """Test that rule-based detectors catch gaming attempts."""

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

    def test_adversarial_narratives_json_exists(self, adversarial_dataset):
        """Acceptance: Create adversarial_narratives.json with gaming attempts."""
        assert isinstance(adversarial_dataset, list)
        assert len(adversarial_dataset) > 0

        # Verify each narrative has required fields
        for narrative in adversarial_dataset:
            assert "id" in narrative
            assert "narrative" in narrative
            assert "attack_type" in narrative
            assert "expected_detection" in narrative
            assert "description" in narrative

    def test_keyword_stuffing_gaming_detected(self, evaluator, adversarial_dataset):
        """Acceptance: Include keyword stuffing tests - verify detectors catch it."""
        # Find keyword stuffing examples
        keyword_stuffing_narratives = [
            item for item in adversarial_dataset if item["attack_type"] == "keyword_stuffing"
        ]

        assert len(keyword_stuffing_narratives) > 0, "Must have keyword stuffing examples"

        # Test that rule-based detector catches keyword stuffing
        for item in keyword_stuffing_narratives:
            if item["expected_detection"]:
                result = evaluator.evaluate(item["narrative"])
                assert result.risk_score > 60, (
                    f"Keyword stuffing {item['id']} should have high risk score, "
                    f"got {result.risk_score}"
                )

    def test_overgeneralization_gaming_detected(self, evaluator, adversarial_dataset):
        """Acceptance: Include overgeneralization tests - verify detectors catch it."""
        # Find overgeneralization examples
        overgeneralization_narratives = [
            item
            for item in adversarial_dataset
            if item["attack_type"] == "overgeneralization"
        ]

        assert len(overgeneralization_narratives) > 0, (
            "Must have overgeneralization examples"
        )

        # Test that rule-based detector catches overgeneralization (vague language)
        for item in overgeneralization_narratives:
            if item["expected_detection"]:
                result = evaluator.evaluate(item["narrative"])
                # Overgeneralization should trigger vagueness penalties
                vagueness_penalty = result.component_scores.get("vagueness_penalty", 0)
                assert vagueness_penalty > 0, (
                    f"Overgeneralization {item['id']} should have vagueness penalty, "
                    f"got {vagueness_penalty}"
                )

    def test_irrelevance_gaming_detected(self, evaluator, adversarial_dataset):
        """Acceptance: Include irrelevance tests - verify detectors catch it."""
        # Find irrelevant content examples
        irrelevant_narratives = [
            item
            for item in adversarial_dataset
            if item["attack_type"] == "irrelevant_content"
        ]

        assert len(irrelevant_narratives) > 0, "Must have irrelevant content examples"

        # Test that rule-based detector catches irrelevant content
        for item in irrelevant_narratives:
            if item["expected_detection"]:
                result = evaluator.evaluate(item["narrative"])
                assert result.risk_score > 40, (
                    f"Irrelevant content {item['id']} should have high risk score, "
                    f"got {result.risk_score}"
                )

    def test_template_gaming_detected(self, evaluator, adversarial_dataset):
        """Verify rule-based detector catches template gaming."""
        # Find template gaming examples
        template_gaming_narratives = [
            item for item in adversarial_dataset if item["attack_type"] == "template_gaming"
        ]

        assert len(template_gaming_narratives) > 0, "Must have template gaming examples"

        # Test that rule-based detector catches template gaming
        for item in template_gaming_narratives:
            if item["expected_detection"]:
                result = evaluator.evaluate(item["narrative"])
                assert result.risk_score > 50, (
                    f"Template gaming {item['id']} should have high risk score, "
                    f"got {result.risk_score}"
                )

    def test_metric_stuffing_detected(self, evaluator, adversarial_dataset):
        """Verify rule-based detector catches superficial metric stuffing."""
        # Find metric stuffing examples
        metric_stuffing_narratives = [
            item
            for item in adversarial_dataset
            if item["attack_type"] == "superficial_metric_stuffing"
        ]

        assert len(metric_stuffing_narratives) > 0, "Must have metric stuffing examples"

        # Test that rule-based detector catches metric stuffing
        for item in metric_stuffing_narratives:
            if item["expected_detection"]:
                result = evaluator.evaluate(item["narrative"])
                assert result.risk_score > 50, (
                    f"Metric stuffing {item['id']} should have high risk score, "
                    f"got {result.risk_score}"
                )

    def test_combined_gaming_detected(self, evaluator, adversarial_dataset):
        """Verify rule-based detector catches combined gaming strategies."""
        # Find combined gaming examples
        combined_gaming_narratives = [
            item for item in adversarial_dataset if item["attack_type"] == "combined_gaming"
        ]

        if len(combined_gaming_narratives) > 0:
            # Test that rule-based detector catches combined gaming
            for item in combined_gaming_narratives:
                if item["expected_detection"]:
                    result = evaluator.evaluate(item["narrative"])
                    assert result.risk_score > 55, (
                        f"Combined gaming {item['id']} should have high risk score, "
                        f"got {result.risk_score}"
                    )

    def test_all_gaming_types_represented(self, adversarial_dataset):
        """Verify adversarial dataset covers required gaming types."""
        # Extract all attack types from dataset
        attack_types = {item["attack_type"] for item in adversarial_dataset}

        # Required gaming types per acceptance criteria
        required_types = {"keyword_stuffing", "overgeneralization", "irrelevant_content"}

        assert required_types.issubset(attack_types), (
            f"Dataset must include {required_types}, found {attack_types}"
        )

    def test_rule_based_detectors_functional(self, evaluator):
        """Verify rule-based detectors are functional and return expected results."""
        # Test with a clean narrative (should have low risk)
        clean_narrative = """
        Our team developed a novel algorithm to reduce database query latency.
        We hypothesized that implementing a custom caching layer would improve performance.
        Initial tests showed cache hit rates of 45%, which was below our 60% target.
        After three iterations of adjusting eviction policies and cache size,
        we achieved 72% cache hit rate with query latency reduced from 150ms to 45ms.
        """

        result = evaluator.evaluate(clean_narrative)
        assert result.risk_score < 60, (
            f"Clean narrative should have low risk score, got {result.risk_score}"
        )

        # Test with obvious gaming attempt (keyword stuffing)
        gaming_narrative = """
        We experimented and experimented and experimented with uncertainty uncertainty
        uncertainty in our hypothesis hypothesis hypothesis testing testing testing.
        We iterated iterated iterated on failures failures failures.
        """

        result = evaluator.evaluate(gaming_narrative)
        assert result.risk_score > 60, (
            f"Gaming narrative should have high risk score, got {result.risk_score}"
        )
