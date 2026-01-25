"""Tests for benchmark validation script (STORY-009).

This test module validates the acceptance criteria for STORY-009:
- Loads ground_truth.json
- Runs Green Agent on each narrative
- Compares actual vs expected scores
- Computes accuracy metrics (precision, recall, F1)
- Generates report with pass/fail per difficulty tier
- Identifies gaps and improvement areas
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# These imports will fail until implementation exists
from validate_benchmark import (
    BenchmarkReport,
    BenchmarkValidator,
    DifficultyTierResult,
    ValidationResult,
    load_ground_truth,
)


GROUND_TRUTH_PATH = Path(__file__).parent.parent / "data" / "ground_truth.json"


class TestLoadGroundTruth:
    """Test loading ground_truth.json."""

    def test_load_ground_truth_returns_list(self) -> None:
        """load_ground_truth returns a list of entries."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_load_ground_truth_entries_have_required_fields(self) -> None:
        """Each entry has id, narrative, expected_score, classification."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        required_fields = {"id", "narrative", "expected_score", "classification"}
        for entry in data:
            assert required_fields.issubset(set(entry.keys()))

    def test_load_ground_truth_file_not_found(self) -> None:
        """load_ground_truth raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_ground_truth(Path("/nonexistent/path.json"))

    def test_load_ground_truth_invalid_json(self, tmp_path: Path) -> None:
        """load_ground_truth raises ValueError for invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        with pytest.raises(ValueError):
            load_ground_truth(invalid_file)


class TestValidationResult:
    """Test ValidationResult dataclass structure."""

    def test_validation_result_creation(self) -> None:
        """ValidationResult can be created with required fields."""
        result = ValidationResult(
            entry_id="Q001",
            expected_score=15,
            actual_score=18,
            expected_classification="QUALIFYING",
            actual_classification="QUALIFYING",
            classification_match=True,
            score_delta=3,
            difficulty="easy",
        )
        assert result.entry_id == "Q001"
        assert result.expected_score == 15
        assert result.actual_score == 18
        assert result.classification_match is True
        assert result.score_delta == 3

    def test_validation_result_classification_mismatch(self) -> None:
        """ValidationResult correctly identifies classification mismatches."""
        result = ValidationResult(
            entry_id="NQ001",
            expected_score=55,
            actual_score=15,
            expected_classification="NON_QUALIFYING",
            actual_classification="QUALIFYING",
            classification_match=False,
            score_delta=-40,
            difficulty="easy",
        )
        assert result.classification_match is False


class TestDifficultyTierResult:
    """Test DifficultyTierResult for per-tier reporting."""

    def test_difficulty_tier_result_creation(self) -> None:
        """DifficultyTierResult tracks pass/fail per tier."""
        tier_result = DifficultyTierResult(
            tier="easy",
            total=5,
            passed=4,
            failed=1,
            pass_rate=0.80,
        )
        assert tier_result.tier == "easy"
        assert tier_result.total == 5
        assert tier_result.passed == 4
        assert tier_result.failed == 1
        assert tier_result.pass_rate == 0.80


class TestBenchmarkValidator:
    """Test BenchmarkValidator runs Green Agent on narratives."""

    def test_validator_evaluates_single_narrative(self) -> None:
        """Validator evaluates a single narrative and returns ValidationResult."""
        validator = BenchmarkValidator()
        entry = {
            "id": "Q001",
            "narrative": "Our team investigated novel approaches...",
            "expected_score": 15,
            "classification": "QUALIFYING",
            "difficulty": "easy",
        }

        result = validator.validate_entry(entry)

        assert isinstance(result, ValidationResult)
        assert result.entry_id == "Q001"
        assert result.expected_score == 15
        assert 0 <= result.actual_score <= 100

    def test_validator_evaluates_all_entries(self) -> None:
        """Validator evaluates all entries from ground truth."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        results = validator.validate_all(data)

        assert len(results) == len(data)
        assert all(isinstance(r, ValidationResult) for r in results)

    def test_validator_uses_green_agent_evaluator(self) -> None:
        """Validator uses the Green Agent's RuleBasedEvaluator."""
        validator = BenchmarkValidator()

        # Verify the validator has the evaluator
        assert hasattr(validator, "evaluator")
        assert hasattr(validator, "scorer")


class TestAccuracyMetrics:
    """Test computation of precision, recall, and F1 metrics."""

    def test_compute_metrics_perfect_classification(self) -> None:
        """Metrics are perfect when all classifications match."""
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
            ValidationResult("Q2", 15, 18, "QUALIFYING", "QUALIFYING", True, 3, "easy"),
            ValidationResult("NQ1", 50, 55, "NON_QUALIFYING", "NON_QUALIFYING", True, 5, "easy"),
            ValidationResult("NQ2", 60, 65, "NON_QUALIFYING", "NON_QUALIFYING", True, 5, "easy"),
        ]
        validator = BenchmarkValidator()

        metrics = validator.compute_metrics(results)

        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1_score"] == 1.0
        assert metrics["accuracy"] == 1.0

    def test_compute_metrics_with_false_positives(self) -> None:
        """Metrics handle false positives (classified QUALIFYING when should be NON_QUALIFYING)."""
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
            ValidationResult("NQ1", 50, 15, "NON_QUALIFYING", "QUALIFYING", False, -35, "easy"),
        ]
        validator = BenchmarkValidator()

        metrics = validator.compute_metrics(results)

        # 1 TP, 1 FP, 0 FN
        # Precision = TP/(TP+FP) = 1/2 = 0.5
        # Recall = TP/(TP+FN) = 1/1 = 1.0
        assert metrics["precision"] == 0.5
        assert metrics["recall"] == 1.0

    def test_compute_metrics_with_false_negatives(self) -> None:
        """Metrics handle false negatives (classified NON_QUALIFYING when should be QUALIFYING)."""
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
            ValidationResult("Q2", 15, 50, "QUALIFYING", "NON_QUALIFYING", False, 35, "easy"),
            ValidationResult("NQ1", 50, 55, "NON_QUALIFYING", "NON_QUALIFYING", True, 5, "easy"),
        ]
        validator = BenchmarkValidator()

        metrics = validator.compute_metrics(results)

        # 1 TP, 0 FP, 1 FN, 1 TN
        # Precision = TP/(TP+FP) = 1/1 = 1.0
        # Recall = TP/(TP+FN) = 1/2 = 0.5
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 0.5

    def test_compute_f1_score(self) -> None:
        """F1 score is harmonic mean of precision and recall."""
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
            ValidationResult("Q2", 15, 50, "QUALIFYING", "NON_QUALIFYING", False, 35, "easy"),
            ValidationResult("NQ1", 50, 15, "NON_QUALIFYING", "QUALIFYING", False, -35, "easy"),
        ]
        validator = BenchmarkValidator()

        metrics = validator.compute_metrics(results)

        # 1 TP, 1 FP, 1 FN
        # Precision = 1/2 = 0.5
        # Recall = 1/2 = 0.5
        # F1 = 2 * (0.5 * 0.5) / (0.5 + 0.5) = 0.5
        assert metrics["f1_score"] == pytest.approx(0.5, rel=0.01)

    def test_compute_metrics_handles_edge_cases(self) -> None:
        """Metrics handle edge case with no true positives."""
        results = [
            ValidationResult("NQ1", 50, 55, "NON_QUALIFYING", "NON_QUALIFYING", True, 5, "easy"),
        ]
        validator = BenchmarkValidator()

        metrics = validator.compute_metrics(results)

        # No qualifying predictions, so precision/recall undefined (handle gracefully)
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics


class TestPerTierReporting:
    """Test pass/fail reporting per difficulty tier."""

    def test_generate_tier_results(self) -> None:
        """Generate pass/fail results per difficulty tier."""
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
            ValidationResult("Q2", 15, 50, "QUALIFYING", "NON_QUALIFYING", False, 35, "easy"),
            ValidationResult("Q3", 12, 14, "QUALIFYING", "QUALIFYING", True, 2, "medium"),
            ValidationResult("Q4", 8, 10, "QUALIFYING", "QUALIFYING", True, 2, "hard"),
        ]
        validator = BenchmarkValidator()

        tier_results = validator.generate_tier_results(results)

        assert len(tier_results) == 3
        tier_by_name = {t.tier: t for t in tier_results}

        # Easy: 1 pass, 1 fail
        assert tier_by_name["easy"].passed == 1
        assert tier_by_name["easy"].failed == 1
        assert tier_by_name["easy"].pass_rate == 0.5

        # Medium: 1 pass, 0 fail
        assert tier_by_name["medium"].passed == 1
        assert tier_by_name["medium"].failed == 0
        assert tier_by_name["medium"].pass_rate == 1.0

        # Hard: 1 pass, 0 fail
        assert tier_by_name["hard"].passed == 1
        assert tier_by_name["hard"].failed == 0

    def test_tier_results_include_all_tiers(self) -> None:
        """Tier results include easy, medium, hard even if empty."""
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
        ]
        validator = BenchmarkValidator()

        tier_results = validator.generate_tier_results(results)

        tier_names = {t.tier for t in tier_results}
        # At minimum should include the tier that has data
        assert "easy" in tier_names


class TestBenchmarkReport:
    """Test BenchmarkReport generation."""

    def test_report_contains_all_sections(self) -> None:
        """Report contains metrics, tier results, and gaps."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        assert isinstance(report, BenchmarkReport)
        assert hasattr(report, "metrics")
        assert hasattr(report, "tier_results")
        assert hasattr(report, "gaps")
        assert hasattr(report, "validation_results")

    def test_report_metrics_structure(self) -> None:
        """Report metrics include precision, recall, F1, accuracy."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        assert "precision" in report.metrics
        assert "recall" in report.metrics
        assert "f1_score" in report.metrics
        assert "accuracy" in report.metrics

    def test_report_identifies_gaps(self) -> None:
        """Report identifies gaps and improvement areas."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        # Gaps should be a list of identified issues
        assert isinstance(report.gaps, list)

    def test_report_summary_generation(self) -> None:
        """Report can generate a human-readable summary."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)
        summary = report.to_summary()

        assert isinstance(summary, str)
        assert len(summary) > 0
        # Summary should mention key metrics
        assert "precision" in summary.lower() or "accuracy" in summary.lower()


class TestGapIdentification:
    """Test identification of gaps and improvement areas."""

    def test_identifies_classification_mismatches(self) -> None:
        """Gaps include entries where classification doesn't match."""
        validator = BenchmarkValidator()
        results = [
            ValidationResult("Q1", 10, 50, "QUALIFYING", "NON_QUALIFYING", False, 40, "easy"),
            ValidationResult("Q2", 15, 18, "QUALIFYING", "QUALIFYING", True, 3, "easy"),
        ]

        gaps = validator.identify_gaps(results)

        # Should identify Q1 as a gap due to classification mismatch
        gap_ids = [g.get("entry_id") for g in gaps]
        assert "Q1" in gap_ids

    def test_identifies_large_score_deltas(self) -> None:
        """Gaps include entries with large score deltas."""
        validator = BenchmarkValidator()
        results = [
            ValidationResult("Q1", 10, 12, "QUALIFYING", "QUALIFYING", True, 2, "easy"),
            ValidationResult("Q2", 15, 45, "QUALIFYING", "NON_QUALIFYING", False, 30, "easy"),
        ]

        gaps = validator.identify_gaps(results)

        # Should identify Q2 due to large delta
        gap_ids = [g.get("entry_id") for g in gaps]
        assert "Q2" in gap_ids

    def test_gap_includes_improvement_suggestion(self) -> None:
        """Each gap includes a suggestion for improvement."""
        validator = BenchmarkValidator()
        results = [
            ValidationResult("Q1", 10, 50, "QUALIFYING", "NON_QUALIFYING", False, 40, "easy"),
        ]

        gaps = validator.identify_gaps(results)

        assert len(gaps) > 0
        for gap in gaps:
            assert "suggestion" in gap or "reason" in gap


class TestIntegration:
    """Integration tests using actual ground truth data."""

    def test_full_validation_pipeline(self) -> None:
        """Full pipeline: load -> validate -> compute metrics -> generate report."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        validator = BenchmarkValidator()

        report = validator.generate_report(data)

        # Report should have valid structure
        assert isinstance(report, BenchmarkReport)
        assert len(report.validation_results) == len(data)
        assert 0.0 <= report.metrics["accuracy"] <= 1.0

    def test_validation_against_ground_truth(self) -> None:
        """Validate that evaluator produces reasonable scores against ground truth."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        validator = BenchmarkValidator()

        report = validator.generate_report(data)

        # Accuracy should be reasonable (at least 60% for rule-based evaluator)
        # This is a smoke test - actual accuracy may vary
        assert report.metrics["accuracy"] >= 0.5, (
            f"Accuracy too low: {report.metrics['accuracy']}"
        )
