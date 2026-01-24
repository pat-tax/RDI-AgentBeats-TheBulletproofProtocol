"""Narrative evaluator for IRS Section 41 R&D tax credit compliance.

Evaluates R&D narratives and returns structured judgments with risk scores.
"""

from typing import TypedDict

from bulletproof_green.rules.experimentation_checker import ExperimentationChecker
from bulletproof_green.rules.routine_engineering import RoutineEngineeringDetector
from bulletproof_green.rules.vagueness_detector import VaguenessDetector
from bulletproof_green.scorer import RiskScorer


class EvaluationResult(TypedDict):
    """Result of narrative evaluation."""

    risk_score: int
    classification: str
    component_scores: dict[str, int]
    redline: dict[str, dict]


class NarrativeEvaluator:
    """Evaluates R&D narratives for IRS Section 41 compliance.

    This evaluator integrates multiple rule-based detectors to assess
    narratives for R&D tax credit qualification. It uses:
    - RoutineEngineeringDetector (30% weight)
    - VaguenessDetector (25% weight)
    - ExperimentationChecker (15% weight)
    - Business risk and specificity placeholders (20% + 10% weight)
    """

    def __init__(self):
        """Initialize evaluator with all detectors."""
        self.routine_detector = RoutineEngineeringDetector()
        self.vagueness_detector = VaguenessDetector()
        self.experimentation_checker = ExperimentationChecker()
        self.risk_scorer = RiskScorer()

    def evaluate(self, narrative: str) -> EvaluationResult:
        """Evaluate a narrative and return structured judgment.

        Args:
            narrative: R&D narrative text to evaluate

        Returns:
            Structured evaluation result dict containing:
            - risk_score: 0-100 integer
            - classification: QUALIFYING or NON_QUALIFYING
            - component_scores: breakdown of risk factors
            - redline: specific feedback and issues from each detector
        """
        # Run each detector's analysis
        routine_result = self.routine_detector.analyze(narrative)
        vagueness_result = self.vagueness_detector.analyze(narrative)
        experimentation_result = self.experimentation_checker.analyze(narrative)

        # Build component scores dict
        component_scores = {
            "routine_engineering": routine_result["score"],
            "vagueness": vagueness_result["score"],
            "business_risk": 0,  # Placeholder for future implementation
            "experimentation": experimentation_result["score"],
            "specificity": 0,  # Placeholder for future implementation
        }

        # Aggregate scores using RiskScorer
        risk_result = self.risk_scorer.calculate_risk(component_scores)

        # Build redline dict with detection details for transparency
        redline: dict[str, dict] = {}

        if routine_result["detections"]:
            redline["routine_engineering"] = {
                "detections": routine_result["detections"],
                "count": len(routine_result["detections"]),
            }

        if vagueness_result["detections"]:
            redline["vagueness"] = {
                "detections": vagueness_result["detections"],
                "count": len(vagueness_result["detections"]),
            }

        # Add experimentation findings to redline
        experimentation_details = {
            "uncertainty_found": experimentation_result["uncertainty_found"],
            "alternatives_found": experimentation_result["alternatives_found"],
            "failures_found": experimentation_result["failures_found"],
        }
        if not all(experimentation_details.values()):
            redline["experimentation"] = experimentation_details

        # Return structured result
        return {
            "risk_score": risk_result["risk_score"],
            "classification": risk_result["classification"],
            "component_scores": component_scores,
            "redline": redline,
        }
