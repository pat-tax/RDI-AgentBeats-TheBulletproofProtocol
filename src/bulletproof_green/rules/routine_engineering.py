"""Routine engineering pattern detector for IRS Section 41 compliance.

Detects routine engineering activities that do not qualify for R&D tax credit
under IRS Section 41(d)(3). Routine engineering includes debugging, maintenance,
and other activities that do not involve technical uncertainty.
"""

from typing import TypedDict


class Detection(TypedDict):
    """A single routine engineering keyword detection."""

    keyword: str
    reason: str


class AnalysisResult(TypedDict):
    """Result of routine engineering analysis."""

    score: int
    detections: list[Detection]


class RoutineEngineeringDetector:
    """Detects routine engineering patterns in R&D narratives.

    This detector identifies keywords and patterns that indicate routine
    engineering work, which is excluded from R&D tax credit eligibility
    under IRS Section 41(d)(3).
    """

    # Routine engineering keywords with IRS guidance citations
    ROUTINE_KEYWORDS: dict[str, str] = {
        "debugging": "IRS Section 41(d)(3): Debugging is routine data collection, not qualified research",
        "bug fix": "IRS Section 41(d)(3): Bug fixes are routine maintenance, not qualified research",
        "production issue": "IRS Section 41(d)(3): Fixing production issues is routine troubleshooting",
        "maintenance": "IRS Section 41(d)(3): Routine maintenance is explicitly excluded",
        "refactor": "IRS Section 41(d)(3): Code refactoring is routine engineering without technical uncertainty",
        "upgrade": "IRS Section 41(d)(3): Upgrades are routine adaptations of existing technology",
        "migration": "IRS Section 41(d)(3): Data migration is routine engineering activity",
        "optimization": "IRS Section 41(d)(3): Performance optimization is routine engineering unless novel",
        "performance tuning": "IRS Section 41(d)(3): Performance tuning is routine engineering activity",
        "code cleanup": "IRS Section 41(d)(3): Code cleanup is routine maintenance activity",
    }

    # Maximum score for this component (30% weight in total risk score)
    MAX_SCORE = 30

    def analyze(self, narrative: str) -> AnalysisResult:
        """Analyze narrative for routine engineering patterns.

        Args:
            narrative: R&D narrative text to analyze

        Returns:
            Analysis result with score (0-30) and list of detections
        """
        narrative_lower = narrative.lower()
        detections: list[Detection] = []

        # Detect each routine keyword
        for keyword, reason in self.ROUTINE_KEYWORDS.items():
            if keyword in narrative_lower:
                detections.append({"keyword": keyword, "reason": reason})

        # Calculate score based on pattern frequency
        # Each detection adds points, capped at MAX_SCORE
        score = self._calculate_score(detections)

        return {"score": score, "detections": detections}

    def _calculate_score(self, detections: list[Detection]) -> int:
        """Calculate risk score based on detections.

        Args:
            detections: List of routine engineering detections

        Returns:
            Risk score between 0 and MAX_SCORE (30)
        """
        if not detections:
            return 0

        # Each unique detection adds 3 points
        # This ensures 10 detections = 30 points (max score)
        score = len(detections) * 3

        # Cap at maximum score
        return min(score, self.MAX_SCORE)
