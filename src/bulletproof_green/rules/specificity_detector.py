"""Specificity detector for IRS Section 41 R&D narratives (STORY-032).

Detects specific metrics, timestamps, error codes, and failure citations.
Resists gaming attempts like metric stuffing and superficial metric listing.

Interface: detect(text: str) -> tuple[int, float]
- penalty: 0-10 points (higher = less specific)
- score: 0.0-1.0 (higher = more specific)
"""

from __future__ import annotations

import re


class SpecificityDetector:
    """Detects specificity in narratives through metrics, dates, and measurements.

    Implements detect(text: str) -> tuple[int, float] interface for modular
    detector architecture (STORY-032, STORY-040-045).
    """

    # Metrics pattern: numbers with units (ms, %, GB, req/s, etc.)
    # Note: No trailing \b after % to match "95%" correctly
    METRIC_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?(?:\s*(?:ms|s|seconds?|minutes?|hours?|%|GB|MB|KB|req/s|requests?))",
        re.IGNORECASE,
    )

    # Date/timestamp pattern (YYYY-MM-DD, MM/DD/YYYY, etc.)
    DATE_PATTERN = re.compile(
        r"\b\d{4}[-/]\d{2}[-/]\d{2}\b|" r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", re.IGNORECASE
    )

    # Error code pattern (ERROR-XXX, ERR-XXX, E-XXX, etc.)
    ERROR_CODE_PATTERN = re.compile(r"\b(?:ERROR|ERR|E)-\d+\b", re.IGNORECASE)

    # Bare numbers (for fallback detection when units are missing)
    BARE_NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b")

    # Experimentation keywords (to detect context for metrics)
    EXPERIMENTATION_KEYWORDS = [
        r"\bhypothes",
        r"\bexperiment",
        r"\bfail",
        r"\biterat",
        r"\btest",
        r"\battempt",
        r"\btrial",
        r"\buncertain",
        r"\bobserv",
        r"\bretry",
        r"\bimprov",
        r"\breduc",
        r"\bfinal",
    ]

    def detect(self, text: str) -> tuple[int, float]:
        """Detect specificity in narrative text.

        Checks for:
        - Quantitative metrics with units (45ms, 95%, 1000 req/s)
        - Timestamps and dates (2024-01-15)
        - Error codes (ERROR-503)
        - Failure citations with specific data
        - Context (experimentation narrative vs. metric stuffing)

        Args:
            text: Narrative text to analyze

        Returns:
            tuple[int, float]: (penalty, specificity_score)
                - penalty: 0-10 points (0 = highly specific, 10 = vague)
                - specificity_score: 0.0-1.0 (normalized specificity level)
        """
        # Handle edge cases
        stripped = text.strip()
        if not stripped:
            return (10, 0.0)

        # Count specificity indicators
        metrics = self.METRIC_PATTERN.findall(text)
        dates = self.DATE_PATTERN.findall(text)
        error_codes = self.ERROR_CODE_PATTERN.findall(text)
        bare_numbers = self.BARE_NUMBER_PATTERN.findall(text)

        # Total specificity indicators
        total_indicators = len(metrics) + len(dates) + len(error_codes)

        # Check for experimentation context (use regex for word boundaries)
        text_lower = text.lower()
        exp_evidence = sum(
            1 for pattern in self.EXPERIMENTATION_KEYWORDS if re.search(pattern, text_lower)
        )

        # Detect metric stuffing (STORY-032 adversarial gaming)
        word_count = len(text.split())
        metric_density = (len(metrics) / max(1, word_count)) * 100

        # Detect repeated metrics (e.g., "95% 95% 95%")
        # Allow some repetition (like "from 120ms to 45ms"), but flag excessive
        unique_metrics = set(metrics)
        if len(metrics) > 0:
            repetition_ratio = len(metrics) / len(unique_metrics)
            has_metric_repetition = repetition_ratio >= 2.5  # e.g., 3 metrics, only 1 unique
        else:
            has_metric_repetition = False

        # Gaming detection rules:
        # 1. Metric repetition (same metric repeated 2.5+ times)
        # 2. High density (>30%) with no/weak exp evidence
        # 3. Very high density (>50%) regardless of evidence
        is_metric_stuffing = (
            has_metric_repetition
            or (metric_density > 30 and exp_evidence <= 1)
            or (metric_density > 50)
        )

        # Calculate base specificity score (0.0-1.0)
        # Good narratives have 3+ specific indicators
        base_score = min(1.0, total_indicators / 3.0)

        # Adjust for bare numbers (some specificity even without units)
        if total_indicators < 3 and len(bare_numbers) >= 2:
            base_score = min(1.0, base_score + (len(bare_numbers) * 0.15))

        # Penalize metric stuffing (reduce score for gaming attempts)
        if is_metric_stuffing:
            specificity_score = max(0.0, base_score * 0.4)  # Reduce score by 60%
        else:
            specificity_score = base_score

        # Calculate penalty (inverse of score)
        # 3+ indicators with context: 0 penalty
        # 2 indicators: 0 penalty (sufficient specificity)
        # 1 indicator: 3-5 penalty based on context
        # 0 indicators: 10 penalty
        # Metric stuffing: higher penalty despite metrics
        if is_metric_stuffing:
            penalty = 15  # Penalize gaming heavily
        elif total_indicators >= 3:
            penalty = 0  # High specificity
        elif total_indicators == 2:
            # 2 indicators = reasonable specificity
            penalty = 0
        elif total_indicators == 1:
            # 1 indicator = moderate specificity
            # Error codes and other single indicators acceptable with context
            if exp_evidence >= 2:
                penalty = 0  # Good context (e.g., "experiment failed with ERROR-503, retry...")
            elif exp_evidence >= 1:
                penalty = 3  # Some context
            else:
                penalty = 5  # Standalone metric
        else:
            # Check if bare numbers provide some specificity
            if len(bare_numbers) >= 3:
                penalty = 5  # Some numbers present
            else:
                penalty = 10  # No specificity at all

        return (penalty, specificity_score)
