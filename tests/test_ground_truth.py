"""Tests for ground truth dataset validation.

Verifies STORY-008 acceptance criteria:
- 10+ labeled narratives (minimum for Phase 1)
- Mix of qualifying (Risk Score < 20) and non-qualifying narratives
- Covers failure patterns: vague language, business risk, routine engineering
- Difficulty tiers: Easy (obvious), Medium (subtle), Hard (edge cases)
- JSON format with human-readable annotations
- Each entry: narrative, expected_score, classification, annotations
- Anonymized to protect confidentiality
"""

import json
from pathlib import Path

import pytest

GROUND_TRUTH_PATH = Path(__file__).parent.parent / "data" / "ground_truth.json"


@pytest.fixture
def ground_truth_data() -> list[dict]:
    """Load the ground truth dataset."""
    assert GROUND_TRUTH_PATH.exists(), f"Ground truth file not found: {GROUND_TRUTH_PATH}"
    with open(GROUND_TRUTH_PATH) as f:
        data = json.load(f)
    assert isinstance(data, list), "Ground truth must be a JSON array"
    return data


class TestGroundTruthDataset:
    """Tests for ground truth dataset requirements."""

    def test_minimum_entries(self, ground_truth_data: list[dict]) -> None:
        """Dataset must have at least 10 labeled narratives."""
        assert len(ground_truth_data) >= 10, (
            f"Dataset must have at least 10 narratives, found {len(ground_truth_data)}"
        )

    def test_required_fields(self, ground_truth_data: list[dict]) -> None:
        """Each entry must have required fields: narrative, expected_score, classification, annotations."""
        required_fields = {"id", "narrative", "expected_score", "classification", "annotations"}
        for i, entry in enumerate(ground_truth_data):
            missing = required_fields - set(entry.keys())
            assert not missing, f"Entry {i} missing required fields: {missing}"

    def test_id_uniqueness(self, ground_truth_data: list[dict]) -> None:
        """All entry IDs must be unique."""
        ids = [entry.get("id") for entry in ground_truth_data]
        assert len(ids) == len(set(ids)), "Entry IDs must be unique"

    def test_narrative_content(self, ground_truth_data: list[dict]) -> None:
        """Narratives must be non-empty strings with reasonable length."""
        for entry in ground_truth_data:
            narrative = entry.get("narrative", "")
            assert isinstance(narrative, str), f"Entry {entry.get('id')}: narrative must be string"
            assert len(narrative) >= 100, (
                f"Entry {entry.get('id')}: narrative too short (min 100 chars)"
            )
            assert len(narrative) <= 3000, (
                f"Entry {entry.get('id')}: narrative too long (max 3000 chars)"
            )

    def test_expected_score_range(self, ground_truth_data: list[dict]) -> None:
        """Expected score must be integer 0-100."""
        for entry in ground_truth_data:
            score = entry.get("expected_score")
            assert isinstance(score, int), f"Entry {entry.get('id')}: expected_score must be int"
            assert 0 <= score <= 100, (
                f"Entry {entry.get('id')}: expected_score must be 0-100, got {score}"
            )

    def test_classification_values(self, ground_truth_data: list[dict]) -> None:
        """Classification must be QUALIFYING or NON_QUALIFYING."""
        valid_classifications = {"QUALIFYING", "NON_QUALIFYING"}
        for entry in ground_truth_data:
            classification = entry.get("classification")
            assert classification in valid_classifications, (
                f"Entry {entry.get('id')}: invalid classification '{classification}'"
            )

    def test_classification_score_consistency(self, ground_truth_data: list[dict]) -> None:
        """Classification must align with expected_score (QUALIFYING: score < 20)."""
        for entry in ground_truth_data:
            score = entry.get("expected_score", 100)
            classification = entry.get("classification", "")
            if classification == "QUALIFYING":
                assert score < 20, (
                    f"Entry {entry.get('id')}: QUALIFYING must have score < 20, got {score}"
                )
            else:
                assert score >= 20, (
                    f"Entry {entry.get('id')}: NON_QUALIFYING must have score >= 20, got {score}"
                )


class TestGroundTruthMixture:
    """Tests for dataset balance and coverage."""

    def test_qualifying_and_non_qualifying_mix(self, ground_truth_data: list[dict]) -> None:
        """Dataset must have both qualifying and non-qualifying narratives."""
        qualifying = [e for e in ground_truth_data if e.get("classification") == "QUALIFYING"]
        non_qualifying = [e for e in ground_truth_data if e.get("classification") == "NON_QUALIFYING"]
        assert len(qualifying) >= 3, f"Need at least 3 qualifying narratives, found {len(qualifying)}"
        assert len(non_qualifying) >= 3, (
            f"Need at least 3 non-qualifying narratives, found {len(non_qualifying)}"
        )


class TestFailurePatternCoverage:
    """Tests for failure pattern coverage."""

    def test_covers_routine_engineering(self, ground_truth_data: list[dict]) -> None:
        """Dataset must include narratives flagged for routine engineering."""
        annotations_text = " ".join(
            str(e.get("annotations", {})) for e in ground_truth_data
        ).lower()
        assert "routine" in annotations_text or any(
            "routine" in str(e.get("failure_patterns", [])).lower() for e in ground_truth_data
        ), "Dataset must include narratives covering routine engineering pattern"

    def test_covers_business_risk(self, ground_truth_data: list[dict]) -> None:
        """Dataset must include narratives flagged for business risk language."""
        annotations_text = " ".join(
            str(e.get("annotations", {})) for e in ground_truth_data
        ).lower()
        assert "business" in annotations_text or any(
            "business" in str(e.get("failure_patterns", [])).lower() for e in ground_truth_data
        ), "Dataset must include narratives covering business risk pattern"

    def test_covers_vague_language(self, ground_truth_data: list[dict]) -> None:
        """Dataset must include narratives flagged for vague language."""
        annotations_text = " ".join(
            str(e.get("annotations", {})) for e in ground_truth_data
        ).lower()
        assert "vague" in annotations_text or any(
            "vague" in str(e.get("failure_patterns", [])).lower() for e in ground_truth_data
        ), "Dataset must include narratives covering vague language pattern"


class TestDifficultyTiers:
    """Tests for difficulty tier coverage."""

    def test_difficulty_tiers_present(self, ground_truth_data: list[dict]) -> None:
        """Dataset must include entries for each difficulty tier."""
        tiers = {e.get("difficulty") for e in ground_truth_data}
        required_tiers = {"easy", "medium", "hard"}
        missing = required_tiers - tiers
        assert not missing, f"Missing difficulty tiers: {missing}"

    def test_each_tier_has_entries(self, ground_truth_data: list[dict]) -> None:
        """Each difficulty tier must have at least one entry."""
        tier_counts = {}
        for entry in ground_truth_data:
            tier = entry.get("difficulty", "unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        for tier in ["easy", "medium", "hard"]:
            assert tier_counts.get(tier, 0) >= 1, f"Tier '{tier}' must have at least 1 entry"


class TestAnnotations:
    """Tests for annotation quality."""

    def test_annotations_structure(self, ground_truth_data: list[dict]) -> None:
        """Annotations must be a dict with human-readable content."""
        for entry in ground_truth_data:
            annotations = entry.get("annotations")
            assert isinstance(annotations, dict), (
                f"Entry {entry.get('id')}: annotations must be a dict"
            )
            assert "irs_rationale" in annotations, (
                f"Entry {entry.get('id')}: annotations must include 'irs_rationale'"
            )

    def test_annotations_not_empty(self, ground_truth_data: list[dict]) -> None:
        """Annotations must contain meaningful content."""
        for entry in ground_truth_data:
            rationale = entry.get("annotations", {}).get("irs_rationale", "")
            assert len(rationale) >= 50, (
                f"Entry {entry.get('id')}: irs_rationale must be at least 50 chars"
            )


class TestAnonymization:
    """Tests for anonymization (no PII or confidential info)."""

    def test_no_email_addresses(self, ground_truth_data: list[dict]) -> None:
        """Narratives must not contain email addresses."""
        import re
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        for entry in ground_truth_data:
            narrative = entry.get("narrative", "")
            match = email_pattern.search(narrative)
            assert match is None, f"Entry {entry.get('id')}: contains email address"

    def test_no_phone_numbers(self, ground_truth_data: list[dict]) -> None:
        """Narratives must not contain phone numbers."""
        import re
        phone_pattern = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
        for entry in ground_truth_data:
            narrative = entry.get("narrative", "")
            match = phone_pattern.search(narrative)
            assert match is None, f"Entry {entry.get('id')}: contains phone number"

    def test_no_specific_company_names(self, ground_truth_data: list[dict]) -> None:
        """Narratives should use generic references, not specific company names."""
        # Check for common real company names that shouldn't appear
        prohibited = ["google", "amazon", "microsoft", "facebook", "apple", "netflix", "uber"]
        for entry in ground_truth_data:
            narrative = entry.get("narrative", "").lower()
            for company in prohibited:
                assert company not in narrative, (
                    f"Entry {entry.get('id')}: contains company name '{company}'"
                )
