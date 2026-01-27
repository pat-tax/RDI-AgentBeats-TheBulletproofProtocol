"""Tests for STORY-020: Update output schema per specification.

This test module validates the acceptance criteria for STORY-020:
- Version and timestamp fields
- Narrative ID (UUID)
- Primary metrics object (compliance_classification, confidence, risk_score, risk_category, predicted_audit_outcome)
- Component scores object (routine_engineering_penalty, vagueness_penalty, business_risk_penalty, experimentation_penalty, specificity_penalty, total_penalty)
- Diagnostics object (routine_patterns_detected, vague_phrases_detected, business_keywords_detected, experimentation_evidence_score, specificity_score)
- Redline object with severity counts (total_issues, critical, high, medium, issues array)
- Metadata object (evaluation_time_ms, rules_version, irs_citations)
- JSON schema validation
- Backwards compatibility with legacy fields
"""

import json
import uuid
from datetime import datetime

from bulletproof_green.evaluator import RuleBasedEvaluator


class TestVersionAndTimestamp:
    """Test version and timestamp fields."""

    def test_has_version_field(self):
        """Test that output includes version field."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        # Convert to dict for schema validation
        output = result.to_dict()

        assert "version" in output
        assert output["version"] == "1.0"

    def test_has_timestamp_field(self):
        """Test that output includes timestamp field."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "timestamp" in output
        # Validate ISO 8601 format
        timestamp = datetime.fromisoformat(output["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)


class TestNarrativeID:
    """Test narrative ID (UUID) field."""

    def test_has_narrative_id(self):
        """Test that output includes narrative_id field."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "narrative_id" in output

    def test_narrative_id_is_valid_uuid(self):
        """Test that narrative_id is a valid UUID."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        # Should be parseable as UUID
        narrative_uuid = uuid.UUID(output["narrative_id"])
        assert isinstance(narrative_uuid, uuid.UUID)

    def test_different_evaluations_get_different_ids(self):
        """Test that each evaluation gets a unique narrative_id."""
        evaluator = RuleBasedEvaluator()

        result1 = evaluator.evaluate("Sample narrative 1.")
        result2 = evaluator.evaluate("Sample narrative 2.")

        output1 = result1.to_dict()
        output2 = result2.to_dict()

        assert output1["narrative_id"] != output2["narrative_id"]


class TestPrimaryMetrics:
    """Test primary_metrics object structure."""

    def test_has_primary_metrics_object(self):
        """Test that output includes primary_metrics object."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "primary_metrics" in output
        assert isinstance(output["primary_metrics"], dict)

    def test_primary_metrics_has_all_fields(self):
        """Test that primary_metrics contains all required fields."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        pm = output["primary_metrics"]

        assert "compliance_classification" in pm
        assert "confidence" in pm
        assert "risk_score" in pm
        assert "risk_category" in pm
        assert "predicted_audit_outcome" in pm

    def test_compliance_classification_values(self):
        """Test that compliance_classification has valid values."""
        evaluator = RuleBasedEvaluator()

        # Low risk narrative
        low_risk = evaluator.evaluate("""
        The project faced significant technical uncertainty. Experiments failed
        initially with 500ms latency. After iterations, achieved 45ms. Metrics:
        throughput 50,000 req/s, memory 1.2GB.
        """)

        # High risk narrative
        high_risk = evaluator.evaluate("Routine maintenance improved market share greatly.")

        low_output = low_risk.to_dict()
        high_output = high_risk.to_dict()

        assert low_output["primary_metrics"]["compliance_classification"] in ["QUALIFYING", "NON_QUALIFYING"]
        assert high_output["primary_metrics"]["compliance_classification"] in ["QUALIFYING", "NON_QUALIFYING"]

    def test_predicted_audit_outcome_field(self):
        """Test that predicted_audit_outcome is included."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        pm = output["primary_metrics"]

        assert "predicted_audit_outcome" in pm
        assert pm["predicted_audit_outcome"] in ["PASS_AUDIT", "FAIL_AUDIT"]


class TestComponentScoresObject:
    """Test component_scores object structure."""

    def test_has_component_scores_object(self):
        """Test that output includes component_scores object."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "component_scores" in output
        assert isinstance(output["component_scores"], dict)

    def test_component_scores_has_all_fields(self):
        """Test that component_scores contains all required fields."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        cs = output["component_scores"]

        assert "routine_engineering_penalty" in cs
        assert "vagueness_penalty" in cs
        assert "business_risk_penalty" in cs
        assert "experimentation_penalty" in cs
        assert "specificity_penalty" in cs
        assert "total_penalty" in cs

    def test_total_penalty_equals_sum(self):
        """Test that total_penalty equals sum of individual penalties."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Routine maintenance with vague improvements for market share.")

        output = result.to_dict()
        cs = output["component_scores"]

        expected_total = (
            cs["routine_engineering_penalty"] +
            cs["vagueness_penalty"] +
            cs["business_risk_penalty"] +
            cs["experimentation_penalty"] +
            cs["specificity_penalty"]
        )

        assert cs["total_penalty"] == expected_total


class TestDiagnosticsObject:
    """Test diagnostics object structure."""

    def test_has_diagnostics_object(self):
        """Test that output includes diagnostics object."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "diagnostics" in output
        assert isinstance(output["diagnostics"], dict)

    def test_diagnostics_has_all_fields(self):
        """Test that diagnostics contains all required fields."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        diag = output["diagnostics"]

        assert "routine_patterns_detected" in diag
        assert "vague_phrases_detected" in diag
        assert "business_keywords_detected" in diag
        assert "experimentation_evidence_score" in diag
        assert "specificity_score" in diag

    def test_diagnostics_values_are_numeric(self):
        """Test that diagnostic values are numeric."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative with routine maintenance and vague claims.")

        output = result.to_dict()
        diag = output["diagnostics"]

        assert isinstance(diag["routine_patterns_detected"], int)
        assert isinstance(diag["vague_phrases_detected"], int)
        assert isinstance(diag["business_keywords_detected"], int)
        assert isinstance(diag["experimentation_evidence_score"], float)
        assert isinstance(diag["specificity_score"], float)

    def test_experimentation_evidence_score_range(self):
        """Test that experimentation_evidence_score is between 0 and 1."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Experiments failed, hypotheses tested, iterations completed.")

        output = result.to_dict()
        diag = output["diagnostics"]

        assert 0.0 <= diag["experimentation_evidence_score"] <= 1.0

    def test_specificity_score_range(self):
        """Test that specificity_score is between 0 and 1."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Response time improved from 250ms to 45ms.")

        output = result.to_dict()
        diag = output["diagnostics"]

        assert 0.0 <= diag["specificity_score"] <= 1.0


class TestRedlineObject:
    """Test redline object with severity counts."""

    def test_has_redline_object(self):
        """Test that output includes redline object."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "redline" in output
        assert isinstance(output["redline"], dict)

    def test_redline_has_severity_counts(self):
        """Test that redline includes severity count fields."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        redline = output["redline"]

        assert "total_issues" in redline
        assert "critical" in redline
        assert "high" in redline
        assert "medium" in redline
        assert "issues" in redline

    def test_redline_severity_counts_match_issues(self):
        """Test that severity counts match the issues array."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Routine maintenance with vague improvements for market share.")

        output = result.to_dict()
        redline = output["redline"]

        # Count severities from issues array
        critical_count = sum(1 for issue in redline["issues"] if issue["severity"] == "critical")
        high_count = sum(1 for issue in redline["issues"] if issue["severity"] == "high")
        medium_count = sum(1 for issue in redline["issues"] if issue["severity"] == "medium")

        assert redline["critical"] == critical_count
        assert redline["high"] == high_count
        assert redline["medium"] == medium_count
        assert redline["total_issues"] == len(redline["issues"])

    def test_issues_array_structure(self):
        """Test that issues array contains properly structured issues."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Routine maintenance performed.")

        output = result.to_dict()
        redline = output["redline"]

        if len(redline["issues"]) > 0:
            issue = redline["issues"][0]
            assert "category" in issue
            assert "severity" in issue
            assert "text" in issue
            assert "suggestion" in issue


class TestMetadataObject:
    """Test metadata object structure."""

    def test_has_metadata_object(self):
        """Test that output includes metadata object."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        assert "metadata" in output
        assert isinstance(output["metadata"], dict)

    def test_metadata_has_all_fields(self):
        """Test that metadata contains all required fields."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        meta = output["metadata"]

        assert "evaluation_time_ms" in meta
        assert "rules_version" in meta
        assert "irs_citations" in meta

    def test_evaluation_time_is_numeric(self):
        """Test that evaluation_time_ms is a number."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        meta = output["metadata"]

        assert isinstance(meta["evaluation_time_ms"], (int, float))
        assert meta["evaluation_time_ms"] > 0

    def test_rules_version_format(self):
        """Test that rules_version is a valid version string."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        meta = output["metadata"]

        assert isinstance(meta["rules_version"], str)
        assert len(meta["rules_version"]) > 0

    def test_irs_citations_is_array(self):
        """Test that irs_citations is an array."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        meta = output["metadata"]

        assert isinstance(meta["irs_citations"], list)
        # Should have at least one citation
        assert len(meta["irs_citations"]) > 0


class TestJSONSchemaValidation:
    """Test JSON schema validation."""

    def test_output_is_json_serializable(self):
        """Test that the output can be serialized to JSON."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        # Should not raise exception
        json_str = json.dumps(output)
        assert isinstance(json_str, str)
        assert len(json_str) > 0

    def test_output_can_be_deserialized(self):
        """Test that the JSON output can be deserialized."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()
        json_str = json.dumps(output)

        # Should not raise exception
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)
        assert "version" in deserialized


class TestBackwardsCompatibility:
    """Test backwards compatibility with legacy fields."""

    def test_legacy_fields_still_accessible(self):
        """Test that legacy field access still works."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        # Legacy field access should still work
        assert hasattr(result, "classification")
        assert hasattr(result, "confidence")
        assert hasattr(result, "risk_score")
        assert hasattr(result, "risk_category")
        assert hasattr(result, "component_scores")
        assert hasattr(result, "redline")

    def test_classification_maps_to_compliance_classification(self):
        """Test that classification field maps correctly."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        # Legacy field should match new field
        assert result.classification == output["primary_metrics"]["compliance_classification"]

    def test_component_scores_accessible_both_ways(self):
        """Test that component_scores are accessible in both formats."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("Sample narrative.")

        output = result.to_dict()

        # Legacy access
        assert "routine_engineering_penalty" in result.component_scores

        # New schema access
        assert "routine_engineering_penalty" in output["component_scores"]

        # Values should match
        assert result.component_scores["routine_engineering_penalty"] == \
               output["component_scores"]["routine_engineering_penalty"]


class TestCompleteSchemaExample:
    """Test complete schema matches specification example."""

    def test_complete_output_structure(self):
        """Test that a complete evaluation produces the expected structure."""
        evaluator = RuleBasedEvaluator()
        result = evaluator.evaluate("""
        The team performed routine maintenance to improve market share.
        We made significant improvements with better performance.
        The initiative was very successful.
        """)

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

        # Validate complete structure can be serialized
        json_str = json.dumps(output, indent=2)
        assert len(json_str) > 0
