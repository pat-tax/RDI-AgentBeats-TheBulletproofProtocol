"""Benchmark validation script for IRS Section 41 narratives (STORY-009).

Validates ground truth dataset and measures benchmark performance by running
the Green Agent evaluator on each narrative and computing accuracy metrics.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bulletproof_green.evaluator import RuleBasedEvaluator
from bulletproof_green.scorer import AgentBeatsScorer


@dataclass
class ValidationResult:
    """Result of validating a single narrative entry."""

    entry_id: str
    expected_score: int
    actual_score: int
    expected_classification: str
    actual_classification: str
    classification_match: bool
    score_delta: int
    difficulty: str


@dataclass
class DifficultyTierResult:
    """Pass/fail results for a difficulty tier."""

    tier: str
    total: int
    passed: int
    failed: int
    pass_rate: float


@dataclass
class BenchmarkReport:
    """Complete benchmark validation report."""

    validation_results: list[ValidationResult]
    metrics: dict[str, float]
    tier_results: list[DifficultyTierResult]
    gaps: list[dict[str, str]]

    def to_summary(self) -> str:
        """Generate a human-readable summary of the report."""
        lines = [
            "=" * 60,
            "BENCHMARK VALIDATION REPORT",
            "=" * 60,
            "",
            "OVERALL METRICS",
            "-" * 30,
            f"Accuracy:  {self.metrics['accuracy']:.2%}",
            f"Precision: {self.metrics['precision']:.2%}",
            f"Recall:    {self.metrics['recall']:.2%}",
            f"F1 Score:  {self.metrics['f1_score']:.2%}",
            "",
            "RESULTS BY DIFFICULTY TIER",
            "-" * 30,
        ]

        for tier in self.tier_results:
            lines.append(
                f"{tier.tier.upper():8} - Pass: {tier.passed}/{tier.total} ({tier.pass_rate:.0%})"
            )

        if self.gaps:
            lines.extend(
                [
                    "",
                    "IDENTIFIED GAPS",
                    "-" * 30,
                ]
            )
            for gap in self.gaps:
                lines.append(f"  - {gap['entry_id']}: {gap.get('reason', 'Unknown issue')}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def load_ground_truth(path: Path) -> list[dict[str, Any]]:
    """Load ground truth dataset from JSON file.

    Args:
        path: Path to ground_truth.json file

    Returns:
        List of ground truth entries

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file contains invalid JSON
    """
    if not path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {path}")

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in ground truth file: {e}") from e

    return data


class BenchmarkValidator:
    """Validates benchmark using Green Agent evaluator.

    Runs the RuleBasedEvaluator and AgentBeatsScorer on each narrative
    in the ground truth dataset and compares results.
    """

    # Threshold for considering score delta as significant
    SCORE_DELTA_THRESHOLD = 15

    def __init__(self) -> None:
        """Initialize validator with Green Agent components."""
        self.evaluator = RuleBasedEvaluator()
        self.scorer = AgentBeatsScorer()

    def validate_entry(self, entry: dict[str, Any]) -> ValidationResult:
        """Validate a single ground truth entry.

        Args:
            entry: Ground truth entry with narrative, expected_score, etc.

        Returns:
            ValidationResult with actual vs expected comparison
        """
        narrative = entry.get("narrative", "")
        expected_score = entry.get("expected_score", 100)
        expected_classification = entry.get("classification", "NON_QUALIFYING")
        difficulty = entry.get("difficulty", "unknown")
        entry_id = entry.get("id", "unknown")

        # Run Green Agent evaluation
        eval_result = self.evaluator.evaluate(narrative)
        actual_score = eval_result.risk_score
        actual_classification = eval_result.classification

        # Compare results
        classification_match = expected_classification == actual_classification
        score_delta = actual_score - expected_score

        return ValidationResult(
            entry_id=entry_id,
            expected_score=expected_score,
            actual_score=actual_score,
            expected_classification=expected_classification,
            actual_classification=actual_classification,
            classification_match=classification_match,
            score_delta=score_delta,
            difficulty=difficulty,
        )

    def validate_all(self, data: list[dict[str, Any]]) -> list[ValidationResult]:
        """Validate all entries in ground truth dataset.

        Args:
            data: List of ground truth entries

        Returns:
            List of ValidationResults
        """
        return [self.validate_entry(entry) for entry in data]

    def compute_metrics(self, results: list[ValidationResult]) -> dict[str, float]:
        """Compute precision, recall, F1, and accuracy metrics.

        Classification metrics treat QUALIFYING as the positive class:
        - True Positive: Expected QUALIFYING, Actual QUALIFYING
        - False Positive: Expected NON_QUALIFYING, Actual QUALIFYING
        - False Negative: Expected QUALIFYING, Actual NON_QUALIFYING
        - True Negative: Expected NON_QUALIFYING, Actual NON_QUALIFYING

        Args:
            results: List of ValidationResults

        Returns:
            Dict with precision, recall, f1_score, accuracy
        """
        tp = fp = fn = tn = 0

        for r in results:
            if r.expected_classification == "QUALIFYING":
                if r.actual_classification == "QUALIFYING":
                    tp += 1
                else:
                    fn += 1
            else:  # NON_QUALIFYING
                if r.actual_classification == "QUALIFYING":
                    fp += 1
                else:
                    tn += 1

        # Handle edge cases to avoid division by zero
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (
            2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        )
        accuracy = (tp + tn) / len(results) if results else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
        }

    def generate_tier_results(self, results: list[ValidationResult]) -> list[DifficultyTierResult]:
        """Generate pass/fail results per difficulty tier.

        Args:
            results: List of ValidationResults

        Returns:
            List of DifficultyTierResults
        """
        tier_data: dict[str, dict[str, int]] = {}

        for r in results:
            tier = r.difficulty
            if tier not in tier_data:
                tier_data[tier] = {"total": 0, "passed": 0, "failed": 0}

            tier_data[tier]["total"] += 1
            if r.classification_match:
                tier_data[tier]["passed"] += 1
            else:
                tier_data[tier]["failed"] += 1

        tier_results = []
        for tier, data in sorted(tier_data.items()):
            pass_rate = data["passed"] / data["total"] if data["total"] > 0 else 0.0
            tier_results.append(
                DifficultyTierResult(
                    tier=tier,
                    total=data["total"],
                    passed=data["passed"],
                    failed=data["failed"],
                    pass_rate=pass_rate,
                )
            )

        return tier_results

    def identify_gaps(self, results: list[ValidationResult]) -> list[dict[str, str]]:
        """Identify gaps and improvement areas.

        Gaps include:
        - Classification mismatches
        - Large score deltas (> threshold)

        Args:
            results: List of ValidationResults

        Returns:
            List of gap dictionaries with entry_id, reason, and suggestion
        """
        gaps = []

        for r in results:
            reasons: list[str] = []

            if not r.classification_match:
                reasons.append(
                    f"Classification mismatch: expected {r.expected_classification}, "
                    f"got {r.actual_classification}"
                )

            if abs(r.score_delta) > self.SCORE_DELTA_THRESHOLD:
                reasons.append(
                    f"Large score delta: {r.score_delta:+d} points "
                    f"(expected {r.expected_score}, got {r.actual_score})"
                )

            if reasons:
                suggestion = self._generate_suggestion(r)
                gaps.append(
                    {
                        "entry_id": r.entry_id,
                        "reason": "; ".join(reasons),
                        "suggestion": suggestion,
                        "difficulty": r.difficulty,
                    }
                )

        return gaps

    def _generate_suggestion(self, result: ValidationResult) -> str:
        """Generate improvement suggestion for a gap.

        Args:
            result: ValidationResult with gap

        Returns:
            Suggestion string
        """
        if (
            result.expected_classification == "QUALIFYING"
            and result.actual_classification == "NON_QUALIFYING"
        ):
            return (
                "Evaluator may be too strict. Review if narrative contains sufficient "
                "experimentation evidence that is not being detected."
            )
        elif (
            result.expected_classification == "NON_QUALIFYING"
            and result.actual_classification == "QUALIFYING"
        ):
            return (
                "Evaluator may be too lenient. Review if routine engineering, "
                "business risk, or vague language patterns should be detected."
            )
        else:
            return "Review scoring calibration for this difficulty tier."

    def generate_report(self, data: list[dict[str, Any]]) -> BenchmarkReport:
        """Generate complete benchmark validation report.

        Args:
            data: Ground truth dataset

        Returns:
            BenchmarkReport with all metrics and analysis
        """
        results = self.validate_all(data)
        metrics = self.compute_metrics(results)
        tier_results = self.generate_tier_results(results)
        gaps = self.identify_gaps(results)

        return BenchmarkReport(
            validation_results=results,
            metrics=metrics,
            tier_results=tier_results,
            gaps=gaps,
        )


def main() -> None:
    """Run benchmark validation from command line."""
    ground_truth_path = Path(__file__).parent.parent / "data" / "ground_truth.json"

    print(f"Loading ground truth from: {ground_truth_path}")
    data = load_ground_truth(ground_truth_path)
    print(f"Loaded {len(data)} entries")

    validator = BenchmarkValidator()
    report = validator.generate_report(data)

    print(report.to_summary())


if __name__ == "__main__":
    main()
