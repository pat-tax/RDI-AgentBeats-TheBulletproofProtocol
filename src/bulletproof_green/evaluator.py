"""Narrative evaluator for IRS Section 41 R&D tax credit compliance.

Evaluates R&D narratives and returns structured judgments with risk scores.
"""


class NarrativeEvaluator:
    """Evaluates R&D narratives for IRS Section 41 compliance."""

    def evaluate(self, narrative: str) -> str:
        """Evaluate a narrative and return structured judgment.

        Args:
            narrative: R&D narrative text to evaluate

        Returns:
            Structured evaluation result as text containing:
            - risk_score: 0-100 integer
            - classification: QUALIFYING or NON_QUALIFYING
            - component_scores: breakdown of risk factors
            - redline: specific feedback and issues
        """
        # Simple heuristic-based evaluation (STORY-006+ will add sophisticated rules)
        risk_score = self._calculate_risk_score(narrative)
        classification = "QUALIFYING" if risk_score < 20 else "NON_QUALIFYING"

        # Build structured result
        result = (
            f"risk_score: {risk_score}, "
            f"classification: {classification}, "
            f"component_scores: {{}}, "
            f"redline: {{}}"
        )

        return result

    def _calculate_risk_score(self, narrative: str) -> int:
        """Calculate risk score based on simple heuristics.

        Args:
            narrative: Narrative text

        Returns:
            Risk score between 0 and 100
        """
        narrative_lower = narrative.lower()

        # Simple keyword-based scoring (placeholder for full implementation)
        score = 0

        # Penalize routine engineering keywords
        routine_keywords = ["bug", "fix", "maintenance", "debug", "production issue"]
        for keyword in routine_keywords:
            if keyword in narrative_lower:
                score += 10

        # Penalize vague language
        vague_keywords = ["improve", "enhance", "optimize", "better"]
        for keyword in vague_keywords:
            if keyword in narrative_lower:
                score += 5

        # Reward experimentation indicators
        experiment_keywords = ["experiment", "uncertain", "hypothesis", "tested"]
        for keyword in experiment_keywords:
            if keyword in narrative_lower:
                score -= 5

        # Ensure score stays in 0-100 range
        return max(0, min(100, score))
