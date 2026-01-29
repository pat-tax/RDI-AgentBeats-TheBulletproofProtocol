"""Tests for STORY-020: Update output schema per specification.

Validates core behavior:
- Complete output structure matches spec
- Severity counts match issues array
- Total penalty equals sum of components
- JSON serialization works
- Backwards compatibility maintained
"""

import json
import uuid

from bulletproof_green.evals.evaluator import RuleBasedEvaluator


class TestCompleteOutputSchema:
    """Test complete output schema structure."""

    def test_complete_output_structure(self):
        """Test that evaluation produces complete expected structure."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Routine maintenance to improve market share.")

        output = result.to_dict()

        # Top-level fields
        assert "version" in output
        assert "timestamp" in output
        assert "narrative_id" in output
        assert "primary_metrics" in output
        assert "component_scores" in output
        assert "diagnostics" in output
        assert "redline" in output
        assert "metadata" in output

        # Primary metrics fields
        pm = output["primary_metrics"]
        assert all(
            k in pm
            for k in [
                "compliance_classification",
                "confidence",
                "risk_score",
                "risk_category",
                "predicted_audit_outcome",
            ]
        )

        # Component scores fields
        cs = output["component_scores"]
        assert all(
            k in cs
            for k in [
                "routine_engineering_penalty",
                "vagueness_penalty",
                "business_risk_penalty",
                "experimentation_penalty",
                "specificity_penalty",
                "total_penalty",
            ]
        )

        # Diagnostics fields
        diag = output["diagnostics"]
        assert all(
            k in diag
            for k in [
                "routine_patterns_detected",
                "vague_phrases_detected",
                "business_keywords_detected",
                "experimentation_evidence_score",
                "specificity_score",
            ]
        )

        # Redline fields
        redline = output["redline"]
        assert all(k in redline for k in ["total_issues", "critical", "high", "medium", "issues"])

        # Metadata fields
        meta = output["metadata"]
        assert all(k in meta for k in ["evaluation_time_ms", "rules_version", "irs_citations"])


class TestNarrativeID:
    """Test narrative ID behavior."""

    def test_different_evaluations_get_different_ids(self):
        """Test that each evaluation gets a unique narrative_id."""
        evaluator = RuleBasedEvaluator()

        result1 = evaluator.evaluate("Sample narrative 1.")
        result2 = evaluator.evaluate("Sample narrative 2.")

        id1 = result1.to_dict()["narrative_id"]
        id2 = result2.to_dict()["narrative_id"]

        assert id1 != id2
        uuid.UUID(id1)  # Validates UUID format
        uuid.UUID(id2)


class TestComponentScoresCalculation:
    """Test component scores calculation logic."""

    def test_total_penalty_equals_sum(self):
        """Test that total_penalty equals sum of individual penalties."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Routine maintenance with vague improvements for market share.")

        cs = result.to_dict()["component_scores"]

        expected_total = (
            cs["routine_engineering_penalty"]
            + cs["vagueness_penalty"]
            + cs["business_risk_penalty"]
            + cs["experimentation_penalty"]
            + cs["specificity_penalty"]
        )

        assert cs["total_penalty"] == expected_total


class TestRedlineSeverityCounts:
    """Test redline severity counts match issues."""

    def test_severity_counts_match_issues(self):
        """Test that severity counts match the issues array."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Routine maintenance with vague improvements for market share.")

        redline = result.to_dict()["redline"]

        critical_count = sum(1 for i in redline["issues"] if i["severity"] == "critical")
        high_count = sum(1 for i in redline["issues"] if i["severity"] == "high")
        medium_count = sum(1 for i in redline["issues"] if i["severity"] == "medium")

        assert redline["critical"] == critical_count
        assert redline["high"] == high_count
        assert redline["medium"] == medium_count
        assert redline["total_issues"] == len(redline["issues"])


class TestDiagnosticsScoreRanges:
    """Test diagnostic score value ranges."""

    def test_score_ranges(self):
        """Test that scores are within valid ranges."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Experiments failed, hypotheses tested with 45ms latency.")

        diag = result.to_dict()["diagnostics"]

        assert 0.0 <= diag["experimentation_evidence_score"] <= 1.0
        assert 0.0 <= diag["specificity_score"] <= 1.0


class TestJSONSerialization:
    """Test JSON serialization."""

    def test_roundtrip_serialization(self):
        """Test that output can be serialized and deserialized."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        json_str = json.dumps(output)
        deserialized = json.loads(json_str)

        assert deserialized["version"] == output["version"]
        assert deserialized["narrative_id"] == output["narrative_id"]


class TestBackwardsCompatibility:
    """Test backwards compatibility with legacy fields."""

    def test_legacy_field_access(self):
        """Test that legacy field access still works."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        # Legacy access should match new schema
        assert result.classification == output["primary_metrics"]["compliance_classification"]
        assert (
            result.component_scores["routine_engineering_penalty"]
            == output["component_scores"]["routine_engineering_penalty"]
        )
