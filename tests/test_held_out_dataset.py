"""Tests for held-out test set (STORY-027).

This test module validates:
- Held-out test set exists and is separate from training data
- Dataset structure and metadata
- Data provenance tracking
"""

import json
from pathlib import Path


class TestHeldOutDataset:
    """Test held-out test set structure and isolation."""

    def test_held_out_dataset_exists(self):
        """Test that held-out test set file exists."""
        held_out_path = Path("data/held_out_test_set.json")
        assert held_out_path.exists(), "Held-out test set should exist at data/held_out_test_set.json"

    def test_held_out_dataset_structure(self):
        """Test that held-out dataset has valid structure."""
        held_out_path = Path("data/held_out_test_set.json")

        with held_out_path.open() as f:
            data = json.load(f)

        # Should have metadata and test cases
        assert "metadata" in data
        assert "test_cases" in data

        # Metadata should track provenance
        metadata = data["metadata"]
        assert "version" in metadata
        assert "created_at" in metadata
        assert "description" in metadata
        assert "contamination_check" in metadata

    def test_held_out_has_minimum_test_cases(self):
        """Test that held-out set has sufficient test cases."""
        held_out_path = Path("data/held_out_test_set.json")

        with held_out_path.open() as f:
            data = json.load(f)

        test_cases = data["test_cases"]

        # Should have at least 10 test cases for statistical validity
        assert len(test_cases) >= 10, f"Need ≥10 test cases, got {len(test_cases)}"

    def test_held_out_cases_have_required_fields(self):
        """Test that each test case has required fields."""
        held_out_path = Path("data/held_out_test_set.json")

        with held_out_path.open() as f:
            data = json.load(f)

        test_cases = data["test_cases"]

        for i, case in enumerate(test_cases):
            assert "id" in case, f"Test case {i} missing 'id'"
            assert "narrative" in case, f"Test case {i} missing 'narrative'"
            assert "expected_classification" in case, f"Test case {i} missing 'expected_classification'"
            assert "expected_risk_range" in case, f"Test case {i} missing 'expected_risk_range'"
            assert "difficulty" in case, f"Test case {i} missing 'difficulty'"
            assert "source" in case, f"Test case {i} missing 'source' (provenance)"

    def test_held_out_not_in_ground_truth(self):
        """Test that held-out cases are not in public ground truth."""
        held_out_path = Path("data/held_out_test_set.json")
        ground_truth_path = Path("data/ground_truth.json")

        with held_out_path.open() as f:
            held_out = json.load(f)

        with ground_truth_path.open() as f:
            ground_truth = json.load(f)

        held_out_narratives = {case["narrative"] for case in held_out["test_cases"]}
        ground_truth_narratives = {case["narrative"] for case in ground_truth}

        # No overlap between held-out and ground truth (prevent contamination)
        overlap = held_out_narratives & ground_truth_narratives
        assert len(overlap) == 0, f"Found {len(overlap)} contaminated cases in held-out set"

    def test_held_out_difficulty_distribution(self):
        """Test that held-out set has diverse difficulty levels."""
        held_out_path = Path("data/held_out_test_set.json")

        with held_out_path.open() as f:
            data = json.load(f)

        test_cases = data["test_cases"]
        difficulties = [case["difficulty"] for case in test_cases]

        # Should have representation across difficulty tiers
        unique_difficulties = set(difficulties)
        expected_difficulties = {"EASY", "MEDIUM", "HARD"}

        assert unique_difficulties == expected_difficulties, (
            f"Held-out set should span all difficulties, got {unique_difficulties}"
        )
