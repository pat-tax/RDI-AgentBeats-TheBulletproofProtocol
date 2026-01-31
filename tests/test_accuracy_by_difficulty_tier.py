"""Tests for per-tier accuracy reporting (STORY-030).

Validates that the benchmark validation script reports accuracy metrics
broken down by difficulty tier (EASY, MEDIUM, HARD) and that tiers are
evenly distributed.
"""

import json
from collections import Counter
from pathlib import Path

import pytest

from src.validate_benchmark import BenchmarkValidator, load_ground_truth


class TestDifficultyTierReporting:
    """Test that validation script reports accuracy by difficulty tier."""

    @pytest.fixture
    def ground_truth_data(self) -> list[dict]:
        """Load ground truth dataset."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        return load_ground_truth(ground_truth_path)

    @pytest.fixture
    def validator(self) -> BenchmarkValidator:
        """Create benchmark validator instance."""
        return BenchmarkValidator()

    def test_difficulty_tags_exist_in_ground_truth(self, ground_truth_data: list[dict]):
        """Verify all entries have difficulty tags (EASY, MEDIUM, HARD)."""
        valid_difficulties = {"easy", "medium", "hard", "EASY", "MEDIUM", "HARD"}

        for entry in ground_truth_data:
            assert "difficulty" in entry, f"Entry {entry.get('id')} missing difficulty tag"
            difficulty = entry["difficulty"]
            assert difficulty in valid_difficulties, (
                f"Entry {entry.get('id')} has invalid difficulty: {difficulty}"
            )

    def test_difficulty_distribution_is_even(self, ground_truth_data: list[dict]):
        """Verify difficulty tiers are evenly distributed."""
        difficulty_counts = Counter(
            entry.get("difficulty", "unknown").lower() for entry in ground_truth_data
        )

        # Check all three tiers exist
        assert "easy" in difficulty_counts, "Ground truth must have EASY entries"
        assert "medium" in difficulty_counts, "Ground truth must have MEDIUM entries"
        assert "hard" in difficulty_counts, "Ground truth must have HARD entries"

        # Check even distribution (each tier at least 20% of total)
        total = len(ground_truth_data)
        for difficulty, count in difficulty_counts.items():
            if difficulty in {"easy", "medium", "hard"}:
                proportion = count / total if total > 0 else 0
                assert proportion >= 0.2, (
                    f"{difficulty.upper()} tier has {count}/{total} ({proportion:.1%}), "
                    f"should be at least 20%"
                )

    def test_validator_generates_tier_results(
        self, validator: BenchmarkValidator, ground_truth_data: list[dict]
    ):
        """Verify validator generates per-tier results."""
        results = validator.validate_all(ground_truth_data)
        tier_results = validator.generate_tier_results(results)

        # Should have results for all three tiers
        tiers = {tr.tier for tr in tier_results}
        assert "easy" in tiers, "Tier results must include EASY tier"
        assert "medium" in tiers, "Tier results must include MEDIUM tier"
        assert "hard" in tiers, "Tier results must include HARD tier"

        # Each tier result should have meaningful data
        for tier_result in tier_results:
            assert tier_result.total > 0, f"{tier_result.tier} tier has no entries"
            assert tier_result.passed + tier_result.failed == tier_result.total, (
                f"{tier_result.tier} tier: passed + failed != total"
            )
            assert 0 <= tier_result.pass_rate <= 1.0, (
                f"{tier_result.tier} tier: pass_rate must be between 0 and 1"
            )

    def test_report_summary_includes_tier_breakdown(
        self, validator: BenchmarkValidator, ground_truth_data: list[dict]
    ):
        """Verify report summary includes difficulty tier breakdown."""
        report = validator.generate_report(ground_truth_data)
        summary = report.to_summary()

        # Summary should contain tier section header
        assert "RESULTS BY DIFFICULTY TIER" in summary, (
            "Report must include difficulty tier section"
        )

        # Should list all three tiers with pass/fail counts
        assert "EASY" in summary, "Report must show EASY tier results"
        assert "MEDIUM" in summary, "Report must show MEDIUM tier results"
        assert "HARD" in summary, "Report must show HARD tier results"

        # Should show pass counts in format "Pass: X/Y"
        assert "Pass:" in summary, "Report must show pass counts"

    def test_per_tier_accuracy_calculation(
        self, validator: BenchmarkValidator, ground_truth_data: list[dict]
    ):
        """Verify per-tier accuracy is calculated correctly."""
        results = validator.validate_all(ground_truth_data)
        tier_results = validator.generate_tier_results(results)

        # Manually compute expected pass rate for each tier
        from collections import defaultdict

        tier_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0})
        for result in results:
            tier = result.difficulty
            tier_stats[tier]["total"] += 1
            if result.classification_match:
                tier_stats[tier]["passed"] += 1

        # Verify validator's calculations match our manual calculations
        for tier_result in tier_results:
            expected_total = tier_stats[tier_result.tier]["total"]
            expected_passed = tier_stats[tier_result.tier]["passed"]
            expected_pass_rate = expected_passed / expected_total if expected_total > 0 else 0.0

            assert tier_result.total == expected_total, (
                f"{tier_result.tier}: total mismatch"
            )
            assert tier_result.passed == expected_passed, (
                f"{tier_result.tier}: passed count mismatch"
            )
            assert abs(tier_result.pass_rate - expected_pass_rate) < 0.001, (
                f"{tier_result.tier}: pass_rate mismatch"
            )

    def test_cli_output_displays_tier_breakdown(
        self, validator: BenchmarkValidator, ground_truth_data: list[dict]
    ):
        """Verify CLI output (reporting dashboard) displays tier breakdown."""
        report = validator.generate_report(ground_truth_data)

        # Should have tier_results in the report
        assert len(report.tier_results) >= 3, "Report must have at least 3 tier results"

        # Verify tier_results are structured correctly for CLI display
        for tier_result in report.tier_results:
            assert hasattr(tier_result, "tier"), "Tier result must have tier name"
            assert hasattr(tier_result, "total"), "Tier result must have total count"
            assert hasattr(tier_result, "passed"), "Tier result must have passed count"
            assert hasattr(tier_result, "failed"), "Tier result must have failed count"
            assert hasattr(tier_result, "pass_rate"), "Tier result must have pass rate"

            # Verify data types
            assert isinstance(tier_result.tier, str), "tier must be string"
            assert isinstance(tier_result.total, int), "total must be int"
            assert isinstance(tier_result.passed, int), "passed must be int"
            assert isinstance(tier_result.failed, int), "failed must be int"
            assert isinstance(tier_result.pass_rate, float), "pass_rate must be float"


class TestJSONSchemaForDifficulty:
    """Test that JSON schema includes difficulty field."""

    def test_ground_truth_entry_model_has_difficulty(self):
        """Verify GroundTruthEntry model includes difficulty field."""
        from src.validate_benchmark import GroundTruthEntry

        # Check model fields
        model_fields = GroundTruthEntry.model_fields
        assert "difficulty" in model_fields, "GroundTruthEntry must have difficulty field"

        # Test instantiation with difficulty
        entry = GroundTruthEntry(
            id="TEST-001",
            narrative="Test narrative",
            expected_score=50,
            classification="NON_QUALIFYING",
            difficulty="medium",
        )
        assert entry.difficulty == "medium", "Difficulty field must be accessible"

    def test_validation_result_includes_difficulty(self):
        """Verify ValidationResult model includes difficulty field."""
        from src.validate_benchmark import ValidationResult

        # Check model fields
        model_fields = ValidationResult.model_fields
        assert "difficulty" in model_fields, "ValidationResult must have difficulty field"

        # Test instantiation
        result = ValidationResult(
            entry_id="TEST-001",
            expected_score=50,
            actual_score=55,
            expected_classification="QUALIFYING",
            actual_classification="QUALIFYING",
            classification_match=True,
            score_delta=5,
            difficulty="hard",
        )
        assert result.difficulty == "hard", "Difficulty must be preserved in results"

    def test_difficulty_tier_result_model_exists(self):
        """Verify DifficultyTierResult model exists and is structured correctly."""
        from src.validate_benchmark import DifficultyTierResult

        # Test model instantiation
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
