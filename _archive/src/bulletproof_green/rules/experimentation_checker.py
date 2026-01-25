"""Experimentation checker for IRS Section 41(d) compliance.

Verifies that R&D narratives document the process of experimentation required
by IRS Section 41(d). A qualifying process must demonstrate technical uncertainty,
evaluation of alternatives, and documentation of failures.
"""

from typing import TypedDict


class AnalysisResult(TypedDict):
    """Result of experimentation analysis."""

    score: int
    uncertainty_found: bool
    alternatives_found: bool
    failures_found: bool


class ExperimentationChecker:
    """Checks for IRS Section 41(d) process of experimentation evidence.

    This checker verifies that narratives document the systematic evaluation
    of alternatives required for qualified research under IRS Section 41(d).
    """

    # Keywords indicating technical uncertainty
    UNCERTAINTY_KEYWORDS = [
        "unknown",
        "uncertain",
        "unclear",
        "hypothesis",
        "experiment",
    ]

    # Keywords indicating evaluation of alternatives
    ALTERNATIVES_KEYWORDS = [
        "tried",
        "tested",
        "compared",
        "alternative",
    ]

    # Keywords indicating documented failures
    FAILURES_KEYWORDS = [
        "failed",
        "didn't work",
        "unsuccessful",
        "issue",
    ]

    # Maximum score for this component (15% weight in total risk score)
    MAX_SCORE = 15

    def analyze(self, narrative: str) -> AnalysisResult:
        """Analyze narrative for process of experimentation evidence.

        Args:
            narrative: R&D narrative text to analyze

        Returns:
            Analysis result with score (0-15) and experimentation indicators
        """
        narrative_lower = narrative.lower()

        # Check for each experimentation element
        uncertainty_found = self._check_keywords(narrative_lower, self.UNCERTAINTY_KEYWORDS)
        alternatives_found = self._check_keywords(narrative_lower, self.ALTERNATIVES_KEYWORDS)
        failures_found = self._check_keywords(narrative_lower, self.FAILURES_KEYWORDS)

        # Calculate risk score based on missing elements
        score = self._calculate_score(uncertainty_found, alternatives_found, failures_found)

        return {
            "score": score,
            "uncertainty_found": uncertainty_found,
            "alternatives_found": alternatives_found,
            "failures_found": failures_found,
        }

    def _check_keywords(self, narrative: str, keywords: list[str]) -> bool:
        """Check if any keyword from the list is present in the narrative.

        Args:
            narrative: Lowercase narrative text
            keywords: List of keywords to search for

        Returns:
            True if any keyword found, False otherwise
        """
        return any(keyword in narrative for keyword in keywords)

    def _calculate_score(
        self, uncertainty_found: bool, alternatives_found: bool, failures_found: bool
    ) -> int:
        """Calculate risk score based on experimentation evidence.

        The score increases (higher risk) when experimentation elements are missing.
        Each missing element adds points to the risk score.

        Args:
            uncertainty_found: Whether uncertainty indicators were found
            alternatives_found: Whether alternatives evaluation was found
            failures_found: Whether failures were documented

        Returns:
            Risk score between 0 and MAX_SCORE (15)
        """
        # Count missing elements
        missing_count = 0
        if not uncertainty_found:
            missing_count += 1
        if not alternatives_found:
            missing_count += 1
        if not failures_found:
            missing_count += 1

        # Each missing element adds 5 points (3 missing = 15 max score)
        score = missing_count * 5

        # Cap at maximum score
        return min(score, self.MAX_SCORE)
