"""Business risk detector for IRS Section 41 R&D narratives.

Detects business-focused language that indicates business risk rather than
technical risk/uncertainty. IRS Section 41 requires focus on technical
uncertainty, not business objectives.

Interface: detect(text: str) -> tuple[int, int]
- penalty: 0-20 points (higher = more business risk detected)
- count: number of business risk patterns detected
"""

from __future__ import annotations

import re


class BusinessRiskDetector:
    """Detects business risk language in narratives.

    Implements detect(text: str) -> tuple[int, int] interface for modular
    detector architecture.
    """

    # Business risk patterns (should focus on technical risk instead)
    BUSINESS_PATTERNS: list[tuple[str, str]] = [
        (r"\bmarket\s+share\b", "market share focus"),
        (r"\brevenue\b", "revenue focus"),
        (r"\bprofit(?:s|ability)?\b", "profit focus"),
        (r"\bcustomer\s+satisfaction\b", "customer satisfaction"),
        (r"\bcompetitive\s+position(?:ing)?\b", "competitive positioning"),
        (r"\bsales\s+(?:growth|target)\b", "sales targets"),
        (r"\bbusiness\s+(?:growth|objectives?)\b", "business objectives"),
        (r"\bmarket\s+segments?\b", "market segments"),
        (r"\bstay\s+competitive\b", "competitive pressure"),
    ]

    def detect(self, text: str) -> tuple[int, int]:
        """Detect business risk language in narrative text.

        Checks for business-focused language that indicates business risk
        rather than technical uncertainty. IRS Section 41 requires narratives
        to focus on technical challenges, not business objectives.

        Args:
            text: Narrative text to analyze (case-insensitive)

        Returns:
            tuple[int, int]: (penalty, count)
                - penalty: 0-20 points (5 points per pattern, max 20)
                - count: number of business risk patterns detected
        """
        # Handle edge cases
        stripped = text.strip()
        if not stripped:
            return (0, 0)

        penalty = 0
        count = 0
        text_lower = text.lower()

        for pattern, _ in self.BUSINESS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                penalty += 5
                count += 1

        # Cap penalty at 20 points
        return (min(20, penalty), count)
