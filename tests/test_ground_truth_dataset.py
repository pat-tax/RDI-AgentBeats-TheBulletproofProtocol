"""Tests for ground truth dataset (STORY-016)."""

import json
from pathlib import Path

import pytest


def test_ground_truth_json_exists() -> None:
    """Verify data/ground_truth.json file exists."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    assert ground_truth_path.exists(), "data/ground_truth.json must exist"


def test_ground_truth_json_valid_syntax() -> None:
    """Verify ground_truth.json has valid JSON syntax."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)
    assert isinstance(data, list), "ground_truth.json must be a JSON array"


def test_ground_truth_has_20_narratives() -> None:
    """Verify dataset contains exactly 20 narrative objects."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)

    assert len(data) == 20, "Dataset must contain exactly 20 narratives"


def test_ground_truth_schema_validation() -> None:
    """Verify each narrative object has required fields with correct types."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)

    required_fields = {"id", "narrative", "label", "irs_rationale"}

    for i, item in enumerate(data):
        # Check all required fields exist
        assert isinstance(item, dict), f"Item {i} must be a dictionary"
        assert set(item.keys()) == required_fields, f"Item {i} must have exactly these fields: {required_fields}"

        # Check field types
        assert isinstance(item["id"], str), f"Item {i}: id must be a string"
        assert isinstance(item["narrative"], str), f"Item {i}: narrative must be a string"
        assert isinstance(item["label"], str), f"Item {i}: label must be a string"
        assert isinstance(item["irs_rationale"], str), f"Item {i}: irs_rationale must be a string"

        # Check label values
        assert item["label"] in ["QUALIFYING", "NON_QUALIFYING"], f"Item {i}: label must be QUALIFYING or NON_QUALIFYING"

        # Check narrative is not empty
        assert len(item["narrative"]) > 0, f"Item {i}: narrative must not be empty"
        assert len(item["irs_rationale"]) > 0, f"Item {i}: irs_rationale must not be empty"


def test_ground_truth_has_10_qualifying() -> None:
    """Verify dataset has exactly 10 QUALIFYING narratives."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)

    qualifying_count = sum(1 for item in data if item["label"] == "QUALIFYING")
    assert qualifying_count == 10, "Dataset must have exactly 10 QUALIFYING narratives"


def test_ground_truth_has_10_non_qualifying() -> None:
    """Verify dataset has exactly 10 NON_QUALIFYING narratives."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)

    non_qualifying_count = sum(1 for item in data if item["label"] == "NON_QUALIFYING")
    assert non_qualifying_count == 10, "Dataset must have exactly 10 NON_QUALIFYING narratives"


def test_qualifying_narratives_have_technical_uncertainty() -> None:
    """Verify QUALIFYING narratives contain indicators of technical uncertainty."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)

    uncertainty_keywords = [
        "uncertain", "unknown", "unclear", "hypothesis", "experiment",
        "novel", "innovative", "research", "discovery", "investigation"
    ]

    qualifying_narratives = [item for item in data if item["label"] == "QUALIFYING"]

    for item in qualifying_narratives:
        narrative_lower = item["narrative"].lower()
        has_uncertainty = any(keyword in narrative_lower for keyword in uncertainty_keywords)
        assert has_uncertainty, f"QUALIFYING narrative {item['id']} must contain technical uncertainty indicators"


def test_non_qualifying_narratives_have_disqualifying_patterns() -> None:
    """Verify NON_QUALIFYING narratives contain routine engineering or vague language."""
    ground_truth_path = Path(__file__).parent.parent / "data/ground_truth.json"
    with open(ground_truth_path) as f:
        data = json.load(f)

    routine_keywords = [
        "debug", "bug fix", "production issue", "maintenance", "refactor",
        "upgrade", "migration", "optimization", "performance tuning", "code cleanup"
    ]

    vague_keywords = [
        "optimize", "improve", "enhance", "upgrade", "better", "faster"
    ]

    non_qualifying_narratives = [item for item in data if item["label"] == "NON_QUALIFYING"]

    for item in non_qualifying_narratives:
        narrative_lower = item["narrative"].lower()
        has_routine = any(keyword in narrative_lower for keyword in routine_keywords)
        has_vague = any(keyword in narrative_lower for keyword in vague_keywords)

        assert has_routine or has_vague, f"NON_QUALIFYING narrative {item['id']} must contain routine engineering or vague language"


def test_data_readme_exists() -> None:
    """Verify data/README.md file exists."""
    readme_path = Path(__file__).parent.parent / "data/README.md"
    assert readme_path.exists(), "data/README.md must exist"


def test_data_readme_documents_structure() -> None:
    """Verify data/README.md documents dataset structure and labeling criteria."""
    readme_path = Path(__file__).parent.parent / "data/README.md"
    with open(readme_path) as f:
        content = f.read()

    # Check for key documentation sections
    assert "ground_truth.json" in content, "README must document ground_truth.json"
    assert "QUALIFYING" in content, "README must explain QUALIFYING label"
    assert "NON_QUALIFYING" in content, "README must explain NON_QUALIFYING label"
    assert len(content) > 200, "README must have substantive documentation (>200 chars)"
