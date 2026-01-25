"""Tests for ground truth dataset validation.

Verifies STORY-008 acceptance criteria:
- 10+ labeled narratives (minimum for Phase 1)
- Mix of qualifying (Risk Score < 20) and non-qualifying narratives
- Covers failure patterns: vague language, business risk, routine engineering
- Difficulty tiers: Easy (obvious), Medium (subtle), Hard (edge cases)
- JSON format with human-readable annotations
- Each entry: narrative, expected_score, classification, annotations
- Anonymized to protect confidentiality

Verifies STORY-017 acceptance criteria (Phase 2):
- 20+ labeled narratives (Phase 2 target)
- Even distribution across difficulty tiers
- Additional edge cases and pattern variations
- Updated JSON schema with new fields
- Covers Phase 2 evaluation scenarios
- Anonymized and reviewed for accuracy
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
        """Each entry must have required fields."""
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
        qualifying = [
            e for e in ground_truth_data if e.get("classification") == "QUALIFYING"
        ]
        non_qualifying = [
            e for e in ground_truth_data if e.get("classification") == "NON_QUALIFYING"
        ]
        assert len(qualifying) >= 3, (
            f"Need at least 3 qualifying narratives, found {len(qualifying)}"
        )
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
        import re
        # Check for common real company names that shouldn't appear (as whole words)
        prohibited = ["google", "amazon", "microsoft", "facebook", "apple", "netflix", "uber"]
        for entry in ground_truth_data:
            narrative = entry.get("narrative", "").lower()
            for company in prohibited:
                # Use word boundary to avoid false positives (e.g., "kubernetes" contains "uber")
                pattern = rf"\b{company}\b"
                assert not re.search(pattern, narrative), (
                    f"Entry {entry.get('id')}: contains company name '{company}'"
                )


# =============================================================================
# STORY-017: Phase 2 Tests - Expanded Ground Truth Dataset
# =============================================================================


class TestPhase2DatasetSize:
    """Tests for Phase 2 requirement: 20+ labeled narratives."""

    def test_phase2_minimum_entries(self, ground_truth_data: list[dict]) -> None:
        """Phase 2: Dataset must have at least 20 labeled narratives."""
        assert len(ground_truth_data) >= 20, (
            f"Phase 2 requires at least 20 narratives, found {len(ground_truth_data)}"
        )


class TestPhase2DifficultyDistribution:
    """Tests for Phase 2 requirement: even distribution across difficulty tiers."""

    def test_even_distribution_across_tiers(self, ground_truth_data: list[dict]) -> None:
        """Each difficulty tier should have at least 6 entries for even distribution."""
        tier_counts = {"easy": 0, "medium": 0, "hard": 0}
        for entry in ground_truth_data:
            tier = entry.get("difficulty", "unknown")
            if tier in tier_counts:
                tier_counts[tier] += 1

        min_per_tier = 6
        for tier, count in tier_counts.items():
            assert count >= min_per_tier, (
                f"Tier '{tier}' needs at least {min_per_tier} entries for even distribution, "
                f"found {count}"
            )

    def test_both_classifications_per_tier(self, ground_truth_data: list[dict]) -> None:
        """Each difficulty tier should have both QUALIFYING and NON_QUALIFYING entries."""
        tier_classifications: dict[str, set[str]] = {"easy": set(), "medium": set(), "hard": set()}
        for entry in ground_truth_data:
            tier = entry.get("difficulty", "unknown")
            classification = entry.get("classification", "")
            if tier in tier_classifications:
                tier_classifications[tier].add(classification)

        for tier, classifications in tier_classifications.items():
            assert "QUALIFYING" in classifications, (
                f"Tier '{tier}' missing QUALIFYING entries"
            )
            assert "NON_QUALIFYING" in classifications, (
                f"Tier '{tier}' missing NON_QUALIFYING entries"
            )


class TestPhase2PatternVariations:
    """Tests for Phase 2 requirement: additional edge cases and pattern variations."""

    def test_multiple_failure_pattern_combinations(self, ground_truth_data: list[dict]) -> None:
        """Dataset should include entries with multiple combined failure patterns."""
        multi_pattern_count = 0
        for entry in ground_truth_data:
            annotations = entry.get("annotations", {})
            patterns = annotations.get("failure_patterns", [])
            if len(patterns) >= 2:
                multi_pattern_count += 1

        assert multi_pattern_count >= 3, (
            f"Need at least 3 entries with multiple failure patterns, found {multi_pattern_count}"
        )

    def test_diverse_failure_patterns(self, ground_truth_data: list[dict]) -> None:
        """Dataset should cover diverse failure pattern types."""
        all_patterns: set[str] = set()
        for entry in ground_truth_data:
            annotations = entry.get("annotations", {})
            patterns = annotations.get("failure_patterns", [])
            all_patterns.update(patterns)

        required_patterns = {"routine_engineering", "vague_language", "business_risk"}
        missing = required_patterns - all_patterns
        assert not missing, f"Missing required failure patterns: {missing}"

    def test_diverse_positive_indicators(self, ground_truth_data: list[dict]) -> None:
        """Qualifying entries should demonstrate diverse positive indicators."""
        qualifying_entries = [
            e for e in ground_truth_data if e.get("classification") == "QUALIFYING"
        ]
        all_indicators: set[str] = set()
        for entry in qualifying_entries:
            annotations = entry.get("annotations", {})
            indicators = annotations.get("positive_indicators", [])
            all_indicators.update(indicators)

        # Should have a variety of positive indicators (at least 10 different ones)
        assert len(all_indicators) >= 10, (
            f"Need at least 10 different positive indicators, found {len(all_indicators)}"
        )


class TestPhase2EvaluationScenarios:
    """Tests for Phase 2 requirement: covers Phase 2 evaluation scenarios."""

    def test_edge_case_scores(self, ground_truth_data: list[dict]) -> None:
        """Dataset should include edge cases near the 20-point threshold."""
        # Count entries with scores near the threshold (15-25 range)
        edge_case_count = sum(
            1 for e in ground_truth_data
            if 15 <= e.get("expected_score", 0) <= 25
        )
        assert edge_case_count >= 3, (
            f"Need at least 3 edge cases near threshold (score 15-25), found {edge_case_count}"
        )

    def test_extreme_scores_represented(self, ground_truth_data: list[dict]) -> None:
        """Dataset should include narratives with extreme scores."""
        scores = [e.get("expected_score", 0) for e in ground_truth_data]

        # Should have some very low scores (excellent qualifying)
        low_scores = [s for s in scores if s <= 10]
        assert len(low_scores) >= 2, "Need at least 2 entries with score <= 10"

        # Should have some very high scores (clearly non-qualifying)
        high_scores = [s for s in scores if s >= 60]
        assert len(high_scores) >= 2, "Need at least 2 entries with score >= 60"

    def test_balanced_qualifying_non_qualifying(self, ground_truth_data: list[dict]) -> None:
        """Phase 2 requires balanced mix of qualifying and non-qualifying."""
        qualifying = [
            e for e in ground_truth_data if e.get("classification") == "QUALIFYING"
        ]
        non_qualifying = [
            e for e in ground_truth_data if e.get("classification") == "NON_QUALIFYING"
        ]

        # Both categories should have at least 8 entries
        assert len(qualifying) >= 8, (
            f"Need at least 8 qualifying entries, found {len(qualifying)}"
        )
        assert len(non_qualifying) >= 8, (
            f"Need at least 8 non-qualifying entries, found {len(non_qualifying)}"
        )
