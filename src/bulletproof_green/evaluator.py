"""Rule-based evaluator for IRS Section 41 R&D tax credit narratives.

Evaluates narratives against IRS Section 41 audit standards using rule-based
detection of disqualifying patterns.
"""

from dataclasses import dataclass, field


@dataclass
class Issue:
    """Represents a detected issue in the narrative."""

    category: str
    severity: str
    text: str
    suggestion: str


@dataclass
class Redline:
    """Redline markup containing detected issues."""

    total_issues: int = 0
    issues: list[Issue] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Structured evaluation result per Green-Agent-Metrics-Specification.md."""

    classification: str = "NON_QUALIFYING"
    confidence: float = 0.0
    risk_score: int = 100
    risk_category: str = "CRITICAL"
    component_scores: dict = field(default_factory=dict)
    redline: Redline = field(default_factory=Redline)


class RuleBasedEvaluator:
    """Evaluates narratives against IRS Section 41 using rule-based detection."""

    def evaluate(self, narrative: str) -> EvaluationResult:
        """Evaluate a narrative and return structured results.

        Args:
            narrative: The narrative text to evaluate

        Returns:
            EvaluationResult with risk score, classification, and redline markup
        """
        # Stub implementation - tests should fail
        raise NotImplementedError("Evaluator not yet implemented")
