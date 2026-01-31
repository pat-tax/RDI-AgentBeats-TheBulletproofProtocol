"""Tests for data contamination prevention (STORY-029).

Tests held-out test set, version tracking, and data provenance.
"""

import json
from pathlib import Path

import pytest


class TestHeldOutTestSet:
    """Tests for held-out test set that's not in public ground truth."""

    def test_held_out_test_set_exists(self):
        """Held-out test set file should exist separately from ground truth."""
        held_out_path = Path(__file__).parent.parent / "data" / "held_out_test_set.json"
        assert held_out_path.exists(), "Held-out test set file must exist"

    def test_held_out_test_set_valid_json(self):
        """Held-out test set should be valid JSON with metadata and test_cases."""
        held_out_path = Path(__file__).parent.parent / "data" / "held_out_test_set.json"
        with open(held_out_path) as f:
            data = json.load(f)
        assert isinstance(data, dict), "Held-out test set must be a dict"
        assert "metadata" in data, "Held-out test set must have metadata"
        assert "test_cases" in data, "Held-out test set must have test_cases"

    def test_held_out_test_set_has_entries(self):
        """Held-out test set should contain at least 5 entries."""
        held_out_path = Path(__file__).parent.parent / "data" / "held_out_test_set.json"
        with open(held_out_path) as f:
            data = json.load(f)
        test_cases = data["test_cases"]
        assert len(test_cases) >= 5, "Held-out test set must have at least 5 entries"

    def test_held_out_narratives_not_in_ground_truth(self):
        """Narratives in held-out set must not appear in public ground truth."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        held_out_path = Path(__file__).parent.parent / "data" / "held_out_test_set.json"

        with open(ground_truth_path) as f:
            ground_truth = json.load(f)
        with open(held_out_path) as f:
            held_out_data = json.load(f)

        ground_truth_ids = {entry["id"] for entry in ground_truth}
        held_out_ids = {entry["id"] for entry in held_out_data["test_cases"]}

        overlap = ground_truth_ids & held_out_ids
        assert len(overlap) == 0, f"IDs must not overlap between sets: {overlap}"

    def test_held_out_entries_have_difficulty_tags(self):
        """Each held-out entry should have a difficulty tag."""
        held_out_path = Path(__file__).parent.parent / "data" / "held_out_test_set.json"
        with open(held_out_path) as f:
            data = json.load(f)

        valid_difficulties = {"easy", "medium", "hard", "EASY", "MEDIUM", "HARD"}
        for entry in data["test_cases"]:
            assert "difficulty" in entry, f"Entry {entry.get('id')} missing difficulty"
            assert entry["difficulty"] in valid_difficulties, (
                f"Entry {entry.get('id')} has invalid difficulty: {entry.get('difficulty')}"
            )


class TestVersionTracking:
    """Tests for narrative version tracking."""

    def test_ground_truth_has_version_field(self):
        """Each entry in ground truth should have a version field."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        with open(ground_truth_path) as f:
            data = json.load(f)

        for entry in data:
            assert "version" in entry, f"Entry {entry.get('id')} missing version field"
            assert isinstance(entry["version"], str), (
                f"Entry {entry.get('id')} version must be string"
            )

    def test_held_out_has_version_field(self):
        """Each entry in held-out set should have a version field."""
        held_out_path = Path(__file__).parent.parent / "data" / "held_out_test_set.json"
        with open(held_out_path) as f:
            data = json.load(f)

        for entry in data["test_cases"]:
            assert "version" in entry, f"Entry {entry.get('id')} missing version field"
            assert isinstance(entry["version"], str), (
                f"Entry {entry.get('id')} version must be string"
            )

    def test_version_format_is_semver(self):
        """Version field should follow semantic versioning format (e.g., '1.0.0')."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        with open(ground_truth_path) as f:
            data = json.load(f)

        import re

        semver_pattern = re.compile(r"^\d+\.\d+\.\d+$")
        for entry in data:
            version = entry.get("version", "")
            assert semver_pattern.match(version), (
                f"Entry {entry.get('id')} version '{version}' is not valid semver"
            )

    def test_ground_truth_has_created_at_field(self):
        """Each entry should have a created_at timestamp."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        with open(ground_truth_path) as f:
            data = json.load(f)

        for entry in data:
            assert "created_at" in entry, f"Entry {entry.get('id')} missing created_at"
            assert isinstance(entry["created_at"], str), (
                f"Entry {entry.get('id')} created_at must be string"
            )


class TestDataProvenance:
    """Tests for data provenance documentation."""

    def test_provenance_file_exists(self):
        """Data provenance documentation file should exist."""
        provenance_path = Path(__file__).parent.parent / "data" / "DATA_PROVENANCE.md"
        assert provenance_path.exists(), "DATA_PROVENANCE.md must exist"

    def test_provenance_documents_source(self):
        """Provenance file should document data sources."""
        provenance_path = Path(__file__).parent.parent / "data" / "DATA_PROVENANCE.md"
        with open(provenance_path) as f:
            content = f.read()

        # Check for key sections
        assert "# Data Provenance" in content or "## Data Provenance" in content
        assert "source" in content.lower(), "Must document data sources"
        assert "ground truth" in content.lower() or "ground_truth" in content.lower()

    def test_provenance_documents_methodology(self):
        """Provenance file should document data collection methodology."""
        provenance_path = Path(__file__).parent.parent / "data" / "DATA_PROVENANCE.md"
        with open(provenance_path) as f:
            content = f.read()

        # Check for methodology documentation
        keywords = ["methodology", "method", "process", "collection", "creation"]
        assert any(keyword in content.lower() for keyword in keywords), (
            "Must document data collection methodology"
        )

    def test_provenance_documents_held_out_split(self):
        """Provenance file should explain the held-out/public split."""
        provenance_path = Path(__file__).parent.parent / "data" / "DATA_PROVENANCE.md"
        with open(provenance_path) as f:
            content = f.read()

        assert "held" in content.lower() and "out" in content.lower(), (
            "Must document held-out test set strategy"
        )

    def test_ground_truth_has_provenance_field(self):
        """Each entry should have a provenance field indicating its source."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        with open(ground_truth_path) as f:
            data = json.load(f)

        for entry in data:
            assert "provenance" in entry, f"Entry {entry.get('id')} missing provenance"
            assert isinstance(entry["provenance"], str), (
                f"Entry {entry.get('id')} provenance must be string"
            )
            assert len(entry["provenance"]) > 0, (
                f"Entry {entry.get('id')} provenance cannot be empty"
            )


class TestDifficultyDistribution:
    """Tests for even distribution across difficulty tiers."""

    def test_ground_truth_has_all_difficulty_levels(self):
        """Ground truth should contain all three difficulty levels."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        with open(ground_truth_path) as f:
            data = json.load(f)

        difficulties = {entry.get("difficulty", "").lower() for entry in data}
        assert "easy" in difficulties, "Must have EASY difficulty entries"
        assert "medium" in difficulties, "Must have MEDIUM difficulty entries"
        assert "hard" in difficulties, "Must have HARD difficulty entries"

    def test_difficulty_distribution_is_reasonably_balanced(self):
        """Difficulty tiers should be reasonably balanced (no tier < 20% of total)."""
        ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
        with open(ground_truth_path) as f:
            data = json.load(f)

        difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
        for entry in data:
            difficulty = entry.get("difficulty", "").lower()
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1

        total = len(data)
        for difficulty, count in difficulty_counts.items():
            proportion = count / total if total > 0 else 0
            assert proportion >= 0.2, (
                f"{difficulty.upper()} tier has {count}/{total} ({proportion:.1%}), "
                f"should be at least 20%"
            )
