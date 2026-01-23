"""Tests for vagueness detector (STORY-007).

This test module validates the acceptance criteria for STORY-007:
- Detects vague phrases: optimize, improve, enhance, upgrade, better, faster, user experience
- Checks for numeric substantiation (percentages, metrics, measurements)
- Penalizes vague claims without evidence
- Returns component score (0-25) based on vagueness density
- Passes test: 'improved performance' scores high, 'reduced latency by 40ms' scores low
"""

import pytest

from bulletproof_green.rules.vagueness_detector import VaguenessDetector


class TestVagueKeywordDetection:
    """Test detection of vague phrases."""

    def test_detects_optimize_keyword(self):
        """Test detection of 'optimize' keyword."""
        detector = VaguenessDetector()
        narrative = "We optimized the system to make it faster."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert len(result["detections"]) > 0
        assert any("optimize" in d["phrase"].lower() for d in result["detections"])

    def test_detects_improve_keyword(self):
        """Test detection of 'improve' keyword."""
        detector = VaguenessDetector()
        narrative = "The goal was to improve performance across the system."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("improve" in d["phrase"].lower() for d in result["detections"])

    def test_detects_enhance_keyword(self):
        """Test detection of 'enhance' keyword."""
        detector = VaguenessDetector()
        narrative = "We enhanced the user experience with better features."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("enhance" in d["phrase"].lower() for d in result["detections"])

    def test_detects_upgrade_keyword(self):
        """Test detection of 'upgrade' keyword."""
        detector = VaguenessDetector()
        narrative = "We upgraded the system for better performance."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("upgrade" in d["phrase"].lower() for d in result["detections"])

    def test_detects_better_keyword(self):
        """Test detection of 'better' keyword."""
        detector = VaguenessDetector()
        narrative = "The new approach produced better results."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("better" in d["phrase"].lower() for d in result["detections"])

    def test_detects_faster_keyword(self):
        """Test detection of 'faster' keyword."""
        detector = VaguenessDetector()
        narrative = "We made the application faster for users."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("faster" in d["phrase"].lower() for d in result["detections"])

    def test_detects_user_experience_phrase(self):
        """Test detection of 'user experience' phrase."""
        detector = VaguenessDetector()
        narrative = "Our focus was improving user experience."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("user experience" in d["phrase"].lower() for d in result["detections"])

    def test_detects_all_vague_phrases(self):
        """Test that detector recognizes all vague phrases from acceptance criteria."""
        detector = VaguenessDetector()

        # Narrative containing all vague phrases
        narrative = """
        We optimized the system to improve performance and enhance the user experience.
        The upgrade made everything better and faster.
        """

        result = detector.analyze(narrative)

        # Should detect multiple vague phrases
        unique_phrases = set(d["phrase"] for d in result["detections"])
        assert len(unique_phrases) >= 5


class TestNumericSubstantiation:
    """Test checking for numeric substantiation."""

    def test_recognizes_percentage_as_substantiation(self):
        """Test that percentages count as numeric substantiation."""
        detector = VaguenessDetector()
        narrative = "We improved performance by 25% through caching."

        result = detector.analyze(narrative)

        # Should detect 'improve' but score should be reduced due to percentage
        assert result["score"] < 15  # Lower than purely vague

    def test_recognizes_measurement_as_substantiation(self):
        """Test that measurements count as numeric substantiation."""
        detector = VaguenessDetector()
        narrative = "We reduced latency by 40ms using new algorithms."

        result = detector.analyze(narrative)

        # Should detect 'reduced' but score should be low due to measurement
        assert result["score"] < 10

    def test_recognizes_metrics_as_substantiation(self):
        """Test that numeric metrics count as substantiation."""
        detector = VaguenessDetector()
        narrative = "We improved throughput from 1000 to 1500 requests per second."

        result = detector.analyze(narrative)

        # Should detect 'improve' but score should be low due to metrics
        assert result["score"] < 10

    def test_penalizes_vague_claims_without_evidence(self):
        """Test that vague claims without numbers receive high penalty."""
        detector = VaguenessDetector()
        narrative_with_evidence = "We improved latency from 500ms to 300ms."
        narrative_without_evidence = "We improved latency."

        result_with = detector.analyze(narrative_with_evidence)
        result_without = detector.analyze(narrative_without_evidence)

        # Narrative without evidence should score higher (worse)
        assert result_without["score"] > result_with["score"]


class TestComponentScore:
    """Test component score calculation (0-25 range)."""

    def test_returns_score_in_range_0_to_25(self):
        """Test that component score is between 0 and 25."""
        detector = VaguenessDetector()
        narrative = "We improved and optimized the system."

        result = detector.analyze(narrative)

        assert 0 <= result["score"] <= 25

    def test_score_increases_with_vagueness_density(self):
        """Test that score increases with more vague phrases."""
        detector = VaguenessDetector()

        # Narrative with few vague phrases
        narrative_low = "We reduced latency from 200ms to 150ms using caching."
        result_low = detector.analyze(narrative_low)

        # Narrative with many vague phrases
        narrative_high = """
        We improved everything and optimized the system. The upgrade enhanced
        the user experience and made it better and faster.
        """
        result_high = detector.analyze(narrative_high)

        assert result_high["score"] > result_low["score"]

    def test_zero_score_for_no_vagueness(self):
        """Test that score is 0 when no vague phrases found."""
        detector = VaguenessDetector()
        narrative = "We reduced latency from 500ms to 300ms through algorithmic changes."

        result = detector.analyze(narrative)

        assert result["score"] == 0
        assert len(result["detections"]) == 0


class TestAcceptanceCriteria:
    """Test the specific acceptance criteria from STORY-007."""

    def test_improved_performance_scores_high(self):
        """Test that 'improved performance' without metrics scores high."""
        detector = VaguenessDetector()

        narrative = "We improved performance significantly."

        result = detector.analyze(narrative)

        # Should score high due to vague claim without substantiation
        assert result["score"] > 15

    def test_reduced_latency_by_40ms_scores_low(self):
        """Test that 'reduced latency by 40ms' scores low."""
        detector = VaguenessDetector()

        narrative = "We reduced latency by 40ms using a new caching strategy."

        result = detector.analyze(narrative)

        # Should score low due to specific measurement
        assert result["score"] < 10


class TestRejectionReasons:
    """Test that detections include appropriate reasons."""

    def test_each_detection_includes_reason(self):
        """Test that each detection includes a reason."""
        detector = VaguenessDetector()
        narrative = "We improved the system to make it faster."

        result = detector.analyze(narrative)

        # Each detection should have a reason
        assert all("reason" in d for d in result["detections"])
        assert all(len(d["reason"]) > 0 for d in result["detections"])

    def test_reason_explains_vagueness_issue(self):
        """Test that reasons explain why vague language is problematic."""
        detector = VaguenessDetector()
        narrative = "We optimized performance."

        result = detector.analyze(narrative)

        # At least one reason should mention substantiation or metrics
        reasons = [d["reason"] for d in result["detections"]]
        assert any("substantiation" in r.lower() or "metric" in r.lower()
                   or "measurement" in r.lower() for r in reasons)


class TestResultStructure:
    """Test the structure of the returned result."""

    def test_result_contains_score_field(self):
        """Test that result contains 'score' field."""
        detector = VaguenessDetector()
        narrative = "We improved the system."

        result = detector.analyze(narrative)

        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_result_contains_detections_field(self):
        """Test that result contains 'detections' field."""
        detector = VaguenessDetector()
        narrative = "We optimized performance."

        result = detector.analyze(narrative)

        assert "detections" in result
        assert isinstance(result["detections"], list)

    def test_detection_contains_required_fields(self):
        """Test that each detection contains phrase and reason fields."""
        detector = VaguenessDetector()
        narrative = "We enhanced the user experience."

        result = detector.analyze(narrative)

        if result["detections"]:  # If any detections found
            detection = result["detections"][0]
            assert "phrase" in detection
            assert "reason" in detection
            assert isinstance(detection["phrase"], str)
            assert isinstance(detection["reason"], str)
