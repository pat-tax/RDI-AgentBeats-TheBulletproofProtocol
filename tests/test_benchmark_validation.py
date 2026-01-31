"""Tests for benchmark validation with difficulty tier reporting (STORY-035).

This test module validates that validate_benchmark.py reports accuracy breakdown
by difficulty level, shows pass/fail counts per difficulty, and includes
difficulty distribution in output.

Acceptance criteria:
- Report accuracy breakdown by difficulty level (EASY, MEDIUM, HARD)
- Show pass/fail counts per difficulty
- Include difficulty distribution in output
"""

from pathlib import Path

from validate_benchmark import (
    BenchmarkReport,
    BenchmarkValidator,
    DifficultyTierResult,
    ValidationResult,
    load_ground_truth,
)

GROUND_TRUTH_PATH = Path(__file__).parent.parent / "data" / "ground_truth.json"


class TestDifficultyTierAccuracyReporting:
    """Test that validation script reports accuracy by difficulty tier."""

    def test_report_includes_tier_results(self) -> None:
        """Report includes tier_results field with per-difficulty breakdown."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        assert hasattr(report, "tier_results"), "Report must have tier_results field"
        assert isinstance(report.tier_results, list), "tier_results must be a list"
        assert len(report.tier_results) > 0, "tier_results must not be empty"

    def test_tier_results_cover_all_difficulty_levels(self) -> None:
        """Tier results include easy, medium, and hard difficulties."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)
        tier_names = {tier.tier for tier in report.tier_results}

        assert "easy" in tier_names, "Must report EASY tier"
        assert "medium" in tier_names, "Must report MEDIUM tier"
        assert "hard" in tier_names, "Must report HARD tier"

    def test_tier_result_shows_pass_fail_counts(self) -> None:
        """Each tier result shows total, passed, and failed counts."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        for tier in report.tier_results:
            assert hasattr(tier, "total"), f"{tier.tier} must have total count"
            assert hasattr(tier, "passed"), f"{tier.tier} must have passed count"
            assert hasattr(tier, "failed"), f"{tier.tier} must have failed count"
            assert tier.total > 0, f"{tier.tier} total must be positive"
            assert tier.passed + tier.failed == tier.total, (
                f"{tier.tier}: passed + failed must equal total"
            )

    def test_tier_result_includes_pass_rate(self) -> None:
        """Each tier result includes pass_rate (accuracy for that tier)."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        for tier in report.tier_results:
            assert hasattr(tier, "pass_rate"), f"{tier.tier} must have pass_rate"
            assert 0.0 <= tier.pass_rate <= 1.0, (
                f"{tier.tier} pass_rate must be between 0 and 1"
            )
            # Verify pass_rate calculation
            expected_rate = tier.passed / tier.total if tier.total > 0 else 0.0
            assert abs(tier.pass_rate - expected_rate) < 0.001, (
                f"{tier.tier} pass_rate calculation incorrect"
            )

    def test_summary_output_includes_difficulty_breakdown(self) -> None:
        """Report summary includes 'RESULTS BY DIFFICULTY TIER' section."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)
        summary = report.to_summary()

        assert "RESULTS BY DIFFICULTY TIER" in summary, (
            "Summary must include difficulty tier section"
        )

    def test_summary_displays_all_tiers(self) -> None:
        """Summary displays EASY, MEDIUM, and HARD tier results."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)
        summary = report.to_summary()

        # Summary should mention all tiers
        summary_upper = summary.upper()
        assert "EASY" in summary_upper, "Summary must show EASY tier"
        assert "MEDIUM" in summary_upper, "Summary must show MEDIUM tier"
        assert "HARD" in summary_upper, "Summary must show HARD tier"

    def test_summary_shows_pass_fail_format(self) -> None:
        """Summary shows pass/fail in 'Pass: X/Y' format."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)
        summary = report.to_summary()

        # Should show pass counts in format "Pass: X/Y (Z%)"
        assert "Pass:" in summary, "Summary must show pass counts"
        # Should show percentages
        assert "%" in summary, "Summary must show percentage pass rates"

    def test_difficulty_distribution_in_output(self) -> None:
        """Output includes difficulty distribution (count per tier)."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        # Verify tier_results contains distribution information
        total_entries = sum(tier.total for tier in report.tier_results)
        assert total_entries == len(data), (
            "Sum of tier totals must equal total entries"
        )

        # Each tier should have at least some entries
        for tier in report.tier_results:
            assert tier.total > 0, f"{tier.tier} tier should have entries"


class TestAccuracyByDifficultyLevel:
    """Test accuracy calculation per difficulty level."""

    def test_accuracy_calculated_per_tier(self) -> None:
        """Pass rate (accuracy) is calculated correctly for each tier."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        results = validator.validate_all(data)
        tier_results = validator.generate_tier_results(results)

        # Manually verify calculation for each tier
        from collections import defaultdict

        tier_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "passed": 0}
        )
        for result in results:
            tier = result.difficulty
            tier_stats[tier]["total"] += 1
            if result.classification_match:
                tier_stats[tier]["passed"] += 1

        # Verify validator calculations match manual calculations
        for tier_result in tier_results:
            expected_total = tier_stats[tier_result.tier]["total"]
            expected_passed = tier_stats[tier_result.tier]["passed"]
            expected_rate = expected_passed / expected_total if expected_total > 0 else 0.0

            assert tier_result.total == expected_total, (
                f"{tier_result.tier}: incorrect total count"
            )
            assert tier_result.passed == expected_passed, (
                f"{tier_result.tier}: incorrect passed count"
            )
            assert abs(tier_result.pass_rate - expected_rate) < 0.001, (
                f"{tier_result.tier}: incorrect pass rate calculation"
            )

    def test_tier_accuracy_varies_by_difficulty(self) -> None:
        """Different difficulty tiers may have different accuracy rates."""
        validator = BenchmarkValidator()
        data = load_ground_truth(GROUND_TRUTH_PATH)

        report = validator.generate_report(data)

        # Get pass rates by tier
        tier_rates = {tier.tier: tier.pass_rate for tier in report.tier_results}

        # Just verify we can measure different rates (they don't have to be different,
        # but we want to show we're tracking them separately)
        assert "easy" in tier_rates, "Must track easy tier accuracy"
        assert "medium" in tier_rates, "Must track medium tier accuracy"
        assert "hard" in tier_rates, "Must track hard tier accuracy"

        # All rates should be valid percentages
        for tier, rate in tier_rates.items():
            assert 0.0 <= rate <= 1.0, f"{tier} accuracy must be 0-100%"


class TestDifficultyTierResultModel:
    """Test DifficultyTierResult data model."""

    def test_difficulty_tier_result_has_required_fields(self) -> None:
        """DifficultyTierResult has tier, total, passed, failed, pass_rate."""
        tier_result = DifficultyTierResult(
            tier="easy",
            total=10,
            passed=8,
            failed=2,
            pass_rate=0.8,
        )

        assert tier_result.tier == "easy"
        assert tier_result.total == 10
        assert tier_result.passed == 8
        assert tier_result.failed == 2
        assert tier_result.pass_rate == 0.8

    def test_validation_result_preserves_difficulty(self) -> None:
        """ValidationResult includes and preserves difficulty field."""
        result = ValidationResult(
            entry_id="Q001",
            expected_score=15,
            actual_score=18,
            expected_classification="QUALIFYING",
            actual_classification="QUALIFYING",
            classification_match=True,
            score_delta=3,
            difficulty="hard",
        )

        assert result.difficulty == "hard", "Difficulty must be preserved"


class TestIntegrationWithGroundTruth:
    """Integration tests with actual ground truth data."""

    def test_full_pipeline_with_tier_reporting(self) -> None:
        """Full pipeline includes tier reporting: load -> validate -> report."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        validator = BenchmarkValidator()

        report = validator.generate_report(data)

        # Verify complete report structure
        assert isinstance(report, BenchmarkReport)
        assert len(report.validation_results) == len(data)
        assert len(report.tier_results) >= 3  # easy, medium, hard
        assert hasattr(report, "metrics")
        assert hasattr(report, "gaps")

        # Verify tier results are populated
        for tier in report.tier_results:
            assert tier.total > 0
            assert 0.0 <= tier.pass_rate <= 1.0

    def test_summary_output_is_human_readable(self) -> None:
        """Summary output is formatted for human readability."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        validator = BenchmarkValidator()

        report = validator.generate_report(data)
        summary = report.to_summary()

        # Should be multi-line with clear sections
        assert "\n" in summary, "Summary should be multi-line"
        assert "=" in summary, "Summary should have section dividers"
        assert "-" in summary, "Summary should have subsection dividers"

        # Should include key metrics and tier breakdown
        assert "OVERALL METRICS" in summary
        assert "RESULTS BY DIFFICULTY TIER" in summary

    def test_report_tier_results_sum_to_total(self) -> None:
        """Sum of all tier totals equals total validation results."""
        data = load_ground_truth(GROUND_TRUTH_PATH)
        validator = BenchmarkValidator()

        report = validator.generate_report(data)

        total_from_tiers = sum(tier.total for tier in report.tier_results)
        total_results = len(report.validation_results)

        assert total_from_tiers == total_results, (
            f"Tier totals ({total_from_tiers}) must equal "
            f"total results ({total_results})"
        )
