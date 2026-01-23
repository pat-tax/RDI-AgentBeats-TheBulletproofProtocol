#!/usr/bin/env python3
"""Validate benchmark metrics for green agent.

This script runs the green agent against the ground truth dataset and
measures classification accuracy, F1 score, precision, and recall using
sklearn.metrics.

The goal is to beat the IRS AI baseline:
- Accuracy: 61.2% → Target: >= 70%
- F1 Score: 0.42 → Target: >= 0.72
- Precision: Target >= 75%
- Recall: Target >= 70%
"""

import json
import sys
from pathlib import Path

from sklearn.metrics import (  # type: ignore[import-untyped]
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bulletproof_green.evaluator import EvaluationResult, NarrativeEvaluator


def load_ground_truth() -> list[dict]:
    """Load the ground truth dataset.

    Returns:
        List of ground truth cases with id, narrative, label, irs_rationale
    """
    data_path = Path(__file__).parent.parent / "data" / "ground_truth.json"
    with open(data_path) as f:
        return json.load(f)


def evaluate_narrative(evaluator: NarrativeEvaluator, narrative: str) -> EvaluationResult:
    """Evaluate a single narrative using the green agent.

    Args:
        evaluator: The NarrativeEvaluator instance
        narrative: The R&D narrative text

    Returns:
        Evaluation result dict with risk_score, classification, etc.
    """
    return evaluator.evaluate(narrative)


def run_validation() -> dict:
    """Run validation against all ground truth cases.

    Returns:
        Dict with metrics (accuracy, f1_score, precision, recall) and predictions
    """
    # Load ground truth data
    ground_truth = load_ground_truth()

    # Initialize evaluator
    evaluator = NarrativeEvaluator()

    # Evaluate each case
    predictions = []
    true_labels = []
    predicted_labels = []

    print(f"Evaluating {len(ground_truth)} ground truth cases...")

    for i, case in enumerate(ground_truth, 1):
        narrative_id = case["id"]
        narrative = case["narrative"]
        true_label = case["label"]

        # Evaluate with green agent
        result = evaluate_narrative(evaluator, narrative)
        predicted_label = result["classification"]
        risk_score = result["risk_score"]

        # Store results
        predictions.append(
            {
                "id": narrative_id,
                "true_label": true_label,
                "predicted_label": predicted_label,
                "risk_score": risk_score,
            }
        )

        true_labels.append(true_label)
        predicted_labels.append(predicted_label)

        # Progress indicator
        correct = "✓" if true_label == predicted_label else "✗"
        print(f"  [{i:2d}/20] {narrative_id}: {correct} (score={risk_score})")

    # Calculate metrics using sklearn
    accuracy = accuracy_score(true_labels, predicted_labels)
    f1 = f1_score(
        true_labels,
        predicted_labels,
        pos_label="QUALIFYING",  # type: ignore[arg-type]
        zero_division=0.0,  # type: ignore[arg-type]
    )
    precision = precision_score(
        true_labels,
        predicted_labels,
        pos_label="QUALIFYING",  # type: ignore[arg-type]
        zero_division=0.0,  # type: ignore[arg-type]
    )
    recall = recall_score(
        true_labels,
        predicted_labels,
        pos_label="QUALIFYING",  # type: ignore[arg-type]
        zero_division=0.0,  # type: ignore[arg-type]
    )

    # Compile results
    results = {
        "accuracy": float(accuracy),
        "f1_score": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "n_samples": len(ground_truth),
        "predictions": predictions,
    }

    return results


def save_results(results: dict) -> None:
    """Save validation results to results/benchmark_validation.json.

    Args:
        results: Dict with metrics and predictions
    """
    output_path = Path(__file__).parent.parent / "results" / "benchmark_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")


def print_summary(results: dict) -> None:
    """Print a summary of the validation results.

    Args:
        results: Dict with metrics and predictions
    """
    accuracy = results["accuracy"]
    f1 = results["f1_score"]
    precision = results["precision"]
    recall = results["recall"]

    print("\n" + "=" * 60)
    print("BENCHMARK VALIDATION RESULTS")
    print("=" * 60)
    print(f"Samples evaluated: {results['n_samples']}")
    print()
    print(f"Accuracy:  {accuracy:.1%} {'✓' if accuracy >= 0.70 else '✗'} (target: >= 70%)")
    print(f"F1 Score:  {f1:.2f} {'✓' if f1 >= 0.72 else '✗'} (target: >= 0.72)")
    print(f"Precision: {precision:.1%} {'✓' if precision >= 0.75 else '✗'} (target: >= 75%)")
    print(f"Recall:    {recall:.1%} {'✓' if recall >= 0.70 else '✗'} (target: >= 70%)")
    print()
    print("Baseline comparison (IRS AI):")
    print(f"  Accuracy: 61.2% → {accuracy:.1%} ({accuracy - 0.612:+.1%})")
    print(f"  F1 Score: 0.42 → {f1:.2f} ({f1 - 0.42:+.2f})")
    print("=" * 60)


def main() -> int:
    """Main entry point for validation script.

    Returns:
        Exit code (0 for success)
    """
    try:
        # Run validation
        results = run_validation()

        # Save results
        save_results(results)

        # Print summary
        print_summary(results)

        return 0

    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
