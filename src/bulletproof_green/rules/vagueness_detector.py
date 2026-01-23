"""Vagueness detector for IRS Section 41 compliance.

Detects vague language without numeric substantiation that weakens R&D tax credit claims.
IRS expects specific, measurable outcomes rather than general improvement claims.
"""

import re
from typing import TypedDict


class Detection(TypedDict):
    """A single vague phrase detection."""

    phrase: str
    reason: str


class AnalysisResult(TypedDict):
    """Result of vagueness analysis."""

    score: int
    detections: list[Detection]


class VaguenessDetector:
    """Detects vague language in R&D narratives.

    This detector identifies vague phrases that lack numeric substantiation,
    which weakens R&D tax credit claims under IRS Section 41 requirements.
    """

    # Vague phrases that require numeric substantiation
    VAGUE_PHRASES: dict[str, str] = {
        "optimize": "Vague claim lacks numeric substantiation (e.g., % improvement, specific metrics)",
        "improve": "Vague claim lacks numeric substantiation (e.g., % improvement, specific metrics)",
        "enhance": "Vague claim lacks numeric substantiation (e.g., % improvement, specific metrics)",
        "upgrade": "Vague claim lacks numeric substantiation (e.g., version numbers, specific changes)",
        "better": "Vague comparison lacks numeric substantiation (e.g., measurements, benchmarks)",
        "faster": "Vague performance claim lacks numeric substantiation (e.g., ms, throughput)",
        "user experience": "Vague UX claim lacks numeric substantiation (e.g., user metrics, A/B test results)",
        "significantly": "Vague amplifier lacks numeric substantiation",
        "greatly": "Vague amplifier lacks numeric substantiation",
        "substantially": "Vague amplifier lacks numeric substantiation",
    }

    # Maximum score for this component (25% weight in total risk score)
    MAX_SCORE = 25

    # Patterns that indicate numeric substantiation
    NUMERIC_PATTERNS = [
        r'\d+%',  # Percentages: 25%, 40%
        r'\d+\s*(ms|milliseconds|seconds|s|minutes|min)',  # Time: 40ms, 2 seconds
        r'\d+\s*(kb|mb|gb|bytes)',  # Size: 500kb, 2mb
        r'\d+\s*(req/s|requests per second|qps)',  # Throughput: 1000 req/s
        r'from\s+\d+\s+to\s+\d+',  # Range: from 100 to 150
        r'\d+x',  # Multiplier: 2x faster
        r'\d+\.\d+',  # Decimals: 1.5, 2.3
    ]

    def analyze(self, narrative: str) -> AnalysisResult:
        """Analyze narrative for vague language without substantiation.

        Args:
            narrative: R&D narrative text to analyze

        Returns:
            Analysis result with score (0-25) and list of detections
        """
        narrative_lower = narrative.lower()
        detections: list[Detection] = []

        # Detect each vague phrase
        for phrase, reason in self.VAGUE_PHRASES.items():
            if phrase in narrative_lower:
                detections.append({"phrase": phrase, "reason": reason})

        # Check for numeric substantiation
        has_substantiation = self._has_numeric_substantiation(narrative)

        # Calculate score based on vagueness and substantiation
        score = self._calculate_score(detections, has_substantiation)

        return {"score": score, "detections": detections}

    def _has_numeric_substantiation(self, narrative: str) -> bool:
        """Check if narrative contains numeric substantiation.

        Args:
            narrative: R&D narrative text to check

        Returns:
            True if narrative contains numbers/metrics, False otherwise
        """
        for pattern in self.NUMERIC_PATTERNS:
            if re.search(pattern, narrative, re.IGNORECASE):
                return True
        return False

    def _calculate_score(self, detections: list[Detection], has_substantiation: bool) -> int:
        """Calculate risk score based on detections and substantiation.

        Args:
            detections: List of vague phrase detections
            has_substantiation: Whether narrative has numeric substantiation

        Returns:
            Risk score between 0 and MAX_SCORE (25)
        """
        if not detections:
            return 0

        # Base score: each unique detection adds points
        # Fewer detections need higher penalty to ensure vague claims score high
        # 2-3 detections without substantiation should score >15
        base_score = len(detections) * 8

        # Reduce score if numeric substantiation is present
        if has_substantiation:
            # With substantiation, reduce penalty by 60%
            base_score = int(base_score * 0.4)

        # Cap at maximum score
        return min(base_score, self.MAX_SCORE)
