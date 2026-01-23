"""Tests for benchmark validation script.

Tests that the validation script correctly evaluates the green agent
against the ground truth dataset and produces the required metrics.
"""

import json
import subprocess
from pathlib import Path


def test_validate_benchmark_script_exists():
    """Test that the validate_benchmark.py script exists."""
    script_path = Path("scripts/validate_benchmark.py")
    assert script_path.exists(), "scripts/validate_benchmark.py must exist"
    assert script_path.is_file(), "scripts/validate_benchmark.py must be a file"


def test_validate_benchmark_runs_successfully():
    """Test that the validation script runs without errors."""
    result = subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Script failed with: {result.stderr}"


def test_validate_benchmark_creates_output_file():
    """Test that the validation script creates results/benchmark_validation.json."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    assert output_path.exists(), "results/benchmark_validation.json must be created"
    assert output_path.is_file(), "results/benchmark_validation.json must be a file"


def test_benchmark_validation_output_structure():
    """Test that the output JSON has the required structure."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    # Check required fields
    assert "accuracy" in results, "Output must include accuracy"
    assert "f1_score" in results, "Output must include f1_score"
    assert "precision" in results, "Output must include precision"
    assert "recall" in results, "Output must include recall"
    assert "n_samples" in results, "Output must include n_samples"
    assert "predictions" in results, "Output must include predictions list"

    # Check data types
    assert isinstance(results["accuracy"], (int, float)), "accuracy must be numeric"
    assert isinstance(results["f1_score"], (int, float)), "f1_score must be numeric"
    assert isinstance(results["precision"], (int, float)), "precision must be numeric"
    assert isinstance(results["recall"], (int, float)), "recall must be numeric"
    assert isinstance(results["n_samples"], int), "n_samples must be integer"
    assert isinstance(results["predictions"], list), "predictions must be a list"


def test_benchmark_processes_all_ground_truth_cases():
    """Test that all 20 ground truth cases are evaluated."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    assert results["n_samples"] == 20, "Must evaluate all 20 ground truth cases"
    assert len(results["predictions"]) == 20, "Must have 20 predictions"


def test_benchmark_meets_accuracy_threshold():
    """Test that classification accuracy >= 70% (beats IRS AI 61.2%)."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    accuracy = results["accuracy"]
    assert accuracy >= 0.70, f"Accuracy {accuracy:.1%} must be >= 70% (target: beat IRS AI 61.2%)"


def test_benchmark_meets_f1_threshold():
    """Test that F1 score >= 0.72 (beats IRS AI 0.42)."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    f1_score = results["f1_score"]
    assert f1_score >= 0.72, f"F1 score {f1_score:.2f} must be >= 0.72 (target: beat IRS AI 0.42)"


def test_benchmark_meets_precision_threshold():
    """Test that precision >= 75%."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    precision = results["precision"]
    assert precision >= 0.75, f"Precision {precision:.1%} must be >= 75%"


def test_benchmark_meets_recall_threshold():
    """Test that recall >= 70%."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    recall = results["recall"]
    assert recall >= 0.70, f"Recall {recall:.1%} must be >= 70%"


def test_prediction_output_structure():
    """Test that each prediction has the required fields."""
    # Run the script
    subprocess.run(
        ["python", "scripts/validate_benchmark.py"],
        capture_output=True,
        timeout=60,
    )

    output_path = Path("results/benchmark_validation.json")
    with open(output_path) as f:
        results = json.load(f)

    for i, pred in enumerate(results["predictions"]):
        assert "id" in pred, f"Prediction {i} must include id"
        assert "true_label" in pred, f"Prediction {i} must include true_label"
        assert "predicted_label" in pred, f"Prediction {i} must include predicted_label"
        assert "risk_score" in pred, f"Prediction {i} must include risk_score"

        # Check label values
        assert pred["true_label"] in ["QUALIFYING", "NON_QUALIFYING"], (
            f"Prediction {i} true_label must be QUALIFYING or NON_QUALIFYING"
        )
        assert pred["predicted_label"] in ["QUALIFYING", "NON_QUALIFYING"], (
            f"Prediction {i} predicted_label must be QUALIFYING or NON_QUALIFYING"
        )

        # Check risk score range
        assert 0 <= pred["risk_score"] <= 100, f"Prediction {i} risk_score must be 0-100"
