"""Risk scorer for IRS Section 41 R&D tax credit evaluation.

Aggregates component scores into final risk score (0-100) with weighted algorithm.
Uses weighted combination of multiple risk factors to determine overall qualification risk.
"""

from typing import TypedDict


class RiskResult(TypedDict):
    """Result of risk scoring calculation."""

    risk_score: int
    classification: str
    component_scores: dict[str, int]


class RiskScorer:
    """Calculates final risk score from component scores.

    This scorer combines multiple component scores using weighted aggregation
    to produce a final risk score (0-100) and classification decision.

    Component weights:
    - routine_engineering: 30% (max 30 points)
    - vagueness: 25% (max 25 points)
    - business_risk: 20% (max 20 points)
    - experimentation: 15% (max 15 points)
    - specificity: 10% (max 10 points)
    """

    # Classification threshold
    QUALIFYING_THRESHOLD = 20

    def calculate_risk(self, component_scores: dict[str, int]) -> RiskResult:
        """Calculate risk score from component scores.

        Args:
            component_scores: Dictionary with keys:
                - routine_engineering (0-30)
                - vagueness (0-25)
                - business_risk (0-20)
                - experimentation (0-15)
                - specificity (0-10)

        Returns:
            Risk result with risk_score (0-100), classification, and component_scores
        """
        # Sum all component scores (already weighted by their max values)
        risk_score = (
            component_scores.get("routine_engineering", 0)
            + component_scores.get("vagueness", 0)
            + component_scores.get("business_risk", 0)
            + component_scores.get("experimentation", 0)
            + component_scores.get("specificity", 0)
        )

        # Ensure risk_score is an integer
        risk_score = int(risk_score)

        # Classify based on threshold
        classification = (
            "QUALIFYING" if risk_score < self.QUALIFYING_THRESHOLD else "NON_QUALIFYING"
        )

        return {
            "risk_score": risk_score,
            "classification": classification,
            "component_scores": component_scores.copy(),
        }
